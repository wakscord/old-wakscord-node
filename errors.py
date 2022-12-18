from typing import Any, Dict, Union, Type


class NodeException(Exception):
    pass


class BadRequest(NodeException):
    pass


class HTTPException(NodeException):
    def __init__(self, code: Any, message: Union[Any, Dict[str, Any]]):
        self.status = code
        if isinstance(message, dict):
            self.status = message.get("code", self.status)
            self.error = message.get("message", "NodeException")
        else:
            self.error = message
        super().__init__(f"{self.status} {self.error}")


class Forbidden(HTTPException):
    pass


class WebhookDeletedError(HTTPException):
    pass


class DiscordServerError(HTTPException):
    pass


class BannedByCloudflareError(HTTPException):
    pass


ERROR_MAPPING: Dict[str, int] = {
    'NodeException': 2022,
    'HTTPException': 2023,
    'Forbidden': 2024,
    'DiscordServerError': 2025,
    'BannedByCloudflareError': 2026,
    'BadRequest': 2027,
    'WebhookDeletedError': 2028,
}
