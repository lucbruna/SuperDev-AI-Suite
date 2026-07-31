from __future__ import annotations

import pytest

from SuperDev.code import CodeEngine


class TestCodeManager:
    """Tests for the CodeManager class."""

    def test_initialization(self) -> None:
        engine = CodeEngine()
        manager = engine.manager
        assert manager is not None

    def test_register_code_engine(self) -> None:
        engine = CodeEngine()
        manager = engine.manager
        assert manager._engine is not None
