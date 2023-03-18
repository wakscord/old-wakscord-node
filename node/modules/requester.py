import asyncio
from typing import Callable

import aiohttp


class Requester:
    """Represents Discord Webhook request sender for wakscord data.
    """
    def __init__(self, keys: list[str], data: str, deleted_hook: Callable):
        self.keys = keys
        self.data = data
        self.deleted_hook = deleted_hook

        self.session: aiohttp.ClientSession = None

    async def request(self):
        self.session = aiohttp.ClientSession()

        actions = [self.__request(key) for key in self.keys]

        await asyncio.gather(*actions)
        await self.session.close()

    async def __request(
        self,
        key: str,
        retry: int = 0,
    ):
        if retry > 12:
            return

        if retry:
            await asyncio.sleep(retry * 10)
            session = aiohttp.ClientSession()
        else:
            session = self.session

        async with session.post(
            f"https://discord.com/api/webhooks/{key}",
            data=self.data,
            headers={"Content-Type": "application/json"},
        ) as response:
            if response.status == 404:
                return self.deleted_hook(key)

            if response.status == 429:
                asyncio.create_task(
                    self.__request(
                        key,
                        retry=retry + 1,
                    )
                )

        if retry:
            await session.close()
