"""Test stage."""

from __future__ import annotations

import time
from typing import Any


class TestStage:
    def __init__(self) -> None:
        self._tests: list[dict[str, Any]] = []

    def run_tests(self, project: str, test_type: str = "unit") -> dict[str, Any]:
        import uuid

        run_id = str(uuid.uuid4())[:8]
        test = {
            "run_id": run_id,
            "project": project,
            "type": test_type,
            "total": 150,
            "passed": 148,
            "failed": 2,
            "skipped": 0,
            "status": "completed",
            "duration_seconds": 45.0,
            "timestamp": time.time(),
        }
        self._tests.append(test)
        return test

    def get_results(self, run_id: str) -> dict[str, Any]:
        for t in self._tests:
            if t["run_id"] == run_id:
                return t
        return {"error": "not_found"}

    def list_runs(self, project: str = "", limit: int = 20) -> list[dict[str, Any]]:
        tests = self._tests
        if project:
            tests = [t for t in tests if t["project"] == project]
        return tests[-limit:]

    def count(self) -> int:
        return len(self._tests)
