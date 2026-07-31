"""Trigger engine: facade for the triggers subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.triggers.trigger_evaluator import (TriggerCondition,
                                                   TriggerEvaluator)
from automation.triggers.trigger_history import TriggerHistory
from automation.triggers.trigger_models import (TriggerDefinition,
                                                TriggerEvent)
from automation.triggers.trigger_registry import TriggerRegistry
from automation.triggers.trigger_router import TriggerRouter
from automation.triggers.trigger_scheduler import TriggerScheduler


class TriggerEngine:
    """Registers triggers, routes events, and fires schedules."""

    def __init__(self, registry: TriggerRegistry | None = None,
                 evaluator: TriggerEvaluator | None = None,
                 router: TriggerRouter | None = None,
                 scheduler: TriggerScheduler | None = None,
                 history: TriggerHistory | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self.registry = registry or TriggerRegistry()
        self.evaluator = evaluator or TriggerEvaluator()
        self.history = history or TriggerHistory()
        self.router = router or TriggerRouter(self.registry, self.evaluator,
                                             events, self.history)
        self.scheduler = scheduler or TriggerScheduler(self.router, events)
        self.events = events
        self.metrics = metrics

    # -- registration ------------------------------------------------------
    def register(self, definition: TriggerDefinition) -> TriggerDefinition:
        self.registry.register(definition)
        return definition

    def register_condition(self, trigger_id: str, name: str,
                           condition: dict[str, Any]) -> TriggerDefinition:
        return self.register(TriggerDefinition(
            trigger_id, name, "condition", condition=condition))

    def register_event(self, trigger_id: str, name: str,
                       event_type: str,
                       predicate: Callable[[dict[str, Any]], bool] | None = None,
                       ) -> TriggerDefinition:
        return self.register(TriggerDefinition(
            trigger_id, name, "event",
            predicate=predicate, config={"event_type": event_type}))

    def register_time(self, trigger_id: str, name: str,
                      interval_seconds: float,
                      predicate: Callable[[dict[str, Any]], bool] | None = None,
                      ) -> TriggerDefinition:
        definition = self.register(TriggerDefinition(
            trigger_id, name, "time", predicate=predicate))
        self.scheduler.schedule(trigger_id, interval_seconds)
        return definition

    # -- lifecycle ---------------------------------------------------------
    def enable(self, trigger_id: str) -> bool:
        return self.registry.set_enabled(trigger_id, True)

    def disable(self, trigger_id: str) -> bool:
        return self.registry.set_enabled(trigger_id, False)

    def list(self) -> list[str]:
        return self.registry.list()

    def remove(self, trigger_id: str) -> bool:
        self.scheduler.unschedule(trigger_id)
        return self.registry.remove(trigger_id)

    # -- evaluation --------------------------------------------------------
    def evaluate(self, trigger_id: str,
                 event_data: dict[str, Any] | None = None) -> bool:
        definition = self.registry.get(trigger_id)
        if definition is None:
            return False
        return TriggerCondition(definition, self.evaluator).evaluate(
            {"data": event_data or {}})

    def fire(self, event_type: str,
             data: dict[str, Any] | None = None) -> list[str]:
        """Routes an event and returns the matched trigger ids."""
        matched = self.router.route(TriggerEvent(event_type, data or {}))
        if self.metrics is not None:
            self.metrics.increment("triggers.fired", len(matched))
        return matched

    # -- scheduling --------------------------------------------------------
    def run_due(self, now: float | None = None) -> list[str]:
        return self.scheduler.run_due(now)

    def firing_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)
