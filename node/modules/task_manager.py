import asyncio
import json
from typing import Callable

from env import MAX_CONCURRENT, WAIT_CONCURRENT
from message import Message
from requester import Requester


class TaskManager:
    """Represents storing and managing requests for modules.requester.Request
    """
    def __init__(self, deleted_hook: Callable):
        self._deleted_hook = deleted_hook

        self.processed = 0
        self._message_queue = asyncio.Queue()
        self._task_queue = asyncio.Queue()

    @property
    def message_size(self):
        return self._message_queue.qsize()

    @property
    def task_size(self):
        return self._task_queue.qsize()

    async def add_message(self, message: Message):
        await self._message_queue.put(message)

    async def process(self):
        message: Message = await self._message_queue.get()

        data = json.dumps(message.data)
        for chunk in message.get(MAX_CONCURRENT):
            requester = Requester(chunk, data, self._deleted_hook)

            await self._task_queue.put(requester.request())

        while self._task_queue.qsize() > 0:
            task = await self._task_queue.get()

            await task

            await asyncio.sleep(WAIT_CONCURRENT)

        self.processed += len(message.keys)
