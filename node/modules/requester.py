import asyncio
from typing import Callable

import aiohttp


class Requester:
    def __init__(self, keys: list[str], data: str, deleted_hook: Callable):
        self.keys = keys
        self.data = data
        self.deleted_hook = deleted_hook

        self.session: aiohttp.ClientSession = None

    async def request(self):
        self.session = aiohttp.ClientSession()

        actions = [self.__request(key) for key in self.keys]

        await asyncio.gather(*actions)

    async def __request(
        self,
        key: str,
        retry: int = 0,
    ):
        if retry > 12:
            return

        if retry:
            await asyncio.sleep(retry * 10)

        async with self.session.post(
            f"https://discord.com/api/webhooks/{key}",
            data=self.data,
            headers={"Content-Type": "application/json"},
        ) as response:
            if response.status == 429:
                asyncio.create_task()
