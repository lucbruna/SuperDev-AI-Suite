from __future__ import annotations

from typing import Any


class RegressionEngine:
    """Regression testing — change detection, baseline, comparison, impact analysis."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.regression
        self._baselines: dict[str, dict[str, Any]] = {}
        self._changes: dict[str, list[dict[str, Any]]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- baselines -----------------------------------------------------------

    def set_baseline(self, target: str, snapshot: dict[str, Any]) -> None:
        self._baselines[target] = {
            "snapshot": dict(snapshot),
            "recorded_at": __import__("time").time(),
        }
        self.engine.metrics.increment("regression.baselines", labels={"target": target})

    def get_baseline(self, target: str) -> dict[str, Any] | None:
        baseline = self._baselines.get(target)
        return dict(baseline["snapshot"]) if baseline else None

    def has_baseline(self, target: str) -> bool:
        return target in self._baselines

    # -- change detection ----------------------------------------------------

    def detect_changes(
        self,
        target: str,
        current: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Compare a current snapshot against the stored baseline."""
        baseline = self.get_baseline(target)
        if baseline is None:
            self.set_baseline(target, current)
            return [{"key": "baseline", "change": "created"}]

        changes: list[dict[str, Any]] = []
        for key, new_value in current.items():
            old_value = baseline.get(key, None)
            if old_value != new_value:
                changes.append({
                    "key": key,
                    "from": old_value,
                    "to": new_value,
                    "severity": self._severity(old_value, new_value),
                })
        self._changes.setdefault(target, []).extend(changes)
        self.engine.metrics.increment(
            "regression.changes", labels={"target": target}
        )
        return changes

    @staticmethod
    def _severity(old: Any, new: Any) -> str:
        """Heuristic severity for a value change (numeric drift is high)."""
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
            if old == 0 and new != 0:
                return "high"
            if old != 0 and abs(new - old) / abs(old) > 0.5:
                return "high"
            if abs(new - old) > 0:
                return "medium"
        return "low"

    # -- comparison ----------------------------------------------------------

    def compare(
        self,
        target: str,
        current: dict[str, Any],
    ) -> dict[str, Any]:
        changes = self.detect_changes(target, current)
        high = sum(1 for c in changes if c.get("severity") == "high")
        return {
            "target": target,
            "changes": changes,
            "high_impact": high,
            "regression": high > 0,
            "changed_keys": [c["key"] for c in changes],
        }

    # -- impact analysis -----------------------------------------------------

    def impact_analysis(self, target: str, changed_files: list[str]) -> dict[str, Any]:
        """Estimate the blast radius of changes across known files."""
        related = self.engine.registry.list_suites()
        affected_suites = [
            s.suite_id for s in related.values()
            if s.target and any(f in s.target for f in changed_files)
        ]
        return {
            "target": target,
            "changed_files": list(changed_files),
            "affected_suites": affected_suites,
            "risk": "high" if affected_suites else "low",
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "baselines": len(self._baselines),
            "tracked_targets": len(self._changes),
        }


__all__ = ["RegressionEngine"]
