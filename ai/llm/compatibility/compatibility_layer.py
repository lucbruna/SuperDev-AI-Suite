from __future__ import annotations

from typing import Any


class CompatibilityLayer:
    """Resolves provider aliases and converts between message formats."""

    def __init__(self) -> None:
        self._aliases: dict[str, str] = {
            "gpt-4": "openai",
            "gpt-3.5": "openai",
            "claude": "anthropic",
            "gemini": "google",
            "command": "cohere",
            "bedrock": "aws",
        }

    def register_alias(self, provider_name: str, alias: str) -> None:
        self._aliases[alias] = provider_name

    def resolve_alias(self, name: str) -> str:
        return self._aliases.get(name, name)

    def convert_request(self, from_format: str, to_format: str, request: dict[str, Any]) -> dict[str, Any]:
        if from_format == to_format:
            return dict(request)

        if from_format == "openai" and to_format == "standard":
            return {
                "prompt": request.get("messages", [{}])[0].get("content", ""),
                "max_tokens": request.get("max_tokens", 1024),
                "temperature": request.get("temperature", 0.7),
                "model": request.get("model", ""),
            }

        if from_format == "standard" and to_format == "openai":
            return {
                "messages": [{"role": "user", "content": request.get("prompt", "")}],
                "max_tokens": request.get("max_tokens", 1024),
                "temperature": request.get("temperature", 0.7),
                "model": request.get("model", "gpt-4"),
            }

        return dict(request)

    def to_dict(self) -> dict[str, Any]:
        return {
            "aliases": dict(self._aliases),
            "supported_conversions": [
                "openai->standard",
                "standard->openai",
            ],
        }
