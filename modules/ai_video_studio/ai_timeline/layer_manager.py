"""Layer manager — z-order and stacking for overlapping timeline elements."""
from __future__ import annotations


from modules.ai_video_studio.core.exceptions import ValidationError


class LayerManager:
    """Tracks layer (z-index) assignment for clips and overlays."""

    def __init__(self) -> None:
        self._layers: dict[str, int] = {}
        self._next_layer = 0

    def assign(self, clip_id: str, layer: int | None = None) -> int:
        """Assign a layer to a clip, returning the assigned z-index."""
        if layer is None:
            layer = self._next_layer
            self._next_layer += 1
        if layer < 0:
            raise ValidationError("Layer cannot be negative", field="layer")
        self._layers[clip_id] = layer
        return layer

    def get(self, clip_id: str) -> int | None:
        return self._layers.get(clip_id)

    def raise_to_top(self, clip_id: str) -> int:
        """Move a clip to the top of the stacking order."""
        top = max(self._layers.values(), default=-1) + 1
        self._layers[clip_id] = top
        self._next_layer = top + 1
        return top

    def send_to_bottom(self, clip_id: str) -> int:
        bottom = min(self._layers.values(), default=0) - 1
        self._layers[clip_id] = bottom
        return bottom

    def reorder(self, ordering: list[str]) -> None:
        """Set explicit z-order; last item is the topmost."""
        seen = set(ordering)
        for clip_id in ordering:
            if clip_id in seen:
                raise ValidationError(f"Duplicate clip '{clip_id}' in ordering", field="ordering")
            seen.add(clip_id)
        for idx, clip_id in enumerate(ordering):
            self._layers[clip_id] = idx
        self._next_layer = len(ordering)

    def ordering(self) -> list[tuple[str, int]]:
        """Return clips sorted bottom-to-top as (id, layer)."""
        return sorted(self._layers.items(), key=lambda kv: kv[1])

    def topmost(self) -> str | None:
        if not self._layers:
            return None
        return max(self._layers.items(), key=lambda kv: kv[1])[0]


_layer_manager: LayerManager | None = None


def get_layer_manager() -> LayerManager:
    global _layer_manager
    if _layer_manager is None:
        _layer_manager = LayerManager()
    return _layer_manager
