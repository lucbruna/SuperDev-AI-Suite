"""
HR Events - Event-driven communication for HR systems.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    CANDIDATE_SCREENED = "recruitment.candidate_screened"
    CANDIDATE_MATCHED = "recruitment.candidate_matched"
    CANDIDATE_SHORTLISTED = "recruitment.candidate_shortlisted"
    INTERVIEW_SCHEDULED = "recruitment.interview_scheduled"
    OFFER_MADE = "recruitment.offer_made"
    OFFER_ACCEPTED = "recruitment.offer_accepted"

    ONBOARDING_STARTED = "onboarding.started"
    ONBOARDING_COMPLETED = "onboarding.completed"
    TRAINING_ASSIGNED = "onboarding.training_assigned"

    REVIEW_SCHEDULED = "performance.review_scheduled"
    REVIEW_COMPLETED = "performance.review_completed"
    GOAL_UPDATED = "performance.goal_updated"
    GOAL_ACHIEVED = "performance.goal_achieved"
    PERFORMANCE_ANOMALY = "performance.anomaly_detected"
    FEEDBACK_SUBMITTED = "performance.feedback_submitted"

    TRAINING_ENROLLED = "learning.training_enrolled"
    TRAINING_COMPLETED = "learning.training_completed"
    SKILL_ACQUIRED = "learning.skill_acquired"
    LEARNING_PATH_UPDATED = "learning.path_updated"

    TALENT_IDENTIFIED = "talent.talent_identified"
    CAREER_PATH_UPDATED = "talent.career_path_updated"
    SUCCESSION_CANDIDATE = "talent.succession_candidate_identified"
    TURNOVER_RISK = "talent.turnover_risk_detected"

    SURVEY_SUBMITTED = "culture.survey_submitted"
    CULTURE_SCORE_CHANGED = "culture.score_changed"
    CULTURE_DECLINE = "culture.decline_detected"
    ENGAGEMENT_WARNING = "culture.engagement_warning"

    WORKFORCE_DEMAND_CHANGED = "workforce.demand_changed"
    SCHEDULE_PUBLISHED = "workforce.schedule_published"
    CAPACITY_WARNING = "workforce.capacity_warning"

    PAYROLL_PROCESSED = "payroll.payroll_processed"
    SALARY_REVIEW = "payroll.salary_review"
    BENEFIT_CHANGED = "payroll.benefit_changed"
    COMPENSATION_ALERT = "payroll.compensation_alert"

    HR_HEALTH_CHANGED = "hr.health_changed"
    HR_ALERT = "hr.alert"


@dataclass
class HREvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 0


EventHandler = Union[Callable[[HREvent], None], Callable[[HREvent], Awaitable[None]]]


class HREventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[HREvent] = []
        self._max_history = 1000
        self._event_counts: Dict[EventType, int] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_global(self, handler: EventHandler) -> None:
        self._global_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False

    async def publish(self, event: HREvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: HREvent) -> None:
        await self._process_event(event)

    async def start_processor(self) -> None:
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())

    async def stop_processor(self) -> None:
        if self._processor_task:
            self._processor_task.cancel()
            try: await self._processor_task
            except asyncio.CancelledError: pass
            self._processor_task = None

    async def _event_processor_loop(self) -> None:
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processor error: {e}")

    async def _process_event(self, event: HREvent) -> None:
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        handlers = list(self._handlers.get(event.event_type, []))
        handlers.extend(self._global_handlers)
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[HREvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)
