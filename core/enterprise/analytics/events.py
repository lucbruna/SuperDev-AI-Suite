from __future__ import annotations as __

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AnalyticsEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt_{uuid4().hex[:12]}")
    name: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    user_id: str = ""
    org_id: str = ""
    session_id: str = ""
    source: str = "api"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class EventTracker:
    def __init__(self) -> None:
        self._events: List[AnalyticsEvent] = []

    async def track(self, event: AnalyticsEvent) -> str:
        await asyncio.sleep(0.01)
        self._events.append(event)
        return event.id

    async def get_events(
        self,
        name: Optional[str] = None,
        period: Optional[tuple[datetime, datetime]] = None,
        org_id: Optional[str] = None,
    ) -> List[AnalyticsEvent]:
        await asyncio.sleep(0.01)
        results = list(self._events)

        if name:
            results = [e for e in results if e.name == name]
        if period:
            start, end = period
            results = [e for e in results if start <= e.timestamp <= end]
        if org_id:
            results = [e for e in results if e.org_id == org_id]

        return results

    async def get_metrics(
        self,
        name: str,
        metric_type: str = "count",
        period: Optional[tuple[datetime, datetime]] = None,
    ) -> Dict[str, Any]:
        await asyncio.sleep(0.01)
        events = await self.get_events(name, period)

        if not events:
            return {"name": name, "metric_type": metric_type, "count": 0, "period": str(period)}

        if metric_type == "count":
            return {
                "name": name,
                "metric_type": "count",
                "count": len(events),
                "period": str(period),
            }
        elif metric_type == "sum":
            total = sum(
                float(e.properties.get("value", 0))
                for e in events
                if "value" in e.properties
            )
            return {
                "name": name,
                "metric_type": "sum",
                "total": total,
                "count": len(events),
                "period": str(period),
            }
        elif metric_type == "avg":
            values = [
                float(e.properties.get("value", 0))
                for e in events
                if "value" in e.properties
            ]
            avg = sum(values) / len(values) if values else 0.0
            return {
                "name": name,
                "metric_type": "avg",
                "average": avg,
                "count": len(values),
                "period": str(period),
            }

        return {"name": name, "metric_type": metric_type, "count": len(events)}
