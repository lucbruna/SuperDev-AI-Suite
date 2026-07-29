"""
Audit Manager - Comprehensive audit logging and compliance reporting
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from enterprise_ai_core.config import AuditConfig
from enterprise_ai_core.models import AuditEvent, Severity, Event, EventType
from enterprise_ai_core.audit.event_logger import EventLogger
from enterprise_ai_core.audit.compliance_reporter import ComplianceReporter
from enterprise_ai_core.audit.decision_history import DecisionHistory


class AuditManager:
    """Enterprise audit logging and compliance"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config.audit
        self.logger = EventLogger(self.config)
        self.compliance = ComplianceReporter(self.config)
        self.decision_history = DecisionHistory(self.config)
        self._buffer: List[AuditEvent] = []
        self._flush_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        await self.logger.initialize()
        await self.compliance.initialize()
        await self.decision_history.initialize()
        self._flush_task = asyncio.create_task(self._flush_loop())

    async def shutdown(self) -> None:
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        await self.flush()
        await self.logger.shutdown()

    async def log(
        self,
        event_type: str,
        action: str,
        outcome: str = "success",
        actor_id: Optional[UUID] = None,
        actor_type: str = "system",
        resource_type: str = "",
        resource_id: Optional[UUID] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: Severity = Severity.INFO,
        compliance_tags: Optional[List[str]] = None,
    ) -> UUID:
        event = AuditEvent(
            event_type=event_type,
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            compliance_tags=compliance_tags or [],
        )

        self._buffer.append(event)

        if len(self._buffer) >= 100:
            await self.flush()

        await self.orchestrator.publish_event(
            Event(
                type=EventType.AUDIT_LOGGED,
                source_id=event.id,
                source_type="audit",
                payload={
                    "event_type": event_type,
                    "action": action,
                    "outcome": outcome,
                },
                severity=severity,
            )
        )

        return event.id

    async def log_decision(
        self,
        decision_id: UUID,
        context: Dict,
        options: List[Dict],
        selected: Dict,
        rationale: str,
        confidence: float,
        policy_evaluations: List[Dict],
        made_by: Optional[UUID] = None,
    ) -> UUID:
        return await self.decision_history.record(
            decision_id=decision_id,
            context=context,
            options=options,
            selected=selected,
            rationale=rationale,
            confidence=confidence,
            policy_evaluations=policy_evaluations,
            made_by=made_by,
        )

    async def get_audit_trail(
        self,
        actor_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        return await self.logger.query(
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    async def generate_compliance_report(
        self,
        standard: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        return await self.compliance.generate_report(standard, start_date, end_date)

    async def get_decision_history(
        self,
        decision_id: Optional[UUID] = None,
        context_filter: Optional[Dict] = None,
        made_by: Optional[UUID] = None,
        limit: int = 50,
    ) -> List[Dict]:
        return await self.decision_history.query(
            decision_id=decision_id,
            context_filter=context_filter,
            made_by=made_by,
            limit=limit,
        )

    async def flush(self) -> int:
        if not self._buffer:
            return 0

        count = len(self._buffer)
        events = self._buffer[:]
        self._buffer.clear()

        await self.logger.write_batch(events)
        return count

    async def _flush_loop(self) -> None:
        while True:
            await asyncio.sleep(10)
            await self.flush()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "buffer_size": len(self._buffer),
            "logger": self.logger.get_stats(),
            "compliance": self.compliance.get_stats(),
            "decision_history": self.decision_history.get_stats(),
        }