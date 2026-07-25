from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool

from backend.config import config


class DatabaseManager:
    """Production-ready database manager with connection pooling, health checks, and migrations."""

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
        self._readonly_engine: AsyncEngine | None = None
        self._readonly_session_factory: async_sessionmaker[AsyncSession] | None = None

    def create_engine(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        echo: bool = False,
        is_readonly: bool = False,
    ) -> AsyncEngine:
        """Create async engine with production-ready connection pooling."""
        
        if is_readonly:
            # Read-only replica can use larger pool
            pool_size = pool_size * 2
            max_overflow = max_overflow * 2

        engine = create_async_engine(
            database_url,
            echo=echo,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            pool_recycle=pool_recycle,
            pool_pre_ping=pool_pre_ping,
            connect_args={
                "server_settings": {
                    "application_name": "superdev-api",
                    "jit": "off",
                },
                "command_timeout": 60,
            },
        )

        # Add query timeouts
        @event.listens_for(engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            if not is_readonly:
                cursor.execute("SET LOCAL statement_timeout = '30s'")
            else:
                cursor.execute("SET LOCAL statement_timeout = '60s'")

        return engine

    def create_pgbouncer_engine(self, database_url: str) -> AsyncEngine:
        """Create engine optimized for PgBouncer transaction pooling."""
        # PgBouncer requires specific settings
        return create_async_engine(
            database_url,
            poolclass=NullPool,  # PgBouncer handles pooling
            echo=False,
            connect_args={
                "server_settings": {
                    "application_name": "superdev-api",
                    "jit": "off",
                },
                "command_timeout": 30,
                "statement_cache_size": 0,  # Disable prepared statements for PgBouncer
            },
        )

    async def initialize(self) -> None:
        """Initialize all database connections."""
        db_config = config.database

        # Determine if using PgBouncer
        use_pgbouncer = "pgbouncer" in db_config.url or db_config.pool_size == 0

        if use_pgbouncer:
            self._engine = self.create_pgbouncer_engine(db_config.url)
        else:
            self._engine = self.create_engine(
                database_url=db_config.url,
                pool_size=db_config.pool_size,
                max_overflow=db_config.max_overflow,
                pool_timeout=db_config.pool_timeout,
                pool_recycle=db_config.pool_recycle,
                pool_pre_ping=db_config.pool_pre_ping,
                echo=db_config.echo,
            )

        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        # Initialize read-only replica if configured
        if hasattr(db_config, 'readonly_url') and db_config.readonly_url:
            self._readonly_engine = self.create_engine(
                database_url=db_config.readonly_url,
                pool_size=db_config.pool_size * 2,
                max_overflow=db_config.max_overflow * 2,
                pool_timeout=db_config.pool_timeout,
                pool_recycle=db_config.pool_recycle,
                pool_pre_ping=db_config.pool_pre_ping,
                echo=False,
                is_readonly=True,
            )
            self._readonly_session_factory = async_sessionmaker(
                bind=self._readonly_engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )

        # Test connections
        await self.health_check()

    async def health_check(self) -> dict:
        """Comprehensive health check."""
        results = {"primary": False, "readonly": False}

        # Check primary
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                await conn.execute(text("SELECT pg_is_in_recovery()"))
                results["primary"] = True
        except Exception as e:
            results["primary_error"] = str(e)

        # Check readonly
        if self._readonly_engine:
            try:
                async with self._readonly_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    await conn.execute(text("SELECT pg_is_in_recovery()"))
                    results["readonly"] = True
            except Exception as e:
                results["readonly_error"] = str(e)

        return results

    @asynccontextmanager
    async def get_session(self, readonly: bool = False) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup."""
        if readonly and self._readonly_session_factory:
            session_factory = self._readonly_session_factory
        else:
            session_factory = self._session_factory

        if not session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_transaction(self, readonly: bool = False) -> AsyncGenerator[AsyncSession, None]:
        """Get session with explicit transaction control."""
        async with self.get_session(readonly=readonly) as session:
            async with session.begin():
                yield session

    async def execute_raw(self, query: str, params: dict = None, readonly: bool = False) -> list:
        """Execute raw SQL query."""
        async with self.get_session(readonly=readonly) as session:
            result = await session.execute(text(query), params or {})
            return result.mappings().all()

    async def get_pool_status(self) -> dict:
        """Get connection pool statistics."""
        pool = self._engine.pool
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalidated(),
        }

    async def close(self) -> None:
        """Close all database connections."""
        if self._engine:
            await self._engine.dispose()
        if self._readonly_engine:
            await self._readonly_engine.dispose()


# Global instance
db_manager = DatabaseManager()


async def get_db_session(readonly: bool = False) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with db_manager.get_session(readonly=readonly) as session:
        yield session


async def get_db_readonly() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for read-only database sessions."""
    async with db_manager.get_session(readonly=True) as session:
        yield session


async def init_database() -> None:
    """Initialize database on application startup."""
    await db_manager.initialize()


async def close_database() -> None:
    """Close database on application shutdown."""
    await db_manager.close()