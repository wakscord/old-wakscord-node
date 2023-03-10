import asyncio
import logging

from aiohttp import web

from .modules.env import IDX, OWNER
from .modules.task_manager import TaskManager

logger = logging.getLogger("app")


class WakscordNode(web.Application):
    def __init__(self):
        super().__init__()

        self.task_manager = TaskManager()

    async def route_index(self, request: web.Request) -> web.Response:
        return web.json_response(
            {
                "info": {
                    "node_id": IDX,
                    "owner": OWNER,
                },
                "pending": {"total": 0, "messages": 0, "tasks": 0},
                "processed": 0,
            }
        )

    async def request_loop(self):
        logger.info("Request loop started")

        while True:
            await asyncio.sleep(1)

    def setup_routers(self):
        pass
