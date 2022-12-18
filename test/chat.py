import os

import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv(dotenv_path=".config/.env")


WEBHOOKS = ["WEBHOOKS"]


async def main():
    session = aiohttp.ClientSession(headers={"X-Wakscord-Key": os.getenv("ACCESS_KEY")})
    while True:
        text = input("enter chat: ")
        data = await session.post(
            "http://localhost/request",
            json={"keys": WEBHOOKS, "data": {"content": text}},
        )
        json_data = await data.json()
        print(f"successful, task_id: {json_data['task_id']}")


asyncio.run(main())
