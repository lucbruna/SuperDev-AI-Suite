"""Alembic environment configuration for async SQLAlchemy.

Reads database URL from backend.config and runs migrations using async engine.
"""
from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import Base to get all models registered on metadata
from backend.database.base import Base

# Import all models so they register on Base.metadata
import backend.database.models.user  # noqa: F401
import backend.database.models.project  # noqa: F401
import backend.database.models.workflow  # noqa: F401
import backend.database.models.agent  # noqa: F401
import backend.database.models.plugin  # noqa: F401
import backend.database.models.provider  # noqa: F401
import backend.database.models.knowledge  # noqa: F401
import backend.database.models.notification  # noqa: F401
import backend.database.models.audit  # noqa: F401
import backend.database.models.organization  # noqa: F401
import backend.database.models.role  # noqa: F401
import backend.database.models.api_key  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override sqlalchemy.url from application config
try:
    from backend.config import config as app_config
    config.set_main_option("sqlalchemy.url", app_config.database.url)
except Exception:
    pass


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
