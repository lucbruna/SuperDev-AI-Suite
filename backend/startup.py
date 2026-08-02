from __future__ import annotations

import logging
from datetime import UTC

from backend.config import config
from backend.health import HealthChecker
from backend.registry import service_registry

logger = logging.getLogger("superdev")


async def startup_handler() -> None:
    logger.info("Running startup initialization")

    logger.info("Loading configuration", extra={"environment": config.app.environment})
    logger.info("Checking database connection")
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine(config.database.url, pool_size=1, echo=False)
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        logger.info("Database connection verified")
    except Exception as e:
        logger.warning("Database connection failed — app will start without DB: %s", e)
        # Don't raise — let the app start so health checks and fallback work

    logger.info("Running database migrations")
    try:
        import asyncio
        from pathlib import Path

        from alembic.config import Config as AlembicConfig
        from alembic import command

        repo_root = Path(__file__).resolve().parent.parent
        alembic_cfg = AlembicConfig(str(repo_root / "alembic.ini"))
        alembic_cfg.set_main_option(
            "script_location",
            str((repo_root / config.database.migration_dir).resolve()),
        )
        # Run alembic in a thread — command.upgrade() calls asyncio.run()
        # internally, which fails when an event loop is already running
        # (startup_handler is async).
        await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
        logger.info("Migrations complete")
    except Exception as e:
        logger.warning("Migrations skipped or failed", extra={"error": str(e)})

    logger.info("Running database seed")
    try:
        import asyncio

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        # Converte URL async (postgresql+asyncpg://) para sync (postgresql://)
        sync_url = config.database.url.replace("+asyncpg", "").replace("+aiosqlite", "")

        def _run_seed():
            engine = create_engine(sync_url, pool_pre_ping=True)
            try:
                with Session(engine) as session:
                    from backend.database.seeds.roles import seed_roles_and_permissions
                    from backend.database.seeds.seed_data import seed_database

                    seed_roles_and_permissions(session)
                    seed_database(session)
            finally:
                engine.dispose()

        await asyncio.to_thread(_run_seed)
        logger.info("Database seed complete")
    except Exception as e:
        logger.warning("Database seed skipped or failed", extra={"error": str(e)})

    # Ensure RBAC system roles exist (idempotent)
    try:
        from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

        engine = create_async_engine(config.database.url, pool_size=1, echo=False)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            from backend.auth.rbac import ensure_system_roles

            await ensure_system_roles(session)
        await engine.dispose()
        logger.info("RBAC system roles ensured")
    except Exception as e:
        logger.warning("RBAC role seeding skipped or failed: %s", e)

    logger.info("Initializing cache")
    try:
        from redis.asyncio import Redis

        redis = Redis(
            host=config.redis.host,
            port=config.redis.port,
            password=config.redis.password or None,
            db=config.redis.db,
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

    from datetime import datetime

    service_registry.register("started_at", datetime.now(UTC).isoformat())

    # Feature initializers that previously used the deprecated
    # ``router.on_event("startup")`` hook (code_search + cloud pool).
    try:
        from backend.code_search.api import init_code_search_index

        await init_code_search_index()
        logger.info("Code-search index initialized")
    except Exception as e:
        logger.warning("Code-search index init skipped: %s", e)

    try:
        from backend.cloud.api import init_cloud_pool

        await init_cloud_pool()
        logger.info("Cloud pool initialized")
    except Exception as e:
        logger.warning("Cloud pool init skipped: %s", e)

    logger.info("Running health check")
    health = HealthChecker()
    results = await health.check_all()
    for name, status in results.items():
        logger.info("Health check", extra={"component": name, "status": status.status.value})

    logger.info("Startup complete")
