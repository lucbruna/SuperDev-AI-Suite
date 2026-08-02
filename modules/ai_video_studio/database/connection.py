"""Database connection manager with health checks."""
from __future__ import annotations
import logging
from sqlalchemy import text
from modules.ai_video_studio.database.database import get_engine

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and health checks."""

    @staticmethod
    async def health_check() -> dict:
        try:
            engine = await get_engine()
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                row = result.scalar()
                return {"status": "healthy", "database": "connected", "result": row}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

    @staticmethod
    async def get_pool_stats() -> dict:
        engine = await get_engine()
        pool = engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
        }