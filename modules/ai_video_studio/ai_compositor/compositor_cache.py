"""Compositor cache — memoize node outputs across frames.

Keys are content hashes, so unchanged subtrees skip re-evaluation during
interactive playback.
"""
from __future__ import annotations

import hashlib
import threading
from collections import OrderedDict

import numpy as np
from numpy.typing import NDArray


def frame_hash(arr: NDArray[np.floating]) -> str:
    return hashlib.sha1(np.ascontiguousarray(arr).tobytes()).hexdigest()


class CompositorCache:
    """Thread-safe LRU keyed by (node_id, params_hash, input_hashes)."""

    def __init__(self, capacity: int = 512) -> None:
        self._capacity = capacity
        self._data: OrderedDict[str, NDArray[np.floating]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> NDArray[np.floating] | None:
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
                return self._data[key]
        return None

    def put(self, key: str, frame: NDArray[np.floating]) -> None:
        with self._lock:
            self._data[key] = frame
            self._data.move_to_end(key)
            while len(self._data) > self._capacity:
                self._data.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)
