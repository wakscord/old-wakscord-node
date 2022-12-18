import platform
import asyncio
import logging
import os

from aiohttp import web
from dotenv import load_dotenv

from app import NodeServer, __version__
from log_handler import CustomHandler

load_dotenv(dotenv_path=".config/.env")
logger = CustomHandler.development("main")


def main():
    app = NodeServer()

    app.setup_routers()
    logging.basicConfig(level=logging.DEBUG)
    print(
        """\033[1;32;40m
__          __     _  __ _____  _____ ____  _____  _____  
\ \        / /\   | |/ // ____|/ ____/ __ \|  __ \|  __ \ 
 \ \  /\  / /  \  | ' /| (___ | |   | |  | | |__) | |  | |
  \ \/  \/ / /\ \ |  <  \___ \| |   | |  | |  _  /| |  | |
   \  /\  / ____ \| . \ ____) | |___| |__| | | \ \| |__| |
    \/  \/_/    \_\_|\_\_____/ \_____\____/|_|  \_\_____/ \033[0m"""
    )
    print(
        "\033[1;32;40m Wakscord Node is a Discord webhook decentralized transmission node. \033[0m"
    )
    print(f"\033[1;32;40m version: {__version__} \033[0m")
    print(
        f"\033[1;32;40m [metadata] name: {app.metadata['name']} | owner: {app.metadata.get('owner', 'anonymous')}\033[0m"
    )

    if platform.system() != "Windows":
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.new_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host=str(os.getenv("HOST")), port=int(os.getenv("PORT")))

    loop.run_until_complete(site.start())
    loop.create_task(app.requester_loop())
    loop.run_forever()


if __name__ == "__main__":
    main()
