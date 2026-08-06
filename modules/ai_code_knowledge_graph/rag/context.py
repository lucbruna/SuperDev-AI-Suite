"""RAG context — format retrieved items into an LLM-friendly context string."""
from __future__ import annotations

from typing import Any


def build_context(results: list[tuple[str, float, dict[str, Any]]], max_chars: int = 4000) -> str:
    """Render top-k retrieval results as a compact, ordered context block."""
    lines: list[str] = []
    used = 0
    for item_id, score, payload in results:
        kind = payload.get("kind", "item")
        name = payload.get("name", "")
        file = payload.get("file", "")
        label = f"{kind}:{name} ({file})" if name and file else (name or file or item_id)
        line = f"- [{score:.3f}] {label}"
        if used + len(line) > max_chars:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines) or "no relevant context found"
