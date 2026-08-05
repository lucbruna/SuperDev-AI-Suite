"""Aggregated router for the architecture_intelligence module."""
from __future__ import annotations

from fastapi import APIRouter

from modules.architecture_intelligence.api.intelligence_api import router as api_router

router = APIRouter()
router.include_router(api_router)
