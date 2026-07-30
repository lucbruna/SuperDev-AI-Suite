"""Tests for the Alembic migration infrastructure."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

from backend.database.migrations import (
    create_tables,
    drop_tables,
    get_current_revision,
    run_migrations,
    stamp_head,
)


class TestAlembicConfig:
    def test_alembic_ini_exists(self):
        ini_path = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
        assert ini_path.exists(), f"alembic.ini not found at {ini_path}"

    def test_alembic_env_exists(self):
        env_path = Path(__file__).resolve().parent.parent.parent / "alembic" / "env.py"
        assert env_path.exists(), f"alembic/env.py not found at {env_path}"

    def test_alembic_script_template_exists(self):
        tpl_path = Path(__file__).resolve().parent.parent.parent / "alembic" / "script.py.mako"
        assert tpl_path.exists(), f"alembic/script.py.mako not found at {tpl_path}"

    def test_versions_directory_exists(self):
        versions_dir = Path(__file__).resolve().parent.parent.parent / "alembic" / "versions"
        assert versions_dir.exists(), f"alembic/versions/ not found at {versions_dir}"


class TestMigrationsModule:
    def test_module_imports(self):
        from backend.database import migrations
        assert hasattr(migrations, "run_migrations")
        assert hasattr(migrations, "create_tables")
        assert hasattr(migrations, "drop_tables")
        assert hasattr(migrations, "get_current_revision")
        assert hasattr(migrations, "stamp_head")

    @pytest.mark.asyncio
    async def test_get_current_revision_returns_string_or_none(self):
        result = await get_current_revision()
        assert result is None or isinstance(result, str)


class TestAlembicIni:
    def test_has_script_location(self):
        ini_path = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
        content = ini_path.read_text()
        assert "script_location" in content

    def test_has_sqlalchemy_url(self):
        ini_path = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
        content = ini_path.read_text()
        assert "sqlalchemy.url" in content
