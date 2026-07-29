"""
Content Planner - Plans content strategy
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from uuid import UUID

from marketing_growth_ai.marketing_models import ContentPiece, ContentType


class ContentPlanner:
    """Plans content strategy"""

    def __init__(self):
        self._calendar: Dict[datetime, List[ContentPiece]] = {}

    def create_calendar(
        self,
        themes: List[str],
        frequency: Dict[ContentType, int],
        start_date: datetime = None,
        duration_days: int = 30,
    ) -> List[ContentPiece]:
        start = start_date or datetime.utcnow()
        calendar = []

        for i, theme in enumerate(themes):
            day_offset = (i * duration_days) // len(themes)
            publish_date = start + timedelta(days=day_offset)

            piece = ContentPiece(
                type=ContentType.BLOG_POST,
                title=f"{theme} - Complete Guide",
                body=f"Content about {theme}...",
                keywords=[theme.lower().replace(" ", "-")],
                target_audience="general",
                status="planned",
            )
            calendar.append(piece)

        return calendar

    def get_gaps(self, existing_topics: List[str], target_keywords: List[str]) -> List[str]:
        covered = set(t.lower() for t in existing_topics)
        gaps = [k for k in target_keywords if k.lower() not in covered]
        return gaps

    def optimize_schedule(
        self,
        content: List[ContentPiece],
        audience_data: Dict[str, Any],
    ) -> List[ContentPiece]:
        return content