import asyncio
import logging
import os

from aiohttp import web
from dotenv import load_dotenv
from aiohttp_swagger import setup_swagger

from app import NodeServer, __version__
from log_handler import CustomHandler

load_dotenv(dotenv_path=".config/.env")
logger = CustomHandler.development("main", file_name="main.txt")


async def run(app: web.Application):
    web.run_app(app, host=str(os.getenv("HOST")), port=int(os.getenv("PORT")))


def main():
    app = NodeServer()

    app.setup_routers()
    if os.getenv("GENERATE_SWAGGGER_DOCS", "FALSE") is "TRUE":
        setup_swagger(
            app,
            swagger_url="/swagger-docs",
            ui_version=3,
            title="Wakscord Node API",
            description="왁스코드 노드 API 문서입니다",
            api_version=__version__,
        )
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

    loop = asyncio.new_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, host=str(os.getenv("HOST")), port=int(os.getenv("PORT")))

    loop.run_until_complete(site.start())
    loop.create_task(app.requester_loop())
    loop.run_forever()


if __name__ == "__main__":
    main()
