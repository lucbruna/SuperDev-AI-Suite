from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    ROBOT_STATUS_CHANGED = "robot.status_changed"
    ROBOT_TASK_STARTED = "robot.task_started"
    ROBOT_TASK_COMPLETED = "robot.task_completed"
    ROBOT_ERROR = "robot.error"
    ROBOT_BATTERY_LOW = "robot.battery_low"
    ROBOT_COLLISION = "robot.collision"

    MACHINE_STATE_CHANGED = "machine.state_changed"
    MACHINE_ALERT = "machine.alert"
    PRODUCTION_STARTED = "production.started"
    PRODUCTION_COMPLETED = "production.completed"
    PRODUCTION_DEFECT = "production.defect"

    DEVICE_CONNECTED = "device.connected"
    DEVICE_DISCONNECTED = "device.disconnected"
    DEVICE_ERROR = "device.error"
    TELEMETRY_RECEIVED = "telemetry.received"

    SENSOR_ALERT = "sensor.alert"
    SENSOR_CALIBRATION_DUE = "sensor.calibration_due"
    SENSOR_ANOMALY = "sensor.anomaly"

    VISION_INSPECTION_PASS = "vision.inspection_pass"
    VISION_INSPECTION_FAIL = "vision.inspection_fail"
    VISION_DEFECT_DETECTED = "vision.defect_detected"

    COLLISION_RISK = "motion.collision_risk"
    PATH_DEVIATED = "motion.path_deviation"

    SIMULATION_STARTED = "simulation.started"
    SIMULATION_COMPLETED = "simulation.completed"

    TWIN_SYNCED = "twin.synced"
    TWIN_PREDICTION = "twin.prediction"

    MAINTENANCE_DUE = "maintenance.due"
    FAILURE_PREDICTED = "maintenance.failure_predicted"

    SAFETY_ALERT = "safety.alert"
    EMERGENCY_STOP = "safety.emergency_stop"
    SYSTEM_ALERT = "system.alert"


@dataclass
class PhysicalEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    priority: int = 0


EventHandler = Union[Callable[[PhysicalEvent], None], Callable[[PhysicalEvent], Awaitable[None]]]


class PhysicalEventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[PhysicalEvent] = []
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

    async def publish(self, event: PhysicalEvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: PhysicalEvent) -> None:
        await self._process_event(event)

    async def start_processor(self) -> None:
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())

    async def stop_processor(self) -> None:
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
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

    async def _process_event(self, event: PhysicalEvent) -> None:
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

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[PhysicalEvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)
