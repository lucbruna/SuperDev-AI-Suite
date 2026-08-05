"""Compositor preview — quick downscaled renders for interactive scrub."""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from modules.ai_video_studio.editor_common import resize
from .compositor_cache import CompositorCache
from .compositor_engine import CompositorEngine


class CompositorPreview:
    """Renders the graph at a reduced resolution, caching by content hash."""

    def __init__(
        self,
        engine: CompositorEngine | None = None,
        *,
        max_width: int = 640,
        cache_capacity: int = 256,
    ) -> None:
        self._engine = engine or CompositorEngine()
        self._max_width = max_width
        self._cache = CompositorCache(capacity=cache_capacity)

    def render(self, graph: dict[str, tuple[str, dict[str, Any]]] | None = None) -> NDArray[np.floating]:
        """Full-res render, then return a downscaled preview frame.

        When ``graph`` is omitted, the engine's previously set graph is used
        (same behaviour as :meth:`CompositorEngine.evaluate`).
        """
        graph = graph if graph is not None else self._engine.current_graph()
        key = f"g:{len(graph)}:{graph.get('output', list(graph)[-1] if graph else '')}"
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        full = self._engine.evaluate(graph)
        if full.shape[1] > self._max_width:
            full = resize(full, self._max_width, int(full.shape[0] * self._max_width / full.shape[1]))
        self._cache.put(key, full)
        return full

    def clear(self) -> None:
        self._cache.clear()
