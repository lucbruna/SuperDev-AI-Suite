from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class LlmModel(BaseTool):
    """LLM model management."""

    _name = "llm_model"
    _description = "Manage LLM models: list, info, set_active, compare"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {
            "gpt-4": {"provider": "openai", "context": 8192, "available": True},
            "gpt-4-turbo": {"provider": "openai", "context": 128000, "available": True},
            "gpt-3.5-turbo": {"provider": "openai", "context": 16384, "available": True},
            "claude-3-opus": {"provider": "anthropic", "context": 200000, "available": True},
            "claude-3-sonnet": {"provider": "anthropic", "context": 200000, "available": True},
        }
        self._active: str = "gpt-4"

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
            if action == "list":
                return {"success": True, "models": self._models, "active": self._active}
            elif action == "info":
                model_name = params.get("model", self._active)
                info = self._models.get(model_name)
                if not info:
                    return {"success": False, "error": f"Model not found: {model_name}"}
                return {"success": True, "model": model_name, "info": info}
            elif action == "set_active":
                model_name = params.get("model", "")
                if model_name not in self._models:
                    return {"success": False, "error": f"Model not found: {model_name}"}
                self._active = model_name
                return {"success": True, "active": model_name}
            elif action == "compare":
                model_a = params.get("model_a", "gpt-4")
                model_b = params.get("model_b", "claude-3-opus")
                info_a = self._models.get(model_a, {})
                info_b = self._models.get(model_b, {})
                return {"success": True, "comparison": {model_a: info_a, model_b: info_b}}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._active = "gpt-4"

    async def cleanup(self) -> None:
        pass
