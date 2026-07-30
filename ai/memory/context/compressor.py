from __future__ import annotations

from typing import Any, Dict, List, Optional


class ContextCompressor:
    """Compresses context by summarizing and removing redundancy."""

    def __init__(self):
        self._compression_count: int = 0

    @property
    def compression_count(self) -> int:
        return self._compression_count

    def compress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context.get("content", {})
        compressed: Dict[str, Any] = {}
        for key, value in content.items():
            s = str(value)
            if len(s) > 200:
                compressed[key] = s[:100] + "..."
            else:
                compressed[key] = s
        result = dict(context)
        result["content"] = compressed
        result["metadata"] = dict(result.get("metadata", {}))
        result["metadata"]["compressed"] = True
        result["metadata"]["original_size"] = sum(len(str(v)) for v in content.values())
        result["metadata"]["compressed_size"] = sum(len(str(v)) for v in compressed.values())
        self._compression_count += 1
        return result

    def summarize(self, text: str, max_length: int = 200) -> str:
        words = text.split()
        if len(words) <= max_length // 10:
            return text
        return " ".join(words[: max_length // 10]) + "..."

    def compress_values(self, d: Dict[str, Any], max_value_length: int = 100) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in d.items():
            s = str(value)
            result[key] = s[:max_value_length] + "..." if len(s) > max_value_length else s
        self._compression_count += 1
        return result

    def reset(self) -> None:
        self._compression_count = 0
