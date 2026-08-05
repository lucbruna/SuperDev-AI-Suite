"""Body tracker — tracks bodies across a frame stream."""
from __future__ import annotations


import numpy as np


class BodyTracker:
    """Tracks mapped skeletons across frames (simple nearest-neighbor)."""

    def __init__(self, max_tracks: int = 8) -> None:
        self.max_tracks = max_tracks
        self._tracks: dict[str, dict[str, tuple[float, float]]] = {}

    def update(self, skeleton: dict[str, tuple[float, float]],
               track_id: str | None = None) -> str:
        if track_id is None:
            track_id = self._assign(skeleton)
        self._tracks[track_id] = dict(skeleton)
        while len(self._tracks) > self.max_tracks:
            self._tracks.pop(next(iter(self._tracks)))
        return track_id

    def get(self, track_id: str) -> dict[str, tuple[float, float]] | None:
        track = self._tracks.get(track_id)
        return dict(track) if track else None

    def tracks(self) -> list[str]:
        return list(self._tracks)

    def clear(self) -> None:
        self._tracks.clear()

    def _assign(self, skeleton: dict[str, tuple[float, float]]) -> str:
        # Reuse the closest existing track by head position.
        head = skeleton.get("head")
        if head is not None:
            best_id, best_dist = None, float("inf")
            for tid, track in self._tracks.items():
                if "head" in track:
                    d = np.hypot(track["head"][0] - head[0], track["head"][1] - head[1])
                    if d < best_dist:
                        best_id, best_dist = tid, d
            if best_id is not None and best_dist < 0.25:
                return best_id
        return f"track_{len(self._tracks) + 1}"


_body_tracker: BodyTracker | None = None


def get_body_tracker() -> BodyTracker:
    global _body_tracker
    if _body_tracker is None:
        _body_tracker = BodyTracker()
    return _body_tracker
