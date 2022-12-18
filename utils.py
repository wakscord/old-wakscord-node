import os
import base64


def generate_unique_code() -> str:
    return base64.b32encode(os.urandom(3))[:5].decode("utf-8")
