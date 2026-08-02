"""Alembic environment configuration for async SQLAlchemy migrations.

Supports both PostgreSQL (production) and SQLite (testing).
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from backend.database.base import Base

# Import all models so Alembic can detect them. The audit table lives in
# ``audit_log.py`` (there is no ``audit`` module — importing it was a pre-
# existing bug that made ``alembic upgrade head`` fail with ImportError).
from backend.database.models import (  # noqa: F401
    agent,
    audit_log,
    knowledge,
    notification,
    organization,
    plugin,
    project,
    provider,
    role,
    user,
    workflow,
)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override sqlalchemy.url from environment if available
import os

db_url = os.getenv("DATABASE_URL") or os.getenv("ALEMBIC_DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode — generate SQL without connecting."""
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
    """Run migrations in 'online' mode with an async engine."""
    # The application engine (backend/database/engine.py) pins the search path
    # to ``superdev,public``; mirror it here so ALTER/CREATE statements land in
    # the same schema the models read from.
    connect_args = {}
    if (db_url or "").startswith("postgresql"):
        connect_args = {"server_settings": {"search_path": "superdev,public"}}
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entrypoint for online migrations — delegates to async runner."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
