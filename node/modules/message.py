from typing import Any

from utils import list_chunk


class Message:
    """Represents wrapping wakscord message data."""

    def __init__(self, data):
        self.data = data["data"]
        self.keys = data["keys"]

    def get(self, chunk: int) -> list[list[Any]]:
        # pylint: disable=line-too-long
        return [list(key for key in lst) for lst in list_chunk(self.keys, chunk)]
