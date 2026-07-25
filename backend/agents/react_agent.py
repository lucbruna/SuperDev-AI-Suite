from __future__ import annotations

import json
import time
from typing import Any

from backend.agents.base_agent import (
    AgentResult,
    AgentStatus,
    AgentStep,
    AgentType,
    BaseAgent,
    ToolCall,
)
from backend.agents.tool_registry import tool_registry
from backend.ai_router.router import router as ai_router
from backend.providers.base_provider import Message
from backend.websocket.events import EventBuilder
from backend.websocket.manager import manager


class ReActAgent(BaseAgent):
    """ReAct (Reasoning + Acting) agent implementation."""

    def __init__(self, **kwargs):
        super().__init__(agent_type=AgentType.REACT, **kwargs)
        for tool in tool_registry.get_schemas():
            self.register_tool(tool["name"], tool["description"], tool["parameters"])

    def _build_system_prompt(self) -> str:
        tools_desc = "\n".join(
            f"- {t['name']}: {t['description']}"
            for t in self._tools
        )
        return f"""You are {self.name}. {self.description}

You have access to the following tools:
{tools_desc}

To use a tool, respond with a JSON object in this exact format:
{{"thought": "your reasoning about what to do next", "action": "tool_name", "action_input": {{"param1": "value1"}}}}

When you have the final answer, respond with:
{{"thought": "your final reasoning", "action": "finish", "action_input": {{"output": "your final answer"}}}}

Always think step by step. Use tools when needed to accomplish the task."""

    async def think(
        self,
        messages: list[dict[str, str]],
        **kwargs,
    ) -> str:
        provider_messages = [Message(role=m["role"], content=m["content"]) for m in messages]
        response = await ai_router.complete(
            messages=provider_messages,
            model=self.model,
            provider=self.provider,
            temperature=self.temperature,
            max_tokens=1024,
        )
        return response.content

    async def act(
        self,
        action: str,
        action_input: dict[str, Any],
        **kwargs,
    ) -> Any:
        if action == "finish":
            return action_input.get("output", "")

        result = await tool_registry.execute(action, **action_input)
        return result

    async def run(
        self,
        input_text: str,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> AgentResult:
        self._status = AgentStatus.RUNNING
        start_time = time.time()
        steps: list[AgentStep] = []
        all_tool_calls: list[ToolCall] = []

        event = EventBuilder.agent_start(self.name, self.name)
        await manager.broadcast_all(event.to_dict())

        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": input_text},
        ]

        try:
            for step_num in range(self.max_steps):
                response_text = await self.think(messages)

                try:
                    parsed = json.loads(response_text)
                except json.JSONDecodeError:
                    parsed = {"thought": response_text, "action": "finish", "action_input": {"output": response_text}}

                step = AgentStep(
                    thought=parsed.get("thought", ""),
                    action=parsed.get("action", ""),
                    action_input=parsed.get("action_input", {}),
                )

                progress_event = EventBuilder.agent_progress(
                    self.name, (step_num + 1) / self.max_steps * 100,
                    step.thought[:100],
                )
                await manager.broadcast_all(progress_event.to_dict())

                if step.action == "finish":
                    output = step.action_input.get("output", "")
                    steps.append(step)

                    complete_event = EventBuilder.agent_complete(self.name, output)
                    await manager.broadcast_all(complete_event.to_dict())

                    execution_time = (time.time() - start_time) * 1000
                    self._status = AgentStatus.COMPLETED
                    return AgentResult(
                        output=output,
                        steps=steps,
                        tool_calls=all_tool_calls,
                        execution_time_ms=execution_time,
                    )

                tool_call = ToolCall(
                    id=f"call_{step_num}",
                    name=step.action,
                    arguments=step.action_input,
                )

                try:
                    observation = await self.act(step.action, step.action_input)
                    tool_call.result = observation
                except Exception as e:
                    tool_call.error = str(e)
                    observation = f"Error: {e}"

                step.observation = observation
                step.tool_calls.append(tool_call)
                all_tool_calls.append(tool_call)
                steps.append(step)

                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"Observation: {json.dumps(observation) if not isinstance(observation, str) else observation}"})

            execution_time = (time.time() - start_time) * 1000
            self._status = AgentStatus.COMPLETED
            return AgentResult(
                output="Max steps reached without completion",
                steps=steps,
                tool_calls=all_tool_calls,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._status = AgentStatus.ERROR
            error_event = EventBuilder.agent_complete(self.name, error=str(e))
            await manager.broadcast_all(error_event.to_dict())
            return AgentResult(
                output="",
                steps=steps,
                tool_calls=all_tool_calls,
                execution_time_ms=execution_time,
                error=str(e),
            )
