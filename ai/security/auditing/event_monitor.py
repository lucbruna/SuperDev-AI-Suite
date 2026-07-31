"""Event monitoring."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
import time, uuid

class EventRule:
    def __init__(self, rule_id: str, event_pattern: str, action: str, threshold: int = 1) -> None:
        self.rule_id = rule_id
        self.event_pattern = event_pattern
        self.action = action
        self.threshold = threshold
        self.trigger_count = 0
        self.last_triggered: Optional[float] = None

class EventMonitor:
    def __init__(self) -> None:
        self._events: List[Dict[str, Any]] = []
        self._rules: Dict[str, EventRule] = {}
        self._handlers: Dict[str, Callable[..., Any]] = {}
    def record_event(self, event_type: str, source: str, details: str = "") -> Dict[str, Any]:
        entry = {"event_id": str(uuid.uuid4())[:8], "type": event_type, "source": source, "details": details, "timestamp": time.time()}
        self._events.append(entry)
        self._check_rules(event_type)
        return entry
    def add_rule(self, rule_id: str, event_pattern: str, action: str, threshold: int = 1) -> EventRule:
        rule = EventRule(rule_id, event_pattern, action, threshold)
        self._rules[rule_id] = rule
        return rule
    def register_handler(self, action: str, handler: Callable[..., Any]) -> None:
        self._handlers[action] = handler
    def _check_rules(self, event_type: str) -> None:
        for rule in self._rules.values():
            if rule.event_pattern == event_type or rule.event_pattern == "*":
                rule.trigger_count += 1
                if rule.trigger_count >= rule.threshold:
                    handler = self._handlers.get(rule.action)
                    if handler:
                        handler(event_type, rule)
                    rule.last_triggered = time.time()
                    rule.trigger_count = 0
    def get_events(self, event_type: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        events = self._events
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]
    def clear_events(self) -> int:
        n = len(self._events)
        self._events.clear()
        return n
    def list_rules(self) -> List[str]:
        return list(self._rules.keys())
