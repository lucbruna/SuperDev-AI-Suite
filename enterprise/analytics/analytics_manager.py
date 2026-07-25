from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field

from .events import AnalyticsEvent, EventTracker


class Report(BaseModel):
    id: str = Field(default_factory=lambda: f"rpt_{uuid4().hex[:12]}")
    report_type: str
    params: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class DashboardData(BaseModel):
    dashboard_id: str
    period: str
    total_events: int = 0
    unique_users: int = 0
    top_events: List[Dict[str, Any]] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsManager:
    def __init__(self) -> None:
        self._tracker = EventTracker()
        self._reports: Dict[str, Report] = {}

    async def track_event(
        self,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
        user_id: str = "",
        org_id: str = "",
    ) -> str:
        event = AnalyticsEvent(
            name=name,
            properties=properties or {},
            user_id=user_id,
            org_id=org_id,
        )
        return await self._tracker.track(event)

    async def query_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[AnalyticsEvent]:
        filters = filters or {}
        return await self._tracker.get_events(
            name=filters.get("name"),
            period=filters.get("period"),
            org_id=filters.get("org_id"),
        )

    async def get_dashboard_data(
        self,
        dashboard_id: str,
        period: Optional[str] = "30d",
    ) -> DashboardData:
        await asyncio.sleep(0.02)
        now = datetime.utcnow()
        days = int(period.rstrip("d")) if period and period.endswith("d") else 30
        start = now - timedelta(days=days)

        events = await self._tracker.get_events(
            period=(start, now)
        )

        unique_users = len({e.user_id for e in events if e.user_id})
        name_counts: Dict[str, int] = {}
        for e in events:
            name_counts[e.name] = name_counts.get(e.name, 0) + 1

        top = sorted(name_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return DashboardData(
            dashboard_id=dashboard_id,
            period=period,
            total_events=len(events),
            unique_users=unique_users,
            top_events=[
                {"name": name, "count": count} for name, count in top
            ],
            metrics={
                "events_per_day": round(len(events) / max(days, 1), 1),
                "active_users": unique_users,
            },
        )

    async def generate_report(
        self,
        report_type: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Report:
        await asyncio.sleep(0.03)
        params = params or {}
        now = datetime.utcnow()
        days = int(params.get("period", "30").rstrip("d")) if "period" in params else 30
        start = now - timedelta(days=days)

        events = await self._tracker.get_events(
            name=params.get("event_name"),
            period=(start, now),
            org_id=params.get("org_id"),
        )

        report = Report(
            report_type=report_type,
            params=params,
            data={
                "total_events": len(events),
                "period_start": start.isoformat(),
                "period_end": now.isoformat(),
                "events": [e.model_dump() for e in events[:100]],
                "summary": self._summarize_events(events),
            },
        )
        self._reports[report.id] = report
        return report

    def _summarize_events(
        self, events: List[AnalyticsEvent]
    ) -> Dict[str, Any]:
        if not events:
            return {}
        by_name: Dict[str, int] = {}
        for e in events:
            by_name[e.name] = by_name.get(e.name, 0) + 1
        return {
            "total_events": len(events),
            "unique_events": len(by_name),
            "top_events": dict(
                sorted(by_name.items(), key=lambda x: x[1], reverse=True)[:5]
            ),
        }
