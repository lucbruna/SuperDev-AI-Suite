"""
Supply Chain Events - Event-driven communication system.

Provides event definitions, event bus, and event handlers
for inter-subsystem communication within the Supply Chain AI Engine.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    """All supply chain event types."""
    INVENTORY_LOW = "inventory.low"
    INVENTORY_CRITICAL = "inventory.critical"
    INVENTORY_EXCESS = "inventory.excess"
    INVENTORY_UPDATED = "inventory.updated"
    INVENTORY_RESERVED = "inventory.reserved"
    INVENTORY_RELEASED = "inventory.released"

    DEMAND_FORECAST_UPDATED = "demand.forecast_updated"
    DEMAND_SPIKE_DETECTED = "demand.spike_detected"
    DEMAND_DROP_DETECTED = "demand.drop_detected"
    DEMAND_SEASONALITY_CHANGED = "demand.seasonality_changed"
    DEMAND_TREND_CHANGED = "demand.trend_changed"

    PROCUREMENT_ORDER_CREATED = "procurement.order_created"
    PROCUREMENT_ORDER_APPROVED = "procurement.order_approved"
    PROCUREMENT_ORDER_REJECTED = "procurement.order_rejected"
    PROCUREMENT_ORDER_PLACED = "procurement.order_placed"
    PROCUREMENT_ORDER_RECEIVED = "procurement.order_received"
    PROCUREMENT_EMERGENCY = "procurement.emergency_order"

    SUPPLIER_SCORE_CHANGED = "supplier.score_changed"
    SUPPLIER_RISK_DETECTED = "supplier.risk_detected"
    SUPPLIER_PERFORMANCE_DROP = "supplier.performance_drop"
    SUPPLIER_ADDED = "supplier.added"
    SUPPLIER_REMOVED = "supplier.removed"
    SUPPLIER_CONTRACT_EXPIRING = "supplier.contract_expiring"

    LOGISTICS_ROUTE_OPTIMIZED = "logistics.route_optimized"
    LOGISTICS_DELAY = "logistics.delay_detected"
    LOGISTICS_DELIVERY_STARTED = "logistics.delivery_started"
    LOGISTICS_DELIVERY_COMPLETED = "logistics.delivery_completed"
    LOGISTICS_DELIVERY_FAILED = "logistics.delivery_failed"
    LOGISTICS_COST_INCREASE = "logistics.cost_increase"

    WAREHOUSE_CAPACITY_WARNING = "warehouse.capacity_warning"
    WAREHOUSE_CAPACITY_CRITICAL = "warehouse.capacity_critical"
    WAREHOUSE_LAYOUT_OPTIMIZED = "warehouse.layout_optimized"
    WAREHOUSE_RELOCATION = "warehouse.product_relocated"

    FORECAST_RISK_PREDICTED = "forecast.risk_predicted"
    FORECAST_CAPACITY_INSUFFICIENT = "forecast.capacity_insufficient"
    FORECAST_COST_INCREASE = "forecast.cost_increase"

    OPTIMIZATION_COMPLETED = "optimization.completed"
    OPTIMIZATION_SCENARIO_RUN = "optimization.scenario_run"
    OPTIMIZATION_COST_SAVING = "optimization.cost_saving"

    REPLENISHMENT_TRIGGERED = "replenishment.triggered"
    REPLENISHMENT_EXECUTED = "replenishment.executed"
    REPLENISHMENT_AUTO = "replenishment.automatic"

    APPROVAL_REQUIRED = "approval.required"
    APPROVAL_GRANTED = "approval.granted"
    APPROVAL_DENIED = "approval.denied"

    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_CONFIG_CHANGED = "system.config_changed"

    INTEGRATION_ERP_SYNC = "integration.erp_sync"
    INTEGRATION_FINANCIAL_SYNC = "integration.financial_sync"
    INTEGRATION_CUSTOMER_AI_SYNC = "integration.customer_ai_sync"
    INTEGRATION_ROBOTICS_SYNC = "integration.robotics_sync"

    DIGITAL_TWIN_SCENARIO = "digital_twin.scenario_run"
    DIGITAL_TWIN_RESULT = "digital_twin.result_ready"


@dataclass
class SupplyChainEvent:
    """A supply chain domain event."""
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 0

    def __repr__(self) -> str:
        return f"SupplyChainEvent({self.event_type.value}, source={self.source})"


EventHandler = Union[Callable[["SupplyChainEvent"], None], Callable[["SupplyChainEvent"], Awaitable[None]]]


class SupplyChainEventBus:
    """
    Event bus for supply chain domain events.
    
    Supports both sync and async handlers, priority-based
    event processing, and event correlation.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[SupplyChainEvent] = []
        self._max_history = 1000
        self._event_counts: Dict[EventType, int] = {}
        self._processing = False
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None
        
    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to a specific event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type.value}")
        
    def subscribe_global(self, handler: EventHandler) -> None:
        """Subscribe to all events."""
        self._global_handlers.append(handler)
        logger.debug("Global handler subscribed")
        
    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        """Unsubscribe a handler from an event type."""
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False
        
    async def publish(self, event: SupplyChainEvent) -> None:
        """Publish an event to all subscribers."""
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1
        
    async def publish_nowait(self, event: SupplyChainEvent) -> None:
        """Publish event without queuing (process immediately)."""
        await self._process_event(event)
        
    async def start_processor(self) -> None:
        """Start the async event processor."""
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())
        logger.info("Event processor started")
        
    async def stop_processor(self) -> None:
        """Stop the async event processor."""
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
            self._processor_task = None
        logger.info("Event processor stopped")
        
    async def _event_processor_loop(self) -> None:
        """Process events from the queue."""
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processor error: {e}")
                
    async def _process_event(self, event: SupplyChainEvent) -> None:
        """Process a single event."""
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
                
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[SupplyChainEvent]:
        """Get recent event history, optionally filtered by type."""
        if event_type:
            filtered = [e for e in self._event_history if e.event_type == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]
        
    def get_event_count(self, event_type: EventType) -> int:
        """Get count of events published for a type."""
        return self._event_counts.get(event_type, 0)
        
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
        self._event_counts.clear()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "total_events": len(self._event_history),
            "queue_size": self._queue.qsize(),
            "event_counts": {k.value: v for k, v in self._event_counts.items()},
            "subscribers": sum(len(h) for h in self._handlers.values()),
        }