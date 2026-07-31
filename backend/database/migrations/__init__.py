"""Migration helpers for programmatic migration control.

Provides functions to run Alembic migrations, create/drop tables,
and manage the database lifecycle without the CLI.
"""
from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("superdev.migrations")

_ALEMBIC_DIR = Path(__file__).resolve().parent.parent.parent.parent / "alembic"


async def run_migrations(upgrade: bool = True) -> None:
    """Run Alembic migrations programmatically.

    Parameters
    ----------
    upgrade:
        If *True* runs ``upgrade head``, otherwise ``downgrade base``.
    """
    from alembic.config import Config

    from alembic import command

    alembic_cfg = Config(str(_ALEMBIC_DIR.parent / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(_ALEMBIC_DIR))

    try:
        if upgrade:
            command.upgrade(alembic_cfg, "head")
            logger.info("Migrations upgraded to head")
        else:
            command.downgrade(alembic_cfg, "base")
            logger.info("Migrations downgraded to base")
    except Exception:
        logger.exception("Migration failed")
        raise


async def create_tables(session: AsyncSession) -> None:
    """Create all tables from Base metadata (dev convenience).

    This bypasses Alembic and creates tables directly — useful for
    quick dev setup or test fixture creation.
    """
    from backend.database.base import Base

    conn = await session.get_bind()
    await conn.run_sync(Base.metadata.create_all)
    logger.info("All tables created from Base.metadata")


async def drop_tables(session: AsyncSession) -> None:
    """Drop all tables from Base metadata (testing convenience).

    .. warning:: This drops ALL tables.  Only use in test environments.
    """
    from backend.database.base import Base

    conn = await session.get_bind()
    await conn.run_sync(Base.metadata.drop_all)
    logger.info("All tables dropped from Base.metadata")


async def get_current_revision() -> str | None:
    """Return the current Alembic migration revision, or *None* if no migrations exist."""
    try:
        from alembic.config import Config

        from alembic import command

        alembic_cfg = Config(str(_ALEMBIC_DIR.parent / "alembic.ini"))
        alembic_cfg.set_main_option("script_location", str(_ALEMBIC_DIR))

        from alembic.script import ScriptDirectory
        script = ScriptDirectory.from_config(alembic_cfg)
        head = script.get_current_head()
        return head
    except Exception:
        logger.debug("Could not determine Alembic revision")
        return None


async def stamp_head() -> None:
    """Stamp the current state as head (for existing databases without migration history)."""
    from alembic.config import Config

    from alembic import command

    alembic_cfg = Config(str(_ALEMBIC_DIR.parent / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(_ALEMBIC_DIR))
    command.stamp(alembic_cfg, "head")
    logger.info("Database stamped at head")
