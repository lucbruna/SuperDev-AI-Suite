"""Tests for the AI tools core engine components."""

from __future__ import annotations

import pytest
from typing import Any

from ai.tools.tool_engine import ToolEngine
from ai.tools.tool_manager import ToolManager
from ai.tools.tool_factory import ToolFactory
from ai.tools.tool_registry import ToolRegistry
from ai.tools.tool_executor import ToolExecutor
from ai.tools.tool_validator import ToolValidator
from ai.tools.tool_models import ToolCall, ToolRegistration, ToolContext
from ai.tools.tool_interfaces import ITool, IToolRegistry, IToolExecutor, IToolFactory
from ai.tools.tool_types import ToolStatus, ToolCategory


class TestToolModels:
    """Tests for tool data models."""

    def test_tool_call_defaults(self):
        call = ToolCall(tool_name="test_tool", params={"key": "value"})
        assert call.tool_name == "test_tool"
        assert call.params == {"key": "value"}
        assert call.result is None
        assert call.status == "pending"
        assert call.error is None
        assert call.duration == 0.0

    def test_tool_call_with_result(self):
        call = ToolCall(
            tool_name="test",
            params={},
            result={"success": True},
            status="completed",
            started_at=100.0,
            completed_at=105.0,
        )
        assert call.result == {"success": True}
        assert call.status == "completed"
        assert call.duration == 5.0

    def test_tool_registration(self):
        reg = ToolRegistration(name="my_tool", tool_class=str, category="filesystem")
        assert reg.name == "my_tool"
        assert reg.tool_class is str
        assert reg.category == "filesystem"
        assert reg.version == "1.0.0"
        assert reg.registered_at > 0

    def test_tool_context(self):
        ctx = ToolContext(
            execution_id="exec_1",
            user_id="user_1",
            session_id="session_1",
            permissions=["read", "write"],
        )
        assert ctx.execution_id == "exec_1"
        assert ctx.user_id == "user_1"
        assert "read" in ctx.permissions


class TestToolValidator:
    """Tests for the tool validator."""

    def test_initialization(self):
        validator = ToolValidator()
        assert validator is not None


class TestToolRegistry:
    """Tests for the tool registry."""

    @pytest.fixture
    def registry(self):
        return ToolRegistry()

    def test_register_and_get(self, registry):
        from ai.tools.filesystem.filesystem_tool import FilesystemTool
        tool = FilesystemTool()
        name = registry.register(tool)
        assert name == "filesystem"
        retrieved = registry.get("filesystem")
        assert retrieved is not None
        assert retrieved.name() == "filesystem"

    def test_unregister(self, registry):
        from ai.tools.git.git_tool import GitTool
        tool = GitTool()
        registry.register(tool)
        assert registry.unregister("git") is True
        assert registry.get("git") is None

    def test_list_tools(self, registry):
        from ai.tools.filesystem.filesystem_tool import FilesystemTool
        from ai.tools.git.git_tool import GitTool
        registry.register(FilesystemTool())
        registry.register(GitTool())
        tools = registry.list_tools()
        assert len(tools) == 2


class TestToolFactory:
    """Tests for the tool factory."""

    @pytest.fixture
    def factory(self):
        return ToolFactory()

    def test_create_tool(self, factory):
        from ai.tools.filesystem.filesystem_tool import FilesystemTool
        factory.register_class("filesystem", FilesystemTool)
        tool = factory.create("filesystem")
        assert tool is not None
        assert isinstance(tool, FilesystemTool)

    def test_create_unknown_tool(self, factory):
        with pytest.raises(ValueError):
            factory.create("nonexistent_tool")


class TestToolExecutor:
    """Tests for the tool executor."""

    @pytest.fixture
    def executor(self):
        registry = ToolRegistry()
        validator = ToolValidator()
        from ai.tools.tool_metrics import ToolMetrics
        from ai.tools.tool_logger import ToolLogger
        metrics = ToolMetrics()
        logger = ToolLogger()
        return ToolExecutor(registry, validator, metrics, logger)

    def test_initialization(self, executor):
        assert executor is not None


class TestToolManager:
    """Tests for the tool manager."""

    @pytest.fixture
    def manager(self):
        return ToolManager()

    def test_initialization(self, manager):
        assert manager is not None


class TestToolEngine:
    """Tests for the tool engine."""

    @pytest.fixture
    def engine(self):
        eng = ToolEngine()
        from ai.tools.filesystem.filesystem_tool import FilesystemTool
        eng.register_tool(FilesystemTool())
        return eng

    def test_initialization(self, engine):
        assert engine is not None

    def test_list_tools(self, engine):
        tools = engine.list_tools()
        assert "filesystem" in tools

    def test_get_status(self, engine):
        status = engine.get_status()
        assert status is not None
