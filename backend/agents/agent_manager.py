from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.react_agent import ReActAgent
from backend.utils.uuid_utils import generate_uuid


class AgentManager:
    """Manages agent creation, lifecycle, and execution."""

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}
        self._executions: dict[str, dict[str, Any]] = {}

    def create_agent(
        self,
        name: str,
        description: str = "",
        agent_type: str = "react",
        model: str | None = None,
        provider: str | None = None,
        max_steps: int = 10,
        temperature: float = 0.7,
        **kwargs,
    ) -> BaseAgent:
        agent_id = generate_uuid()

        if agent_type == "react":
            agent = ReActAgent(
                name=name,
                description=description,
                model=model,
                provider=provider,
                max_steps=max_steps,
                temperature=temperature,
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        self._agents[agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict[str, Any]]:
        return [
            {**agent.to_dict(), "id": agent_id}
            for agent_id, agent in self._agents.items()
        ]

    def delete_agent(self, agent_id: str) -> bool:
        if agent_id in self._agents:
            del self._agents[agent_id]
            return True
        return False

    async def execute_agent(
        self,
        agent_id: str,
        input_text: str,
        context: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        agent = self._agents.get(agent_id)
        if not agent:
            return {"error": f"Agent not found: {agent_id}"}

        execution_id = generate_uuid()
        self._executions[execution_id] = {
            "agent_id": agent_id,
            "status": "running",
            "user_id": user_id,
        }

        result = await agent.run(input_text, context)

        self._executions[execution_id]["status"] = result.error and "failed" or "completed"

        return {
            "execution_id": execution_id,
            "agent_id": agent_id,
            "output": result.output,
            "steps": [
                {
                    "thought": s.thought,
                    "action": s.action,
                    "observation": s.observation,
                }
                for s in result.steps
            ],
            "tool_calls": [
                {
                    "name": tc.name,
                    "arguments": tc.arguments,
                    "result": tc.result,
                    "error": tc.error,
                }
                for tc in result.tool_calls
            ],
            "execution_time_ms": result.execution_time_ms,
            "error": result.error,
        }

    def get_execution(self, execution_id: str) -> dict[str, Any] | None:
        return self._executions.get(execution_id)


agent_manager = AgentManager()


BUILTIN_AGENTS = [
    {
        "name": "Code Assistant",
        "description": "Helps with coding tasks, debugging, and code generation",
        "agent_type": "react",
        "max_steps": 15,
    },
    {
        "name": "Code Reviewer",
        "description": "Reviews code for quality, bugs, and improvements",
        "agent_type": "react",
        "max_steps": 10,
    },
    {
        "name": "Debugger",
        "description": "Helps identify and fix bugs in code",
        "agent_type": "react",
        "max_steps": 10,
    },
    {
        "name": "Documentation Writer",
        "description": "Generates documentation for code and projects",
        "agent_type": "react",
        "max_steps": 8,
    },
    {
        "name": "Test Generator",
        "description": "Generates unit tests for code",
        "agent_type": "react",
        "max_steps": 10,
    },
]

for agent_data in BUILTIN_AGENTS:
    try:
        agent_manager.create_agent(**agent_data)
    except Exception:
        pass
