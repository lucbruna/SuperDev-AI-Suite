from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class LlmTokenizer(BaseTool):
    """LLM tokenizer utilities."""

    _name = "llm_tokenizer"
    _description = "Tokenize, count tokens, and estimate costs for LLM text"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._tokenizer_log: list[dict[str, Any]] = []

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
            if action == "encode":
                text = params.get("text", "")
                tokens = [ord(c) for c in text[:50]]
                return {"success": True, "tokens": tokens, "count": len(tokens)}
            elif action == "decode":
                tokens = params.get("tokens", [])
                text = "".join(chr(t) for t in tokens[:50] if 32 <= t <= 126)
                return {"success": True, "text": text}
            elif action == "count":
                text = params.get("text", "")
                model = params.get("model", "gpt-4")
                estimated_tokens = len(text) // 4
                return {"success": True, "count": estimated_tokens, "model": model}
            elif action == "estimate_cost":
                text = params.get("text", "")
                model = params.get("model", "gpt-4")
                tokens = len(text) // 4
                cost_per_token = 0.00003 if "gpt-4" in model else 0.000002
                cost = tokens * cost_per_token
                return {"success": True, "tokens": tokens, "cost_usd": round(cost, 6), "model": model}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._tokenizer_log.clear()

    async def cleanup(self) -> None:
        self._tokenizer_log.clear()
