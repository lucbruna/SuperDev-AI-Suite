"""Feedback processing into structured signals (Volume 31)."""

from __future__ import annotations

import re
from typing import Any

_SIGNALS = [
    ("fix", ("erro", "bug", "falha", "corrigir")),
    ("optimize", ("otimiz", "performance", "lent", "melhorar")),
    ("document", ("documentar", "docs", "explicar")),
    ("secure", ("segurança", "seguranca", "auth", "risco")),
    ("test", ("testar", "teste", "cobertura")),
]


class FeedbackProcessor:
    """Converts free-form feedback into typed improvement signals."""

    def __init__(self) -> None:
        self._processed: list[dict[str, Any]] = []

    def process(self, agent_id: str, text: str) -> dict[str, Any]:
        lowered = text.lower()
        kind = "general"
        for signal_kind, keywords in _SIGNALS:
            if any(keyword in lowered for keyword in keywords):
                kind = signal_kind
                break
        entry = {"agent_id": agent_id, "text": text, "kind": kind,
                 "sentences": re.split(r"[.!?]\s*", text.strip())}
        self._processed.append(entry)
        return entry

    def by_kind(self, kind: str) -> list[dict[str, Any]]:
        return [entry for entry in self._processed
                if entry["kind"] == kind]

    def count(self) -> int:
        return len(self._processed)
