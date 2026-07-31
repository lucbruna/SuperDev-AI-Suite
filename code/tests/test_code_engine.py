from __future__ import annotations

from pathlib import Path

import pytest

from SuperDev.code import CodeEngine
from SuperDev.code.code_models import CodeFile, CodeIssue, CodeIssueSeverity


class TestCodeEngine:
    """Tests for the central CodeEngine class."""

    def test_initialization(self) -> None:
        engine = CodeEngine()
        assert engine is not None

    def test_manager_creation(self) -> None:
        engine = CodeEngine()
        manager = engine.manager
        assert manager is not None

    def test_factory_creation(self) -> None:
        engine = CodeEngine()
        factory = engine.factory
        assert factory is not None

    def test_scanner_creation(self) -> None:
        engine = CodeEngine()
        scanner = engine.scanner
        assert scanner is not None


class TestCodeModels:
    """Tests for the code data models."""

    def test_code_file_creation(self) -> None:
        cf = CodeFile(path="test.py", language="python", content="print('hello')")
        assert cf.path == "test.py"
        assert cf.language == "python"
        assert cf.content == "print('hello')"

    def test_code_issue_creation(self) -> None:
        issue = CodeIssue(
            message="Test issue",
            severity=CodeIssueSeverity.WARNING,
            line=10,
            column=5,
        )
        assert issue.message == "Test issue"
        assert issue.severity == CodeIssueSeverity.WARNING
        assert issue.line == 10
        assert issue.column == 5

    def test_code_issue_severity_values(self) -> None:
        assert CodeIssueSeverity.INFO.value == "info"
        assert CodeIssueSeverity.WARNING.value == "warning"
        assert CodeIssueSeverity.ERROR.value == "error"
        assert CodeIssueSeverity.CRITICAL.value == "critical"
