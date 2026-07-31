from __future__ import annotations

import pytest

from SuperDev.code import CodeEngine


class TestCodeConfig:
    """Tests for the CodeConfig class."""

    def test_config_initialization(self) -> None:
        engine = CodeEngine()
        config = engine.config
        assert config is not None

    def test_config_has_defaults(self) -> None:
        engine = CodeEngine()
        config = engine.config
        assert hasattr(config, "settings")
