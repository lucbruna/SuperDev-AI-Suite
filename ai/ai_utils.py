from __future__ import annotations

import json
import uuid
from typing import Any

TOKEN_RATE: float = 4.0

COST_PER_TOKEN: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 0.00001, "output": 0.00003},
    "gpt-4o-mini": {"input": 0.0000015, "output": 0.000006},
    "claude-3-5-sonnet-20241022": {"input": 0.000003, "output": 0.000015},
    "claude-3-haiku": {"input": 0.00000025, "output": 0.00000125},
    "gemini-1.5-pro": {"input": 0.0000035, "output": 0.0000105},
    "gemini-1.5-flash": {"input": 0.00000035, "output": 0.00000105},
    "llama3": {"input": 0.0, "output": 0.0},
}


def count_tokens(text: str) -> int:
    """Estimate token count from text."""
    return max(1, int(len(text) / TOKEN_RATE))


def truncate_text(text: str, max_tokens: int) -> str:
    """Truncate text to fit within max_tokens."""
    max_chars = int(max_tokens * TOKEN_RATE)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost for a model invocation."""
    rates = COST_PER_TOKEN.get(model, {"input": 0.0, "output": 0.0})
    return (input_tokens * rates["input"]) + (output_tokens * rates["output"])


def format_messages(messages: list[dict[str, Any]]) -> str:
    """Format messages for logging."""
    parts = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = str(msg.get("content", ""))
        parts.append(f"[{role.upper()}] {content[:200]}")
    return "\n".join(parts)


def safe_json_parse(text: str) -> dict[str, Any]:
    """Safely parse JSON from text, handling markdown code fences."""
    cleaned = text.strip()
    if "```json" in cleaned:
        cleaned = cleaned.split("```json")[1].split("```")[0].strip()
    elif "```" in cleaned:
        cleaned = cleaned.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {}


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return f"req_{uuid.uuid4().hex[:16]}"


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"ses_{uuid.uuid4().hex[:16]}"


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary."""
    current = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
