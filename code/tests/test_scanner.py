from __future__ import annotations

import pytest

from SuperDev.code import CodeEngine


class TestCodeScanner:
    """Tests for the CodeScanner class."""

    def test_scanner_initialization(self) -> None:
        engine = CodeEngine()
        scanner = engine.scanner
        assert scanner is not None

    def test_scanner_has_engine_ref(self) -> None:
        engine = CodeEngine()
        assert engine.scanner._engine is not None
