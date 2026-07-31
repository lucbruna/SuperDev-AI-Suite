from __future__ import annotations

from typing import Any

PATTERN_DEFINITIONS: dict[str, str] = {
    "microservices": "Decompose application into independently deployable services",
    "event_driven": "Components communicate through events for loose coupling",
    "message_queue": "Asynchronous communication via message broker",
    "caching": "Store frequently accessed data for fast retrieval",
    "plugin": "Extend functionality through pluggable modules",
    "layered": "Organize code into horizontal layers of responsibility",
    "cqrs": "Separate read and write operations into different models",
    "saga": "Manage distributed transactions through compensating actions",
    "circuit_breaker": "Prevent cascading failures by detecting outages",
    "strangler_fig": "Gradually replace legacy systems incrementally",
}


class PatternIdentifier:
    """Identifies architectural patterns from task descriptions."""

    def __init__(self) -> None:
        self._patterns: dict[str, dict[str, Any]] = {
            k: {"pattern": k, "description": v} for k, v in PATTERN_DEFINITIONS.items()
        }

    def identify_from_task(self, task: str) -> list[dict[str, Any]]:
        task_lower = task.lower()
        results: list[dict[str, Any]] = []

        keyword_map: list[tuple[str, str, float]] = [
            ("microservice", "microservices", 0.9),
            ("event", "event_driven", 0.85),
            ("queue", "message_queue", 0.8),
            ("message", "message_queue", 0.75),
            ("cache", "caching", 0.9),
            ("plugin", "plugin", 0.9),
            ("layered", "layered", 0.7),
            ("layer", "layered", 0.65),
            ("cqrs", "cqrs", 0.95),
            ("saga", "saga", 0.9),
            ("circuit", "circuit_breaker", 0.85),
            ("strangler", "strangler_fig", 0.9),
            ("legacy", "strangler_fig", 0.6),
        ]

        for keyword, pattern_name, confidence in keyword_map:
            if keyword in task_lower:
                info = self._patterns.get(pattern_name)
                if info:
                    results.append(
                        {
                            "pattern": pattern_name,
                            "confidence": confidence,
                            "description": info["description"],
                        }
                    )

        if not results:
            results.append(
                {
                    "pattern": "layered",
                    "confidence": 0.5,
                    "description": PATTERN_DEFINITIONS["layered"],
                }
            )

        return results

    @property
    def known_patterns(self) -> list[str]:
        return list(self._patterns.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "known_patterns": self.known_patterns,
            "pattern_count": len(self._patterns),
        }
