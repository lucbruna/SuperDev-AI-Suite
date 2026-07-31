"""Routes events to matching triggers."""

from __future__ import annotations

from typing import Any

from automation.automation_events import AutomationEventType
from automation.triggers.trigger_evaluator import TriggerEvaluator
from automation.triggers.trigger_history import TriggerHistory
from automation.triggers.trigger_models import TriggerEvent
from automation.triggers.trigger_registry import TriggerRegistry


class TriggerRouter:
    """Matches incoming events against registered triggers."""

    def __init__(self, registry: TriggerRegistry,
                 evaluator: TriggerEvaluator | None = None,
                 events: Any = None, history: TriggerHistory | None = None) -> None:
        self.registry = registry
        self.evaluator = evaluator or TriggerEvaluator()
        self.events = events
        self.history = history

    def route(self, event: TriggerEvent) -> list[str]:
        """Returns the ids of triggers that matched the event."""
        matched: list[str] = []
        for trigger_id in self.registry.list():
            definition = self.registry.get(trigger_id)
            if definition is None or not definition.enabled:
                continue
            if self._matches(definition, event):
                matched.append(trigger_id)
                if self.history is not None:
                    self.history.record(trigger_id, event)
                if self.events is not None:
                    self.events.publish(AutomationEventType.TRIGGER_FIRED,
                                        {"trigger_id": trigger_id,
                                         "event_type": event.event_type})
        return matched

    def _matches(self, definition: Any, event: TriggerEvent) -> bool:
        if definition.trigger_type == "event":
            expected = definition.config.get("event_type")
            if expected and expected != event.event_type:
                return False
            if definition.predicate:
                return bool(definition.predicate(event.data))
            return True
        if definition.trigger_type == "condition":
            if definition.condition:
                return self.evaluator.evaluate_condition(
                    definition.condition, event.data)
            if definition.predicate:
                return bool(definition.predicate(event.data))
            return False
        # time triggers fire through TriggerScheduler, not events
        return False
