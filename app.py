import datetime
from typing import List, Dict

import os
import sys
import json

import asyncio
import traceback
import aiohttp
from aiohttp import web
from requester import MultiRequester
from log_handler import CustomHandler
from errors import NodeException

__version__ = "0.0.1"
logger = CustomHandler.development(__name__)


class NodeServer(web.Application):
    def __init__(self):
        super().__init__()
        self.requester: MultiRequester = MultiRequester()
        self.metadata: Dict[str, str] = json.load(open(".config/metadata.json"))

    async def node_info_json(self, _request: web.Request) -> web.Response:
        __exception_staticmethod_error = self

        return web.json_response(
            data={
                "version": str(__version__),
                "name": self.metadata["name"],
                "description": self.metadata.get("description", ""),
                "owner": self.metadata.get("owner", "anonymous"),
                "platform": sys.platform,
                "library": {
                    "aiohttp": str(aiohttp.__version__),
                    "python": str(sys.version),
                },
                "queue": self.requester.queue.qsize,
            }
        )

    async def node_info_html(self, _request: web.Request) -> web.Response:
        __exception_staticmethod_error = self

        return web.Response(
            text="<h1>Wakscord Node</h1>\n"
            f"<h2>{self.metadata['name']}</h3>\n"
            f"<p>{self.metadata.get('description')}</p>\n"
            f"<p>node owner: {self.metadata.get('owner', '')}",
            content_type="text/html",
        )

    async def log_viewer(self, request: web.Request) -> web.FileResponse:
        __exception_staticmethod_error = self

        if request.headers.get("X-Wakscord-Key") != os.getenv("ACCESS_KEY"):
            raise web.HTTPUnauthorized(
                body=json.dumps({"required": {"headers": "X-Wakscord-Key"}}),
                reason="X-Wakscord-Key header is empty or key value is different",
            )

        file_name = request.match_info["file_name"]
        if file_name in ("/" or ".." or "."):
            raise web.HTTPBadRequest(
                body=json.dumps({}),
                reason="The file name cannot contain path separator characters",
            )
        return web.FileResponse(path=f"logs/{file_name}.txt")

    async def make_request(self, request: web.Request) -> web.Response:
        if request.headers.get("X-Wakscord-Key") != os.getenv("ACCESS_KEY"):
            raise web.HTTPUnauthorized(
                body=json.dumps({"required": {"headers": "X-Wakscord-Key"}}),
                reason="X-Wakscord-Key header is empty or key value is different",
            )

        data = await request.json()

        if not data.get("keys") or not data.get("data"):
            required_data = []
            if not data.get("keys"):
                required_data.append("keys")
            if not data.get("data"):
                required_data.append("data")

            raise web.HTTPBadRequest(
                body=json.dumps({"required": {"body": required_data}}),
                reason="There are necessary arguments in the body part",
            )
        webhook_tokens: List[str] = data["keys"]
        webhook_body_data: dict = data["data"]

        request_urls = [
            f"https://discord.com/api/webhooks/{token}" for token in webhook_tokens
        ]
        task_id = await self.requester.put_actions(
            urls=request_urls, data=webhook_body_data
        )
        return web.json_response(data={"task_id": task_id})

    async def get_task(self, request: web.Request) -> web.Response:
        if request.headers.get("X-Wakscord-Key") != os.getenv("ACCESS_KEY"):
            raise web.HTTPUnauthorized(
                body=json.dumps({"required": {"headers": "X-Wakscord-Key"}}),
                reason="X-Wakscord-Key header is empty or key value is different",
            )

        task_id = request.match_info["task_id"]
        if not self.requester.queue.internal_queue.get(task_id):
            raise web.HTTPNotFound(
                body=json.dumps({}), reason="Session not found or does not exist."
            )

        export_json = await self.requester.queue.export_json(task_id)
        return web.json_response(data=export_json)

    async def delete_task(self, request: web.Request) -> web.Response:
        if request.headers.get("X-Wakscord-Key") != os.getenv("ACCESS_KEY"):
            raise web.HTTPUnauthorized(
                body=json.dumps({"required": {"headers": "X-Wakscord-Key"}}),
                reason="X-Wakscord-Key header is empty or key value is different",
            )

        task_id = request.match_info["task_id"]
        if not self.requester.queue.internal_queue.get(task_id):
            raise web.HTTPNotFound(
                body=json.dumps({}), reason="Session not found or does not exist."
            )

        await self.requester.queue.delete(task_id)
        return web.Response(text="")

    async def stop_task(self, request: web.Request) -> web.Response:
        if request.headers.get("X-Wakscord-Key") != os.getenv("ACCESS_KEY"):
            raise web.HTTPUnauthorized(
                body=json.dumps({"required": {"headers": "X-Wakscord-Key"}}),
                reason="X-Wakscord-Key header is empty or key value is different",
            )

        task_id = request.match_info["task_id"]
        if not self.requester.queue.internal_queue.get(task_id):
            raise web.HTTPNotFound(
                body=json.dumps({}), reason="Session not found or does not exist."
            )

        await self.requester.queue.stop(task_id)
        return web.Response(text="")

    async def requester_loop(self):
        logger.info("Requester loop started running.")
        while True:
            await asyncio.sleep(1)

            try:
                asyncio.create_task(self.requester.process())
            except NodeException as _e:
                logger.error(
                    "An error occurred while executing the actions.\n%s",
                    traceback.format_exc(),
                )

            for task_id, data in self.requester.queue.internal_queue.items():
                data["created_at"]: datetime.datetime

                timedelta: datetime.timedelta = (
                    datetime.datetime.now() - data["created_at"]
                )
                if timedelta.seconds > int(os.getenv("CACHE_CLEANUP_SECOND", 30)):
                    await self.requester.queue.delete(task_id)

    def setup_routers(self) -> None:
        self.router.add_get("/", self.node_info_json, name="node-info-json")
        self.router.add_get("/node-info", self.node_info_html, name="node-info-html")
        self.router.add_get("/log/{file_name}", self.log_viewer, name="log-viewer")
        self.router.add_post("/request", self.make_request, name="make-request")
        self.router.add_get("/task/{task_id}", self.get_task, name="get-task")
        self.router.add_delete("/task/{task_id}", self.delete_task, name="delete-task")
        self.router.add_post("/task/{task_id}/stop", self.stop_task, name="stop-task")
