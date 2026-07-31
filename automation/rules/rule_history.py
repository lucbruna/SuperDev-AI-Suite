"""History of applied rules."""

from __future__ import annotations

import time
from typing import Any


class RuleHistory:
    """Append-only log of rule evaluations."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(self, rule_id: str, matched: bool, consequence: Any = None) -> None:
        self._records.append({
            "rule_id": rule_id,
            "matched": matched,
            "consequence": consequence,
            "timestamp": time.time(),
        })

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._records[-limit:])

    def count(self, rule_id: str | None = None,
              matched_only: bool = False) -> int:
        count = 0
        for record in self._records:
            if rule_id is not None and record["rule_id"] != rule_id:
                continue
            if matched_only and not record["matched"]:
                continue
            count += 1
        return count

    def clear(self) -> None:
        self._records.clear()
