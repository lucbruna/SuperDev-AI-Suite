"""Inventory Video — stock levels, reorder points and alerts."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class InventoryVideoGenerator:
    """Builds narration scripts from inventory snapshots."""

    def generate(self, *, skus: list[dict[str, Any]] | None = None,
                 voice: str = "default") -> dict[str, Any]:
        skus = skus or [{"sku": "SKU-100", "name": "Widget", "stock": 120, "reorder": 40}]
        low = [s for s in skus if s.get("stock", 0) <= s.get("reorder", 0)]
        title = "Inventory status"
        scenes = [
            f"Inventory check across {len(skus)} SKUs.",
            f"{len(low)} SKU(s) at or below reorder point."
            + (f" Including {low[0]['sku']}." if low else ""),
            "Review warehouse levels and confirm incoming orders.",
            "Replenish items flagged in red to avoid stock-outs.",
        ]
        brief = build_brief("erp", title, scenes, voice=voice).to_dict()
        brief["meta"]["low_stock"] = [s["sku"] for s in low]
        return brief


_inventory_video_generator: InventoryVideoGenerator | None = None


def get_inventory_video_generator() -> InventoryVideoGenerator:
    global _inventory_video_generator
    if _inventory_video_generator is None:
        _inventory_video_generator = InventoryVideoGenerator()
    return _inventory_video_generator
