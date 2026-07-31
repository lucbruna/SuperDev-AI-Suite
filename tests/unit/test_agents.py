"""Tests for agents module: base_agent, tool_registry."""

import pytest
from backend.agents.base_agent import (
    AgentResult,
    AgentStatus,
    AgentStep,
    AgentType,
    BaseAgent,
    ToolCall,
)
from backend.agents.tool_registry import ToolRegistry, ToolDefinition


# ── Enums ───────────────────────────────────────────────────────────


class TestAgentEnums:
    def test_agent_status_values(self):
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.PAUSED.value == "paused"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.COMPLETED.value == "completed"

    def test_agent_type_values(self):
        assert AgentType.REACT.value == "react"
        assert AgentType.PLANNER_EXECUTOR.value == "planner_executor"
        assert AgentType.CODE.value == "code"
        assert AgentType.REVIEW.value == "review"
        assert AgentType.CHAT.value == "chat"


# ── ToolCall ────────────────────────────────────────────────────────


class TestToolCall:
    def test_creation(self):
        tc = ToolCall(id="tc1", name="read_file", arguments={"path": "/tmp/a.py"})
        assert tc.result is None
        assert tc.error is None

    def test_with_result(self):
        tc = ToolCall(id="tc1", name="read", arguments={}, result="content")
        assert tc.result == "content"

    def test_with_error(self):
        tc = ToolCall(id="tc1", name="read", arguments={}, error="not found")
        assert tc.error == "not found"


# ── AgentStep ───────────────────────────────────────────────────────


class TestAgentStep:
    def test_defaults(self):
        step = AgentStep()
        assert step.thought == ""
        assert step.action == ""
        assert step.action_input == {}
        assert step.observation is None
        assert step.tool_calls == []

    def test_custom(self):
        step = AgentStep(
            thought="I need to read the file",
            action="read_file",
            action_input={"path": "/tmp/a.py"},
            observation="file content",
        )
        assert step.thought == "I need to read the file"
        assert step.action == "read_file"


# ── AgentResult ─────────────────────────────────────────────────────


class TestAgentResult:
    def test_defaults(self):
        result = AgentResult(output="done")
        assert result.steps == []
        assert result.tool_calls == []
        assert result.token_usage == {}
        assert result.execution_time_ms == 0.0
        assert result.error is None

    def test_with_error(self):
        result = AgentResult(output="", error="timeout")
        assert result.error == "timeout"


# ── BaseAgent (concrete implementation) ─────────────────────────────


class ConcreteAgent(BaseAgent):
    async def run(self, input_text, context=None, **kwargs):
        return AgentResult(output=f"Processed: {input_text}")

    async def think(self, messages, **kwargs):
        return "thinking..."

    async def act(self, action, action_input, **kwargs):
        return {"action": action}


class TestBaseAgent:
    def test_creation(self):
        agent = ConcreteAgent(name="TestAgent", description="A test agent")
        assert agent.name == "TestAgent"
        assert agent.description == "A test agent"
        assert agent.agent_type == AgentType.REACT
        assert agent.status == AgentStatus.IDLE

    def test_custom_type(self):
        agent = ConcreteAgent(name="CodeAgent", agent_type=AgentType.CODE)
        assert agent.agent_type == AgentType.CODE

    def test_register_tool(self):
        agent = ConcreteAgent(name="A")
        agent.register_tool("read_file", "Read a file", {"path": "string"})
        tools = agent.get_tools_schema()
        assert len(tools) == 1
        assert tools[0]["name"] == "read_file"

    def test_to_dict(self):
        agent = ConcreteAgent(name="A", model="gpt-4", provider="openai")
        d = agent.to_dict()
        assert d["name"] == "A"
        assert d["model"] == "gpt-4"
        assert d["provider"] == "openai"
        assert d["status"] == "idle"

    @pytest.mark.asyncio
    async def test_run(self):
        agent = ConcreteAgent(name="A")
        result = await agent.run("hello")
        assert result.output == "Processed: hello"

    @pytest.mark.asyncio
    async def test_think(self):
        agent = ConcreteAgent(name="A")
        thought = await agent.think([{"role": "user", "content": "hi"}])
        assert thought == "thinking..."

    @pytest.mark.asyncio
    async def test_act(self):
        agent = ConcreteAgent(name="A")
        result = await agent.act("read_file", {"path": "/tmp/a.py"})
        assert result["action"] == "read_file"


# ── ToolRegistry ────────────────────────────────────────────────────


class TestToolRegistry:
    def test_register_and_get(self):
        registry = ToolRegistry()

        async def handler(**kwargs):
            return "ok"

        registry.register("test_tool", "A test tool", {"param": "string"}, handler)
        tool = registry.get("test_tool")
        assert tool is not None
        assert tool.name == "test_tool"
        assert tool.description == "A test tool"

    def test_get_not_found(self):
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_list_tools(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("t1", "Tool 1", {}, h, tags=["code"])
        registry.register("t2", "Tool 2", {}, h, tags=["file"])
        assert len(registry.list_tools()) == 2

    def test_list_tools_by_tag(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("t1", "Tool 1", {}, h, tags=["code"])
        registry.register("t2", "Tool 2", {}, h, tags=["file"])
        code_tools = registry.list_tools(tag="code")
        assert len(code_tools) == 1
        assert code_tools[0].name == "t1"

    def test_get_schemas(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("t1", "Tool 1", {"p": "string"}, h)
        schemas = registry.get_schemas()
        assert len(schemas) == 1
        assert schemas[0]["name"] == "t1"
        assert schemas[0]["parameters"]["p"] == "string"

    @pytest.mark.asyncio
    async def test_execute(self):
        registry = ToolRegistry()

        async def add(a: int, b: int) -> int:
            return a + b

        registry.register("add", "Add numbers", {}, add)
        result = await registry.execute("add", a=3, b=4)
        assert result == 7

    @pytest.mark.asyncio
    async def test_execute_not_found(self):
        registry = ToolRegistry()
        with pytest.raises(ValueError, match="Tool not found"):
            await registry.execute("nonexistent")

    def test_delete(self):
        registry = ToolRegistry()

        async def h(**kw):
            return None

        registry.register("t1", "Tool 1", {}, h)
        assert registry.delete("t1") is True
        assert registry.get("t1") is None

    def test_delete_not_found(self):
        registry = ToolRegistry()
        assert registry.delete("nonexistent") is False
