from __future__ import annotations

from backend.config import config
from backend.constants import PROJECT_NAME, VERSION
from backend.environment import Environment, get_environment
from backend.logging import setup_logging
from backend.registry import service_registry
from backend.startup import startup_handler
from backend.shutdown import shutdown_handler


async def lifespan(app):
    env = get_environment()
    log = setup_logging(config.logging)

    if env == Environment.PRODUCTION:
        log.info("Starting SuperDev AI Suite in production mode", version=VERSION)
    else:
        log.info(
            "Starting SuperDev AI Suite",
            version=VERSION,
            environment=env.value,
        )

    await startup_handler()

    yield

    await shutdown_handler()
    log.info("SuperDev AI Suite shutdown complete")