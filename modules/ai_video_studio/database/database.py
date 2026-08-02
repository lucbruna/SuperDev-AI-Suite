"""Async database access for AI Video Studio — delegated to the backend.

The video studio module runs as a native SuperDev module: it shares the
backend's single engine/session instead of creating its own. All public
names below are kept for import compatibility with existing routes.
"""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)


async def get_engine() -> AsyncEngine:
    """Return the shared backend async engine."""
    from backend.database.engine import get_engine_instance

    return get_engine_instance()


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared backend session factory."""
    from backend.database.session import async_session_factory

    return async_session_factory()


async def get_db():
    """FastAPI dependency that yields a session and auto-closes.

    Delegates to the backend's session dependency so the whole platform
    shares one connection pool and transaction lifecycle.
    """
    from backend.database.session import get_db as backend_get_db

    async for session in backend_get_db():
        yield session


async def init_db() -> None:
    """Create all tables (use Alembic in production)."""
    from backend.database.base import Base
    from backend.database.engine import get_engine_instance

    engine = get_engine_instance()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db() -> None:
    """Dispose the shared backend engine."""
    from backend.database.engine import dispose_engine

    await dispose_engine()
    logger.info("Database engine disposed")
