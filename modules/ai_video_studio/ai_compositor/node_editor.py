"""Node editor — high-level API over the compositor graph."""
from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from .compositor_engine import CompositorEngine


class NodeError(RuntimeError):
    """Raised on invalid node editor operations."""


class NodeEditor:
    """Builder-style editor: add_node(...).connect(a, "input", b).render()."""

    def __init__(self, engine: CompositorEngine | None = None) -> None:
        self._engine = engine or CompositorEngine()
        self._graph: dict[str, tuple[str, dict[str, Any]]] = {}
        self._counter = 0

    def add_node(self, name: str, **params: Any) -> str:
        """Register a node op and instantiate it in the graph."""
        self._engine.register(name, _wrap_op(name, params))
        node_id = f"{name}_{self._counter}"
        self._counter += 1
        self._graph[node_id] = (name, params)
        return node_id

    def connect(self, src_id: str, port: str, dst_id: str) -> NodeEditor:
        """Point ``dst``'s ``port`` at ``src``."""
        if dst_id not in self._graph:
            raise NodeError(f"unknown node {dst_id!r}")
        self._graph[dst_id][1][port] = src_id
        return self

    def render(self) -> NDArray[np.floating]:
        return self._engine.evaluate(self._graph)

    @property
    def graph(self) -> dict[str, tuple[str, dict[str, Any]]]:
        return self._graph


def _wrap_op(name: str, params: dict[str, Any]):
    """Build a concrete op closure for generic node names.

    Supports: 'blend' (mode + amount), 'opacity', 'transform' (offset),
    'mask' (keep given mask port), 'passthrough'.
    """
    from .blending_modes import blend as blend_fn

    if name == "blend":

        def op(feeds, cfg):
            if "bottom" not in feeds or "top" not in feeds:
                raise NodeError("blend needs 'bottom' and 'top' inputs")
            return blend_fn(
                feeds["bottom"],
                feeds["top"],
                mode=cfg.get("mode", "normal"),
                amount=float(cfg.get("amount", 1.0)),
            )

        return op
    if name == "opacity":

        def op(feeds, cfg):
            if "input" not in feeds:
                raise NodeError("opacity needs 'input'")
            return feeds["input"] * float(cfg.get("value", 1.0))

        return op
    if name == "mask":

        def op(feeds, cfg):
            if "input" not in feeds or "mask" not in feeds:
                raise NodeError("mask needs 'input' and 'mask'")
            m = feeds["mask"]
            if m.shape != feeds["input"].shape:
                m = np.broadcast_to(m[..., :1], feeds["input"].shape)
            return feeds["input"] * m

        return op
    if name == "transform":

        def op(feeds, cfg):
            if "input" not in feeds:
                raise NodeError("transform needs 'input'")
            img = feeds["input"]
            dx, dy = int(cfg.get("dx", 0)), int(cfg.get("dy", 0))
            out = np.zeros_like(img)
            h, w = img.shape[:2]
            y0, x0 = max(0, dy), max(0, dx)
            y1, x1 = min(h, h + dy), min(w, w + dx)
            out[y0:y1, x0:x1] = img[max(0, -dy) : h + min(0, dy), max(0, -dx) : w + min(0, dx)]
            return out

        return op
    if name == "passthrough":

        def op(feeds, cfg):
            if "input" not in feeds:
                raise NodeError("passthrough needs 'input'")
            return feeds["input"]

        return op
    raise NodeError(f"unknown node {name!r}")
