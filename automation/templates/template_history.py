"""History of template instantiations."""

from __future__ import annotations

import time
from typing import Any


class TemplateHistory:
    """Append-only log of template usage."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(self, template_id: str, variables: dict[str, Any],
               ok: bool = True, error: str | None = None) -> None:
        self._records.append({
            "template_id": template_id,
            "variables": dict(variables),
            "ok": ok,
            "error": error,
            "timestamp": time.time(),
        })

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._records[-limit:])

    def count(self, template_id: str | None = None, ok: bool | None = None) -> int:
        count = 0
        for record in self._records:
            if template_id is not None and record["template_id"] != template_id:
                continue
            if ok is not None and record["ok"] != ok:
                continue
            count += 1
        return count

    def clear(self) -> None:
        self._records.clear()
