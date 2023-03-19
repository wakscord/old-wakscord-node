import os

from .utils import to_int

KEY = os.getenv("KEY", "wakscord")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = to_int(os.getenv("PORT"), 3000)

ID = to_int(os.getenv("ID"), 1)
OWNER = os.getenv("OWNER", "Unknown")

MAX_CONCURRENT = to_int(os.getenv("MAX_CONCURRENT"), 500)
WAIT_CONCURRENT = to_int(os.getenv("WAIT_CONCURRENT"), 0)
