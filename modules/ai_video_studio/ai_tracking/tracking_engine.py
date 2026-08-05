"""Tracking engine — orchestrates trackers across frames."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray


@dataclass
class TrackerResult:
    """A single tracked object's position over time."""

    frames: list[dict[str, Any]] = field(default_factory=list)
    kind: str = "object"
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def centers(self) -> np.ndarray:
        return np.array([[f["x"], f["y"]] for f in self.frames], dtype=np.float64) if self.frames else np.zeros((0, 2))


Tracker = Callable[[NDArray[np.floating]], list[dict[str, Any]]]


class TrackingEngine:
    """Runs a chain of trackers per frame; keeps results keyed by name."""

    def __init__(self) -> None:
        self._trackers: dict[str, Tracker] = {}
        self._results: dict[str, list[dict[str, Any]]] = {}

    def register(self, name: str, tracker: Tracker) -> None:
        self._trackers[name] = tracker

    def track(self, frames: list[NDArray[np.floating]]) -> dict[str, TrackerResult]:
        """Run every registered tracker over ``frames`` and return results."""
        out: dict[str, TrackerResult] = {}
        for name, fn in self._trackers.items():
            detections: list[dict[str, Any]] = []
            for frame in frames:
                detections.extend(fn(frame))
            out[name] = TrackerResult(frames=detections, kind=name)
        self._results = {k: v.frames for k, v in out.items()}
        return out

    def result(self, name: str) -> TrackerResult | None:
        if name in self._results:
            return TrackerResult(frames=self._results[name], kind=name)
        return None

    def names(self) -> list[str]:
        return list(self._trackers)

    def stats(self) -> dict:
        return {"trackers": len(self._trackers), "detections": sum(len(v) for v in self._results.values())}
