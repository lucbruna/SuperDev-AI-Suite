from __future__ import annotations

import logging

from backend.config import config
from backend.health import HealthChecker
from backend.registry import service_registry

logger = logging.getLogger("superdev")


async def startup_handler() -> None:
    logger.info("Running startup initialization")

    logger.info("Loading configuration", extra={"environment": config.app.environment})
    logger.info("Checking database connection")
    try:
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(config.database.url, pool_size=1, echo=False)
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        await engine.dispose()
        logger.info("Database connection verified")
    except Exception as e:
        logger.error("Database connection failed", extra={"error": str(e)})
        raise

    logger.info("Running database migrations")
    try:
        from alembic.config import Config as AlembicConfig

        from alembic import command

        alembic_cfg = AlembicConfig(config.database.migration_dir)
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations complete")
    except Exception as e:
        logger.warning("Migrations skipped or failed", extra={"error": str(e)})

    logger.info("Initializing cache")
    try:
        from redis.asyncio import from_url

        redis = await from_url(
            config.redis.url,
            decode_responses=config.redis.decode_responses,
            socket_connect_timeout=config.redis.socket_connect_timeout,
        )
        await redis.ping()
        service_registry.register("redis", redis)
        logger.info("Cache initialized")
    except Exception as e:
        logger.warning("Cache initialization failed", extra={"error": str(e)})

    logger.info("Registering default data")
    service_registry.register("config", config)
    service_registry.register("started_at", __import__("datetime").datetime.utcnow().isoformat())

    logger.info("Running health check")
    health = HealthChecker()
    results = await health.check_all()
    for name, status in results.items():
        logger.info("Health check", extra={"component": name, "status": status.status.value})

    logger.info("Startup complete")