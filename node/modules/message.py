from typing import Any

from .utils import list_chunk


class Message:
    """Represents wrapping wakscord message data."""

    def __init__(self, data):
        self.data = data["data"]
        self.keys = data["keys"]
        self.proxies = data["proxies"]

    def get(self, chunk: int) -> list[list[Any]]:
        return list_chunk(self.keys, chunk)
