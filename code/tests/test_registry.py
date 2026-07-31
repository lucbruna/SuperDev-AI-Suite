from __future__ import annotations

import pytest

from SuperDev.code import CodeEngine


class TestCodeRegistry:
    """Tests for the CodeRegistry class."""

    def test_registry_initialization(self) -> None:
        engine = CodeEngine()
        registry = engine.registry
        assert registry is not None

    def test_registry_is_empty(self) -> None:
        engine = CodeEngine()
        assert engine.registry.size == 0
