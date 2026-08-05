"""WorkflowState: deterministic per-node status tracking for a workflow run."""
from __future__ import annotations

from typing import Any, Optional

NODE_STATUSES = ("pending", "running", "succeeded", "failed", "skipped")


class WorkflowState:
    """Tracks statuses, results and errors with an integer tick counter."""

    def __init__(self, node_ids: list[str]) -> None:
        self._statuses: dict[str, str] = {node_id: "pending" for node_id in node_ids}
        self._results: dict[str, Any] = {}
        self._errors: dict[str, str] = {}
        self._ticks: dict[str, int] = {}
        self._tick = 0

    def tick(self) -> int:
        return self._tick

    def _advance(self, node_id: str, status: str) -> None:
        if status not in NODE_STATUSES:
            raise ValueError(f"invalid node status {status!r}; expected one of {NODE_STATUSES}")
        self._tick += 1
        self._statuses[node_id] = status
        self._ticks[node_id] = self._tick

    def mark(self, node_id: str, status: str) -> None:
        self._advance(node_id, status)

    def store(self, node_id: str, result: Any) -> None:
        self._advance(node_id, "succeeded")
        self._results[node_id] = result

    def fail(self, node_id: str, error: str) -> None:
        self._advance(node_id, "failed")
        self._errors[node_id] = error

    def status(self, node_id: str) -> Optional[str]:
        return self._statuses.get(node_id)

    def result(self, node_id: str) -> Any:
        return self._results.get(node_id)

    def error(self, node_id: str) -> Optional[str]:
        return self._errors.get(node_id)

    def results(self) -> dict[str, Any]:
        return dict(self._results)

    def errors(self) -> dict[str, str]:
        return dict(self._errors)

    def executed(self) -> list[str]:
        return sorted(
            node_id for node_id, status in self._statuses.items() if status in ("succeeded", "failed")
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "tick": self._tick,
            "statuses": dict(self._statuses),
            "results": dict(self._results),
            "errors": dict(self._errors),
        }
