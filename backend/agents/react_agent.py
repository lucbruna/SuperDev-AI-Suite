from __future__ import annotations

import asyncio
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

# Timeout constants
STEP_TIMEOUT_SECONDS = 60  # Max time per LLM call + tool execution
OVERALL_TIMEOUT_SECONDS = 240  # Max total agent runtime (4 minutes)


class ReActAgent(BaseAgent):
    """ReAct (Reasoning + Acting) agent implementation."""

    def __init__(self, **kwargs):
        # Optional DB session so the runtime honors providers saved in the UI
        # (api key / base URL / model) instead of only env vars.
        self._db = kwargs.pop("db", None)
        super().__init__(agent_type=AgentType.REACT, **kwargs)
        for tool in tool_registry.get_schemas():
            self.register_tool(tool["name"], tool["description"], tool["parameters"])

    def _build_system_prompt(self) -> str:
        tools_desc = "\n".join(f"- {t['name']}: {t['description']}" for t in self._tools)
        return f"""You are {self.name}. {self.description}

You have access to the following tools:
{tools_desc}

You are a coding agent with permission to inspect, create, edit, search, and
delete files inside the project workspace. Do not claim that you cannot access
files or folders: use the available tools whenever the task needs them. Make
the requested code changes directly, then inspect the relevant files to verify
them. File access is intentionally limited to the project workspace.
You can also clone HTTPS GitHub repositories into that workspace when a task
requires external project files.

You also have access to installed agent skills via the skills tools.
Use `list_skills` to see available skills, and `read_skill` to read a skill's
instructions. Skills contain best practices, workflows, and patterns for
specific tasks like code review, security audit, FastAPI development, etc.

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
        try:
            response = await asyncio.wait_for(
                ai_router.complete(
                    messages=provider_messages,
                    model=self.model,
                    provider=self.provider,
                    temperature=self.temperature,
                    max_tokens=1024,
                ),
                timeout=STEP_TIMEOUT_SECONDS,
            )
            return response.content
        except TimeoutError:
            return json.dumps({
                "thought": "LLM call timed out, finishing with current progress",
                "action": "finish",
                "action_input": {"output": "Request timed out. The task required more time than allowed. Please try a simpler request or break it into smaller steps."}
            })

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
                # Check overall timeout
                elapsed = time.time() - start_time
                if elapsed > OVERALL_TIMEOUT_SECONDS:
                    self._status = AgentStatus.COMPLETED
                    return AgentResult(
                        output=f"Agent timed out after {int(elapsed)}s. The task is complex — try breaking it into smaller steps.",
                        steps=steps,
                        tool_calls=all_tool_calls,
                        execution_time_ms=elapsed * 1000,
                    )

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
                    self.name,
                    (step_num + 1) / self.max_steps * 100,
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
                messages.append(
                    {
                        "role": "user",
                        "content": f"Observation: {json.dumps(observation) if not isinstance(observation, str) else observation}",
                    }
                )

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
