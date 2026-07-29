"""FastAPI lifespan context manager.

Wraps the entire startup sequence in try/except so that failures in optional
dependencies or external services do not prevent uvicorn from starting and
listening on the configured port.
"""

from __future__ import annotations

import logging

from backend.config import config
from backend.constants import VERSION
from backend.environment import Environment, get_environment
from backend.log_config import setup_logging
from backend.shutdown import shutdown_handler
from backend.startup import startup_handler


async def lifespan(app):
    """Application lifespan — runs startup before yield, shutdown after.

    The startup block is wrapped in try/except. On failure:
    - A warning is logged
    - The app still starts and listens for requests
    - Health checks will report the degraded/unhealthy state
    """
    env = get_environment()
    log = setup_logging(config.logging)

    if env == Environment.PRODUCTION:
        log.info(f"Starting SuperDev AI Suite in production mode [version={VERSION}]")
    else:
        log.info(
            f"Starting SuperDev AI Suite [version={VERSION}, environment={env.value}]"
        )

    try:
        await startup_handler()
    except Exception as exc:
        log.warning(
            "Startup completed with errors — app is running in degraded mode: %s",
            exc,
        )

    yield

    try:
        await shutdown_handler()
    except Exception as exc:
        log.warning("Shutdown handler raised: %s", exc)

    log.info("SuperDev AI Suite shutdown complete")
