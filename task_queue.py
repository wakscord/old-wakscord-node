import asyncio
import datetime

from typing import Dict, Any, List, Coroutine, Optional, Tuple
from collections import OrderedDict

STATUS_MAPPING: Dict[str, int] = {
    "pending": 0,
    "stopped": 1,
    "finished": 2,
}


class TaskQueue:
    def __init__(self) -> None:
        self.internal_queue: OrderedDict = OrderedDict()

    def empty(self) -> bool:
        if len(self.internal_queue.items()) > 0:
            return False
        return True

    @property
    def qsize(self) -> int:
        queue_size = 0
        for _, data in self.internal_queue.items():
            queue_size += len(data["response"]["pending"])

        return queue_size

    def pending(self, task_id: str) -> bool:
        return self.internal_queue[task_id]["status"] == "pending"

    def stopped(self, task_id: str) -> bool:
        return self.internal_queue[task_id]["status"] == "stopped"

    def deleted(self, task_id: str) -> bool:
        if not self.internal_queue.get(task_id) is None:
            return False
        return True

    async def delete(self, task_id: str) -> None:
        del self.internal_queue[task_id]

    async def action_get(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        try:
            first_serve_task_id = next(
                iter(
                    {
                        task_id: data
                        for task_id, data in self.internal_queue.items()
                        if data["status"] == "pending"
                    }
                )
            )
            first_serve = self.internal_queue[first_serve_task_id]
        except KeyError:
            return

        return first_serve_task_id, first_serve

    async def set_success(self, task_id: str, webhook_token: str) -> None:
        self.internal_queue[task_id]["response"]["pending"].remove(webhook_token)
        self.internal_queue[task_id]["response"]["success"].append(webhook_token)

    async def set_error(
        self, task_id: str, webhook_token: str, data: Dict[str, Any]
    ) -> None:
        self.internal_queue[task_id]["response"]["pending"].remove(webhook_token)
        self.internal_queue[task_id]["response"]["error"].append(
            {
                "token": webhook_token,
                "data": data,
            }
        )

    async def all_pending(self, task_id: str, /) -> None:
        self.internal_queue[task_id]["response"]["pending"] = self.internal_queue[
            task_id
        ]["urls"]

    async def finish(self, task_id: str, /) -> None:
        self.internal_queue[task_id]["status"] = "finished"

    async def stop(self, task_id: str, /) -> None:
        self.internal_queue[task_id]["status"] = "stopped"

    async def export_json(self, task_id: str, /) -> Dict[str, Any]:
        print(self.internal_queue[task_id]["status"])
        return {
            "total_size": len(self.internal_queue[task_id]["urls"]),
            "status": STATUS_MAPPING.get(self.internal_queue[task_id]["status"]),
            "data": self.internal_queue[task_id]["data"],
            "queue": {
                "pending": self.internal_queue[task_id]["response"]["pending"],
                "success": self.internal_queue[task_id]["response"]["success"],
                "error": self.internal_queue[task_id]["response"]["error"],
            },
        }

    async def put(
        self,
        task_id: str,
        actions: List[Coroutine[str, dict, None]],
        urls: List[str],
        data: Dict[str, Any],
    ) -> None:
        action_queue = asyncio.Queue()
        await action_queue.put(actions)

        self.internal_queue[task_id] = {
            "actions": action_queue,
            "status": "pending",
            "urls": urls,
            "data": data,
            "response": {
                "pending": [],
                "success": [],
                "error": [],
            },
            "created_at": datetime.datetime.now(),
        }
