from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from ai_platform.routing.smart_router import SmartRouter


class Experiment:
    def __init__(self, name: str, model_a: str, model_b: str, traffic_split: float = 0.5):
        self.id = f"exp_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.model_a = model_a
        self.model_b = model_b
        self.traffic_split = traffic_split
        self.results: list[dict[str, Any]] = []
        self.status = "draft"
        self.created_at = datetime.utcnow().isoformat()

    def start(self) -> None:
        self.status = "running"
        self.started_at = datetime.utcnow().isoformat()

    def stop(self) -> dict[str, Any]:
        self.status = "completed"
        self.completed_at = datetime.utcnow().isoformat()
        return self.get_report()

    def record_result(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        duration_a: float,
        duration_b: float,
        winner: str | None = None,
    ) -> None:
        self.results.append({
            "prompt": prompt,
            "model_a_response": response_a,
            "model_b_response": response_b,
            "duration_a_ms": duration_a,
            "duration_b_ms": duration_b,
            "winner": winner or "tie",
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_report(self) -> dict[str, Any]:
        total = len(self.results)
        if total == 0:
            return {"experiment_id": self.id, "name": self.name, "status": self.status, "total_trials": 0}
        wins_a = sum(1 for r in self.results if r["winner"] == self.model_a)
        wins_b = sum(1 for r in self.results if r["winner"] == self.model_b)
        ties = total - wins_a - wins_b
        avg_duration_a = sum(r["duration_a_ms"] for r in self.results) / total
        avg_duration_b = sum(r["duration_b_ms"] for r in self.results) / total
        return {
            "experiment_id": self.id,
            "name": self.name,
            "status": self.status,
            "model_a": self.model_a,
            "model_b": self.model_b,
            "traffic_split": self.traffic_split,
            "total_trials": total,
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
            "win_rate_a": round(wins_a / total * 100, 1) if total else 0,
            "win_rate_b": round(wins_b / total * 100, 1) if total else 0,
            "avg_duration_a_ms": round(avg_duration_a, 1),
            "avg_duration_b_ms": round(avg_duration_b, 1),
            "winner": self.model_a if wins_a > wins_b else self.model_b if wins_b > wins_a else "tie",
            "created_at": self.created_at,
        }


_experiments: dict[str, Experiment] = {}


def create_experiment(name: str, model_a: str, model_b: str, traffic_split: float = 0.5) -> Experiment:
    exp = Experiment(name, model_a, model_b, traffic_split)
    _experiments[exp.id] = exp
    return exp


def get_experiment(exp_id: str) -> Experiment | None:
    return _experiments.get(exp_id)


def list_experiments() -> list[Experiment]:
    return list(_experiments.values())


def route_by_experiment(experiment_id: str) -> SmartRouter | None:
    exp = _experiments.get(experiment_id)
    if not exp or exp.status != "running":
        return None
    import random
    router = SmartRouter()
    router.set_fixed_model(exp.model_a if random.random() < exp.traffic_split else exp.model_b)
    return router
