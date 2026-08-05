"""Product scene board — product showcase with features."""
from __future__ import annotations

from typing import Any


class ProductScene:
    """Renders a product showcase board."""

    def render(self, scene: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "product",
            "frame": scene.get("frame", 1),
            "product": scene.get("product", ""),
            "features": scene.get("features", []),
            "caption": scene.get("caption", ""),
            "style": "product hero shot",
            "duration": 3.5,
        }


_product_scene: ProductScene | None = None


def get_product_scene() -> ProductScene:
    global _product_scene
    if _product_scene is None:
        _product_scene = ProductScene()
    return _product_scene
