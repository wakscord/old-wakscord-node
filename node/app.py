import logging

from aiohttp import web

from .modules.env import ID, KEY, OWNER
from .modules.message import Message
from .modules.task_manager import TaskManager

logger = logging.getLogger("app")


class WakscordNode(web.Application):
    """Represents a wakscord node using Application in aiohttp.web

    The following are the functions used by the router.

    - route_index
    - route_request
    - route_get_deleted_webhooks
    - route_delete_deleted_webhooks

    All requests will go through this class and will forward the action.
    """

    def __init__(self):
        super().__init__()

        self.task_manager = TaskManager(deleted_hook=self.deleted_hook)
        self.deleted_webhooks = []

    async def route_index(self, _: web.Request) -> web.Response:
        return web.json_response(
            {
                "info": {
                    "node_id": ID,
                    "owner": OWNER,
                },
                "pending": {
                    "total": self.task_manager.message_size
                    + self.task_manager.task_size,
                    "messages": self.task_manager.message_size,
                    "tasks": self.task_manager.task_size,
                },
                "processed": self.task_manager.processed,
                "deleted": len(self.deleted_webhooks),
            }
        )

    async def route_request(self, request: web.Request) -> web.Response:
        if request.headers.get("Authorization") != f"Bearer {KEY}":
            return web.json_response(
                {"status": "error", "message": "Invalid key"},
                status=401,
            )

        data = await request.json()
        keys = data["keys"]

        for key in data["keys"]:
            if key in self.deleted_webhooks:
                keys.remove(key)

        data["keys"] = keys

        message = Message(data)

        await self.task_manager.add_message(message)

        return web.json_response({"status": "ok"})

    async def route_get_deleted_webhooks(self, _: web.Request) -> web.Response:
        return web.json_response(self.deleted_webhooks)

    async def route_delete_deleted_webhooks(self, _: web.Request) -> web.Response:
        self.deleted_webhooks = []

        return web.json_response({"status": "ok"})

    async def request_loop(self):
        logger.info("Request loop started")

        while True:
            await self.task_manager.process()

    def deleted_hook(self, key: str):
        if key not in self.deleted_webhooks:
            self.deleted_webhooks.append(key)

    def setup_routers(self):
        self.router.add_get("/", self.route_index)
        self.router.add_post("/request", self.route_request)
        self.router.add_get("/deletedWebhooks", self.route_get_deleted_webhooks)
        self.router.add_delete("/deletedWebhooks", self.route_delete_deleted_webhooks)
