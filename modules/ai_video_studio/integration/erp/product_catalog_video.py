"""Product Catalog Video — highlights products from a catalog list."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class ProductCatalogVideoGenerator:
    """Builds narration scripts introducing catalog products."""

    def generate(self, *, products: list[str] | None = None, brand: str = "Our Brand",
                 voice: str = "default") -> dict[str, Any]:
        products = [p for p in (products or ["Product A", "Product B", "Product C"]) if p]
        title = f"{brand} product catalog"
        scenes = [f"Discover the {brand} catalog: {len(products)} featured products."]
        scenes += [f"Next up: {p} — key features and benefits." for p in products]
        scenes.append("Ask your sales representative for pricing and samples.")
        return build_brief("erp", title, scenes, voice=voice, brand=brand,
                           products=products).to_dict()


_product_catalog_video_generator: ProductCatalogVideoGenerator | None = None


def get_product_catalog_video_generator() -> ProductCatalogVideoGenerator:
    global _product_catalog_video_generator
    if _product_catalog_video_generator is None:
        _product_catalog_video_generator = ProductCatalogVideoGenerator()
    return _product_catalog_video_generator
