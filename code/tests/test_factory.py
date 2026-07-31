from __future__ import annotations

import pytest

from SuperDev.code import CodeEngine


class TestCodeFactory:
    """Tests for the CodeFactory class."""

    def test_factory_initialization(self) -> None:
        engine = CodeEngine()
        factory = engine.factory
        assert factory is not None

    def test_factory_has_engine(self) -> None:
        engine = CodeEngine()
        assert engine.factory._engine is not None
