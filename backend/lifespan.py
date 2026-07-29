from __future__ import annotations

from backend.config import config
from backend.constants import VERSION
from backend.environment import Environment, get_environment
from backend.log_config import setup_logging
from backend.shutdown import shutdown_handler
from backend.startup import startup_handler


async def lifespan(app):
    env = get_environment()
    log = setup_logging(config.logging)

    if env == Environment.PRODUCTION:
        log.info(f"Starting SuperDev AI Suite in production mode [version={VERSION}]")
    else:
        log.info(
            f"Starting SuperDev AI Suite [version={VERSION}, environment={env.value}]"
        )

    await startup_handler()

    yield

    await shutdown_handler()
    log.info("SuperDev AI Suite shutdown complete")