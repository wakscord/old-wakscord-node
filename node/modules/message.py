from .utils import list_chunk


class Message:
    def __init__(self, data):
        self.data = data["data"]
        self.keys = data["keys"]

    def get(self, chunk: int) -> list[str]:
        return [[key for key in lst] for lst in list_chunk(self.keys, chunk)]
