"""Analytics endpoints — audience performance summaries."""
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnalyticsSummaryResponse(BaseModel):
    views: int
    watchTime: int
    likes: int
    comments: int
    shares: int
    subscribers: int


# Audience summary for published studio content (in-memory store).
_summary: dict = {
    "views": 1_240_000,
    "watchTime": 3_620_000,
    "likes": 84_200,
    "comments": 12_400,
    "shares": 31_800,
    "subscribers": 156_000,
}


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_summary():
    """Return the aggregate audience summary for published content."""
    return AnalyticsSummaryResponse(**_summary)
