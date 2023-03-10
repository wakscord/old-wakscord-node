import os

KEY = os.getenv("KEY", "wakscord")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 3000)

IDX = os.getenv("IDX", 1)
OWNER = os.getenv("OWNER", "?")

MAX_CONCURRENT = os.getenv("MAX_CONCURRENT", 500)
WAIT_CONCURRENT = os.getenv("WAIT_CONCURRENT", 0)
