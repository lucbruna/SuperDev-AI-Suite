"""Marketplace endpoints — template catalog for the studio storefront."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class TemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str | None = None
    preview: str | None = None
    downloads: int = 0
    rating: float = Field(default=0.0, ge=0.0, le=5.0)
    price: float = 0.0
    featured: bool = False


# Seed catalog — one representative template per studio category.
_templates: dict[str, dict] = {
    "tpl-biz-intro": {
        "id": "tpl-biz-intro", "name": "Modern Business Intro",
        "category": "Business", "description": "Sleek corporate opener with kinetic typography.",
        "downloads": 1240, "rating": 4.8, "price": 0.0, "featured": True,
    },
    "tpl-farm-stories": {
        "id": "tpl-farm-stories", "name": "Farming Stories",
        "category": "Agriculture", "description": "Field-to-table storytelling template with bold captions.",
        "downloads": 860, "rating": 4.6, "price": 12.9,
    },
    "tpl-clinic": {
        "id": "tpl-clinic", "name": "Clinic Explainer",
        "category": "Healthcare", "description": "Clean medical explainer with title-safe text zones.",
        "downloads": 540, "rating": 4.5, "price": 15.0,
    },
    "tpl-course": {
        "id": "tpl-course", "name": "Course Teaser",
        "category": "Education", "description": "Learning-first layout for online course promos.",
        "downloads": 720, "rating": 4.7, "price": 8.5,
    },
    "tpl-finance-report": {
        "id": "tpl-finance-report", "name": "Quarterly Finance Report",
        "category": "Finance", "description": "Data-driven charts and lower-thirds for results videos.",
        "downloads": 410, "rating": 4.4, "price": 19.0,
    },
    "tpl-travel": {
        "id": "tpl-travel", "name": "Destination Highlights",
        "category": "Tourism", "description": "Wide, cinematic pacing for travel reels.",
        "downloads": 610, "rating": 4.6, "price": 9.9,
    },
    "tpl-shop-drops": {
        "id": "tpl-shop-drops", "name": "Shop Drops",
        "category": "Ecommerce", "description": "High-converting product ad with countdown hook.",
        "downloads": 2310, "rating": 4.9, "price": 0.0, "featured": True,
    },
    "tpl-reels": {
        "id": "tpl-reels", "name": "Reels Pack",
        "category": "Social Media", "description": "Nine 9:16 hook-first templates for social feeds.",
        "downloads": 1580, "rating": 4.7, "price": 6.0,
    },
}


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(category: str | None = None, featured: bool | None = None):
    """List the marketplace template catalog (optionally filtered)."""
    items = list(_templates.values())
    if category:
        items = [t for t in items if t["category"] == category]
    if featured is not None:
        items = [t for t in items if t["featured"] == featured]
    return [TemplateResponse(**t) for t in items]


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    if template_id not in _templates:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")
    return TemplateResponse(**_templates[template_id])
