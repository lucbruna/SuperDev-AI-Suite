from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class LlmCompletion(BaseTool):
    """LLM text completions."""

    _name = "llm_completion"
    _description = "Generate LLM text completions with configurable parameters"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._completion_log: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        try:
            if action == "complete":
                prompt = params.get("prompt", "")
                model = params.get("model", "gpt-4")
                params.get("max_tokens", 256)
                params.get("temperature", 0.7)
                result = {
                    "model": model,
                    "prompt": prompt,
                    "completion": f"This is a mock completion for: {prompt[:50]}...",
                    "usage": {"prompt_tokens": len(prompt), "completion_tokens": 50, "total_tokens": len(prompt) + 50},
                }
                self._completion_log.append(result)
                return {"success": True, **result}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._completion_log.clear()

    async def cleanup(self) -> None:
        self._completion_log.clear()
