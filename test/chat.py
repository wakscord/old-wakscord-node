import os

import aiohttp
import asyncio
from dotenv import load_dotenv
from tokens.tpk1 import tokens as tpk1_token
from tokens.tpk2 import tokens as tpk2_token
from tokens.tpk3 import tokens as tpk3_token
from tokens.deleted import tokens as tpk_deleted_token

load_dotenv(dotenv_path="../.config/.env")


WEBHOOKS = tpk1_token + tpk2_token + tpk3_token + tpk_deleted_token


async def main():
    session = aiohttp.ClientSession(headers={"X-Wakscord-Key": "WAKSCORD_KEY"})
    while True:
        text = input("enter chat: ")
        data = await session.post(
            "http://localhost/request",
            json={"keys": WEBHOOKS, "data": {"content": text}},
        )
        json_data = await data.json()
        print(f"successful, task_id: {json_data['task_id']}")


asyncio.run(main())
