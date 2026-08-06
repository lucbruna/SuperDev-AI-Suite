"""Public API facade: JSON-serializable request handlers over EvolutionManager."""
from __future__ import annotations

from typing import Any

from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager


class EvolutionAPI:
    """Thin, dependency-free facade suitable for REST/CLI/frontend layers."""

    def __init__(self, manager: EvolutionManager) -> None:
        self._manager = manager

    def handle(self, action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        handler = getattr(self, f"action_{action}", None)
        if handler is None:
            return {"ok": False, "error": f"unknown action: {action}"}
        try:
            return handler(payload)
        except Exception as exc:  # noqa: BLE001 - facade boundary
            return {"ok": False, "error": str(exc)}

    def action_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {"ok": True, "state": self._manager.state().to_dict()}

    def action_analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        result = self._manager.analyze()
        return {"ok": True, "analysis": result.to_dict()}

    def action_recommend(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Register a recommendation submitted through the API.

        The payload carries the recommendation fields; the manager records it
        as a draft that then flows through the governance gate.
        """
        from modules.ai_evolution_engine.recommendation.recommendation import (
            Recommendation,
        )

        if not payload:
            return {"ok": False, "error": "recommendation payload required"}
        title = str(payload.get("title", "")).strip()
        if not title:
            return {"ok": False, "error": "recommendation title required"}

        def _score(name: str) -> float:
            try:
                return max(0.0, min(1.0, float(payload.get(name, 0.0))))
            except (TypeError, ValueError):
                return 0.0

        item = Recommendation(
            kind=str(payload.get("kind", "general")),
            title=title,
            description=str(payload.get("description", "")),
            target=str(payload.get("target", "")),
            severity=str(payload.get("severity", "info")),
            impact_score=_score("impact_score"),
            effort_score=_score("effort_score"),
            risk_score=_score("risk_score"),
            evidence=[str(e) for e in payload.get("evidence", [])],
        )
        self._manager.recommend(item)
        return {"ok": True, "recommendation": item.to_dict()}

    def _find(self, recommendation_id: str):
        for item in self._manager.recommendations:
            if item.title == recommendation_id:
                return item
        return None

    def action_approve(self, payload: dict[str, Any]) -> dict[str, Any]:
        rec_id = str(payload.get("recommendation_id", ""))
        item = self._find(rec_id)
        if item is None:
            return {"ok": False, "error": "recommendation not found"}
        self._manager.approve(item)
        return {"ok": True, "recommendation_id": rec_id}

    def action_reject(self, payload: dict[str, Any]) -> dict[str, Any]:
        rec_id = str(payload.get("recommendation_id", ""))
        item = self._find(rec_id)
        if item is None:
            return {"ok": False, "error": "recommendation not found"}
        self._manager.reject(item)
        return {"ok": True, "recommendation_id": rec_id}

    def action_start(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._manager.start()
        return {"ok": True}

    def action_stop(self, payload: dict[str, Any]) -> dict[str, Any]:
        self._manager.stop()
        return {"ok": True}
