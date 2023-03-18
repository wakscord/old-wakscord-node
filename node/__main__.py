import asyncio
import logging

from aiohttp import web

from .app import WakscordNode
from .modules.env import *


def main():
    logging.basicConfig(
        format="[%(name)s] (%(asctime)s) %(levelname)s: %(message)s",
        datefmt="%y/%m/%d %p %I:%M:%S",
        level=logging.INFO,
    )

    logger = logging.getLogger("starter")
    app = WakscordNode()

    app.setup_routers()

    logger.info(f"Starting Wakscord Node on {HOST}:{PORT}")

    logger.info(f"Node ID: {IDX}")
    logger.info(f"Node Owner: {OWNER}")
    logger.info(f"MAX_CONCURRENT: {MAX_CONCURRENT}")
    logger.info(f"WAIT_CONCURRENT: {WAIT_CONCURRENT}")

    uvloop = None

    try:
        import uvloop  # type: ignore
    except ImportError:
        logger.warning("uvloop not installed, using asyncio")

    if uvloop:
        logger.info("Using uvloop")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner, host=HOST, port=PORT)

    loop.run_until_complete(site.start())
    loop.create_task(app.request_loop())
    loop.run_forever()


if __name__ == "__main__":
    main()
