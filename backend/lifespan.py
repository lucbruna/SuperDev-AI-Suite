"""FastAPI lifespan context manager.

Wraps the entire startup sequence in try/except so that failures in optional
dependencies or external services do not prevent uvicorn from starting and
listening on the configured port.
"""

from __future__ import annotations

import asyncio

from backend.config import config
from backend.constants import VERSION
from backend.environment import Environment, get_environment
from backend.log_config import setup_logging
from backend.shutdown import shutdown_handler
from backend.signal_handlers import register_signal_handlers
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

    # Register signal handlers for graceful shutdown
    register_signal_handlers(timeout=30)

    if env == Environment.PRODUCTION:
        log.info(f"Starting SuperDev AI Suite in production mode [version={VERSION}]")
    else:
        log.info(f"Starting SuperDev AI Suite [version={VERSION}, environment={env.value}]")

    try:
        await startup_handler()
    except Exception as exc:
        log.warning(
            "Startup completed with errors — app is running in degraded mode: %s",
            exc,
        )

    yield

    # Graceful shutdown with timeout watchdog
    shutdown_task = asyncio.create_task(_safe_shutdown(log))
    try:
        await asyncio.wait_for(shutdown_task, timeout=30.0)
    except TimeoutError:
        log.warning("Shutdown timed out after 30s — forcing exit")
        import os

        os._exit(1)  # noqa: SLF001

    log.info("SuperDev AI Suite shutdown complete")


async def _safe_shutdown(log) -> None:
    """Run shutdown handler safely."""
    try:
        await shutdown_handler()
    except Exception as exc:
        log.warning("Shutdown handler raised: %s", exc)
