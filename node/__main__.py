# Reference
import asyncio
import logging

from aiohttp import web

from .app import WakscordNode
from .modules import env


def main():
    logging.basicConfig(
        format="[%(name)s] (%(asctime)s) %(levelname)s: %(message)s",
        datefmt="%y/%m/%d %p %I:%M:%S",
        level=logging.INFO,
    )

    logger = logging.getLogger("starter")
    app = WakscordNode()

    app.setup_routers()

    logger.info("Starting Wakscord Node on %s:%i", env.HOST, env.PORT)

    logger.info("Node ID: %s", env.ID)
    logger.info("Node Owner: %s", env.OWNER)
    logger.info("MAX_CONCURRENT: %i", env.MAX_CONCURRENT)
    logger.info("WAIT_CONCURRENT: %i", env.WAIT_CONCURRENT)

    uvloop = None

    try:
        import uvloop  # pylint: disable=import-outside-toplevel
    except ImportError:
        logger.warning("uvloop not installed, using asyncio")

    if uvloop:
        logger.info("Using uvloop")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    loop = asyncio.get_event_loop()
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())

    site = web.TCPSite(runner, host=env.HOST, port=env.PORT)

    loop.run_until_complete(site.start())
    loop.create_task(app.request_loop())
    loop.run_forever()


if __name__ == "__main__":
    main()
