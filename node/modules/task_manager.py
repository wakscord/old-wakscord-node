import asyncio

from .requester import Requester


class TaskManager:
    def __init__(self):
        self._queue = asyncio.Queue()
        self.requester = Requester()

    @property
    def size(self):
        return self._queue.qsize()

    async def process(self):
        message = await self._queue.get()
