"""AIOS Reflection — learning from execution outcomes.

Reflects on a completed run (inputs, output, errors) and produces
lessons, quality notes and suggested improvements. Deterministic.
"""

from __future__ import annotations

import time
from typing import Any

POSITIVE_MARKERS = ("success", "ok", "complete", "good", "passed")


class Reflection:
    """Produce insights from a run outcome."""

    def reflect(self, run: dict[str, Any]) -> dict[str, Any]:
        ok = bool(run.get("ok"))
        error = run.get("error")
        lessons: list[str] = []
        if error:
            lessons.append(f"failure recorded: {error}")
        if not run.get("inputs") and run.get("kind") == "agent":
            lessons.append("missing inputs may have degraded the outcome")
        suggestions: list[str] = []
        if error:
            suggestions.append("add retry with backoff for transient failures")
        if not ok:
            suggestions.append("validate inputs before execution")
        return {
            "ok": True,
            "reflected_at": time.time(),
            "outcome_ok": ok,
            "lessons": lessons,
            "suggestions": suggestions,
            "confidence": 0.5 if not lessons else 0.8,
        }

    def summarize(self, runs: list[dict[str, Any]]) -> dict[str, Any]:
        total = len(runs)
        ok = sum(1 for r in runs if r.get("ok"))
        errors = [r.get("error") for r in runs if r.get("error")]
        return {
            "total": total,
            "ok": ok,
            "failed": total - ok,
            "success_rate": round(ok / total, 4) if total else 0.0,
            "distinct_errors": sorted({str(e) for e in errors if e}),
        }
