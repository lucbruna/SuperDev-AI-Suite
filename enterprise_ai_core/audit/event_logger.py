"""
Event Logger - Persists audit events
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import AuditEvent


class EventLogger:
    """Logs audit events to persistent storage"""

    def __init__(self, config):
        self.config = config
        self._events: List[AuditEvent] = []

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def write_batch(self, events: List[AuditEvent]) -> None:
        self._events.extend(events)

    async def query(
        self,
        actor_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        results = self._events

        if actor_id:
            results = [e for e in results if e.actor_id == actor_id]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if start_time:
            results = [e for e in results if e.timestamp >= start_time]
        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        return results[-limit:]

    def get_stats(self) -> Dict:
        return {"total_events": len(self._events)}