"""Compositor engine — node-based compositing with a layered fallback."""
from __future__ import annotations

from .blending_modes import blend, blend_modes
from .compositor_engine import CompositorEngine, NodeGraphError
from .node_editor import NodeEditor, NodeError
from .node_graph import NodeGraph
from .layer_manager import LayerManager

__all__ = [
    "CompositorEngine",
    "NodeGraphError",
    "NodeEditor",
    "NodeError",
    "NodeGraph",
    "LayerManager",
    "blend",
    "blend_modes",
]

engine = CompositorEngine()
