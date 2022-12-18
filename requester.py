import asyncio
from errors import (
    NodeException,
    HTTPException,
    Forbidden,
    DiscordServerError,
    BannedByCloudflareError,
    BadRequest,
    WebhookDeletedError,
    ERROR_MAPPING,
)
from typing import Optional, Union, Dict, Any, List

import aiohttp
import traceback

from task_queue import TaskQueue
from log_handler import CustomHandler
from utils import generate_unique_code

logger = CustomHandler.development(__name__)
deleted_webhooks_logger = CustomHandler.file_writer(
    "Deleted Webhooks Collector", file_name="deleted_webhooks.txt"
)


async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            return await response.json()
    except KeyError:
        logger.warning("Cloudflare related issue occurred")
        raise BannedByCloudflareError(
            response.status,
            "Banned by Cloudflare more than likely.",
        )

    return text


class MultiRequester:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.queue: TaskQueue = TaskQueue()
        self._global_limit = asyncio.Event()
        self._global_limit.set()

    @staticmethod
    def _list_chunk(value: list, n: int, /) -> list:
        return [value[i : i + n] for i in range(0, len(value), n)]

    async def process(self) -> None:
        if not self.queue.empty():
            task_id, actions = await self.queue.action_get()
            try:
                request_actions = await actions["actions"].get()
                chunked = self._list_chunk(request_actions, 500)
                await self.queue.all_pending(task_id)

                for each_chunk in chunked:
                    await asyncio.gather(*each_chunk)
                await self.queue.finish(task_id)
            except (StopIteration, RuntimeError):
                pass

    async def _request(
        self,
        url: str,
        json_data: dict,
        task_id: str,
        retry: Optional[int] = 5,
    ) -> None:
        try:
            await self.__request(
                url=url, json_data=json_data, task_id=task_id, retry=retry
            )
        except Exception as e:
            await self.queue.set_error(
                task_id=task_id,
                webhook_token=url,
                data={
                    "code": ERROR_MAPPING.get(
                        getattr(
                            e,
                            "error",
                            BadRequest,
                        ),
                        2027,
                    ),
                    "message": str(e),
                    "traceback": traceback.format_exc(),
                },
            )

    async def __request(
        self,
        url: str,
        json_data: dict,
        task_id: str,
        retry: Optional[int] = 5,
    ) -> None:
        if not self._session:
            self._session = aiohttp.ClientSession()

        if not self._global_limit.is_set():
            await self._global_limit.wait()

        for tries in range(retry):
            try:
                async with self._session.post(url, json=json_data) as response:
                    logger.debug(
                        "Discord with %s has returned %s", url, response.status
                    )

                    data = await json_or_text(response)

                    has_ratelimit_headers = "X-Ratelimit-Remaining" in response.headers
                    if has_ratelimit_headers:
                        if response.status != 429:
                            if int(response.headers["X-RateLimit-Remaining"]) == 0:
                                logger.debug(
                                    "A global rate limit bucket has been exhausted."
                                )

                    if 300 > response.status >= 200:
                        logger.debug("Requester with %s has received %s", url, data)
                        logger.debug("Successfully sent data with webhook %s", url)
                        await self.queue.set_success(task_id=task_id, webhook_token=url)
                        return

                    if response.status == 429:
                        if not response.headers.get("Via") or isinstance(data, str):
                            logger.critical("Banned by Cloudflare more than likely.")
                            raise BannedByCloudflareError(
                                response.status,
                                "Banned by Cloudflare more than likely.",
                            )

                        retry_after: float = data["retry_after"]
                        logger.warning(
                            "We are being rate limited. Discord with %s responded with 429. Retrying in %.2f seconds.",
                            url,
                            retry_after,
                        )

                        is_global = data.get("global", False)
                        if is_global:
                            logger.warning(
                                "Global rate limit has been hit. Retrying in %.2f seconds.",
                                retry_after,
                            )
                            self._global_limit.clear()

                        await asyncio.sleep(retry_after)
                        logger.debug("Done sleeping for the rate limit. Retrying...")

                        if is_global:
                            self._global_limit.set()
                            logger.debug("Global rate limit is now over.")

                        continue

                    # we've received a 500, 502, 504, or 524, unconditional retry
                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # we've received a 401 or 404, webhook deleted
                    if response.status in {401, 404}:
                        logger.error(
                            "This webhook (%s) has been deleted or cannot be found.",
                            url,
                        )
                        deleted_webhooks_logger.info(url)
                        raise WebhookDeletedError(
                            code=404,
                            message=f"This webhook ({url}) has been deleted or cannot be found.",
                        )

                    if response.status == 403:
                        raise Forbidden(response.status, data)
                    elif response.status >= 500:
                        raise DiscordServerError(response.status, data)
                    else:
                        raise HTTPException(response.status, data)

            # This is handling exceptions from the request
            except OSError as e:
                # Connection reset by peer
                if tries < 4 and e.errno in (54, 10054):
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        if response is not None:
            # We've run out of retries, raise.
            if response.status >= 500:
                raise DiscordServerError(response.status, data)

            raise HTTPException(response.status, data)

        raise RuntimeError("Unreachable code in HTTP handling")

    async def put_actions(self, urls: List[str], data: dict) -> str:
        task_id = generate_unique_code()
        while task_id in self.queue.internal_queue.keys():
            task_id = generate_unique_code()

        actions = [
            self._request(url=url, json_data=data, task_id=task_id) for url in urls
        ]
        await self.queue.put(
            task_id=task_id,
            actions=actions,
            urls=urls,
            data=data,
        )
        return task_id
