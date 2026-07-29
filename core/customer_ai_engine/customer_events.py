"""
Customer Events - Event-driven communication for customer systems.
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
    MESSAGE_RECEIVED = "conversation.message_received"
    MESSAGE_SENT = "conversation.message_sent"
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ENDED = "conversation.ended"
    INTENT_IDENTIFIED = "conversation.intent_identified"

    CALL_RECEIVED = "voice.call_received"
    CALL_ENDED = "voice.call_ended"
    CALL_ESCALATED = "voice.call_escalated"

    CHANNEL_SWITCHED = "omnichannel.channel_switched"
    CUSTOMER_IDENTIFIED = "omnichannel.customer_identified"

    LEAD_CAPTURED = "sales.lead_captured"
    LEAD_QUALIFIED = "sales.lead_qualified"
    SALES_OPPORTUNITY = "sales.opportunity_identified"
    DEAL_CLOSED = "sales.deal_closed"
    PURCHASE_MADE = "sales.purchase_made"

    TICKET_CREATED = "support.ticket_created"
    TICKET_UPDATED = "support.ticket_updated"
    TICKET_RESOLVED = "support.ticket_resolved"
    TICKET_ESCALATED = "support.ticket_escalated"

    PROFILE_UPDATED = "personalization.profile_updated"
    BEHAVIOR_DETECTED = "personalization.behavior_detected"
    RECOMMENDATION_SENT = "personalization.recommendation_sent"

    SENTIMENT_NEGATIVE = "sentiment.negative_detected"
    SENTIMENT_POSITIVE = "sentiment.positive_detected"
    SENTIMENT_NEUTRAL = "sentiment.neutral_detected"
    CUSTOMER_ANGRY = "sentiment.customer_angry"
    FEEDBACK_RECEIVED = "sentiment.feedback_received"

    LOYALTY_TIER_CHANGED = "loyalty.tier_changed"
    LOYALTY_RISK = "loyalty.risk_detected"
    REWARD_REDEEMED = "loyalty.reward_redeemed"

    CAMPAIGN_STARTED = "automation.campaign_started"
    CAMPAIGN_SENT = "automation.campaign_sent"
    TRIGGER_ACTIVATED = "automation.trigger_activated"
    WORKFLOW_COMPLETED = "automation.workflow_completed"

    CX_HEALTH_CHANGED = "cx.health_changed"
    CX_ALERT = "cx.alert"


@dataclass
class CustomerEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 0


EventHandler = Union[Callable[[CustomerEvent], None], Callable[[CustomerEvent], Awaitable[None]]]


class CustomerEventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[CustomerEvent] = []
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

    async def publish(self, event: CustomerEvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: CustomerEvent) -> None:
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

    async def _process_event(self, event: CustomerEvent) -> None:
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

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[CustomerEvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)
