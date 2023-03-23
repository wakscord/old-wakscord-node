import logging

import asyncio
from typing import Callable, Optional, List

import aiohttp

logger = logging.getLogger("requester")


async def content_type(response):
    try:
        if response.headers.get("Content-Type") == "application/json":
            return await response.json()
    except KeyError:
        logger.warning("Cloudflare related issue occurred")
    return await response.text()


class Requester:
    """Represents Discord Webhook request sender for wakscord data."""

    def __init__(self, data: str, deleted_hook: Callable):
        self.data = data
        self.deleted_hook = deleted_hook

        self.session: Optional[aiohttp.ClientSession] = None
        self._global_limit = asyncio.Event()
        self._global_limit.set()

    def __del__(self) -> None:
        if self.session:
            if not self.session.closed:
                loop = asyncio.get_event_loop()
                loop.create_task(self.session.close())

    async def request(self, keys: List[str]):
        for key in keys:
            asyncio.create_task(self._request(key))

    async def _request(
        self,
        key: str,
        retry: int = 5,
    ):
        if not self.session:
            self.session = aiohttp.ClientSession()

        if not self._global_limit.is_set():
            await self._global_limit.wait()

        for tries in range(retry):
            try:
                async with self.session.post(
                    f"https://discord.com/api/webhooks/{key}",
                    data=self.data,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    logger.debug("Webhook (%s) returned %s", key[:35], response.status)

                    data = await content_type(response)

                    has_ratelimit_headers = "X-Ratelimit-Remaining" in response.headers
                    if has_ratelimit_headers:
                        if response.status != 429:
                            if int(response.headers["X-RateLimit-Remaining"]) == 0:
                                logger.debug(
                                    "A global rate limit bucket has been exhausted."
                                )

                    if 300 > response.status >= 200:
                        logger.debug(
                            "Message Successfully sent to Webhook (%s)", key[:35]
                        )
                        return

                    if response.status == 429:
                        if not response.headers.get("Via") or isinstance(data, str):
                            logger.critical("Banned by Cloudflare more than likely.")

                        retry_after: float = data["retry_after"]
                        logger.warning(
                            "We are being rate limited. Webhook (%s) responded with 429. Retrying in %.2f seconds.",
                            key[:35],
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
                        logger.debug(
                            "Done sleeping for the rate limit. Retrying... (%s)",
                            key[:35],
                        )

                        if is_global:
                            self._global_limit.set()
                            logger.debug("Global rate limit is now over.")

                        continue

                    # we've received a 500, 502, 504, or 524, unconditional retry
                    if response.status in {500, 502, 504, 524}:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    if response.status in {401, 404, 403}:
                        logger.debug(
                            "This webhook (%s) has been deleted or cannot be found.",
                            key[:35],
                        )
                        return self.deleted_hook(key)

                    # Discord Server Error
                    if response.status >= 500:
                        logger.critical("Discord Server Error")
                        await asyncio.sleep(retry * 10)
                    else:
                        logger.error(
                            "HTTP Error in Webhook (%s) - %s", key[:35], response.status
                        )

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
                    logger.critical("Discord Server Error")
                    await asyncio.sleep(retry * 10)

                logger.error(
                    "HTTP Error in Webhook (%s) - %s", key[:35], response.status
                )

            raise RuntimeError("Unreachable code in HTTP handling")
