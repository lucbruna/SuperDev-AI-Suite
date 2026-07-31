"""Alerting subsystem generator."""
import os
BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\alerting'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('alert_engine.py', '''"""Alerting subsystem engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class AlertEngine:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
        self._active_alerts: List[Dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def is_running(self) -> bool:
        return self._started
    def add_rule(self, name: str, condition: str, severity: str = "medium") -> Dict[str, Any]:
        rule = {"name": name, "condition": condition, "severity": severity, "enabled": True}
        self._rules.append(rule)
        return rule
    def evaluate_rules(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        triggered = []
        for rule in self._rules:
            if rule.get("enabled"):
                triggered.append({"rule": rule["name"], "severity": rule["severity"], "timestamp": time.time()})
        return triggered
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "rules": len(self._rules), "active_alerts": len(self._active_alerts)}
''')

w('rule_manager.py', '''"""Alert rule management."""
from __future__ import annotations
from typing import Any, Callable, Dict, List
import time

class AlertRule:
    def __init__(self, name: str, condition: Callable[[Dict[str, float]], bool], severity: str = "medium") -> None:
        self.name = name
        self.condition = condition
        self.severity = severity
        self.enabled = True
        self.trigger_count = 0
        self.last_triggered = 0.0

class RuleManager:
    def __init__(self) -> None:
        self._rules: Dict[str, AlertRule] = {}
    def add_rule(self, name: str, condition: Callable[[Dict[str, float]], bool], severity: str = "medium") -> AlertRule:
        rule = AlertRule(name, condition, severity)
        self._rules[name] = rule
        return rule
    def remove_rule(self, name: str) -> bool:
        if name in self._rules:
            del self._rules[name]
            return True
        return False
    def enable_rule(self, name: str) -> bool:
        if name in self._rules:
            self._rules[name].enabled = True
            return True
        return False
    def disable_rule(self, name: str) -> bool:
        if name in self._rules:
            self._rules[name].enabled = False
            return True
        return False
    def evaluate(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        triggered = []
        for rule in self._rules.values():
            if rule.enabled:
                try:
                    if rule.condition(metrics):
                        rule.trigger_count += 1
                        rule.last_triggered = time.time()
                        triggered.append({"name": rule.name, "severity": rule.severity, "trigger_count": rule.trigger_count})
                except Exception:
                    pass
        return triggered
    def list_rules(self) -> List[Dict[str, Any]]:
        return [{"name": r.name, "severity": r.severity, "enabled": r.enabled, "trigger_count": r.trigger_count} for r in self._rules.values()]
''')

w('notification.py', '''"""Alert notifications."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class AlertNotifier:
    def __init__(self) -> None:
        self._channels: Dict[str, Callable[[Dict[str, Any]], bool]] = {}
        self._history: List[Dict[str, Any]] = []
    def add_channel(self, name: str, handler: Callable[[Dict[str, Any]], bool]) -> None:
        self._channels[name] = handler
    def remove_channel(self, name: str) -> bool:
        if name in self._channels:
            del self._channels[name]
            return True
        return False
    def notify(self, alert: Dict[str, Any], channels: List[str] = None) -> Dict[str, bool]:
        target_channels = channels or list(self._channels.keys())
        results = {}
        for ch in target_channels:
            handler = self._channels.get(ch)
            if handler:
                try:
                    results[ch] = handler(alert)
                except Exception:
                    results[ch] = False
            else:
                results[ch] = False
        self._history.append({"alert": alert, "channels": target_channels, "results": results})
        return results
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def list_channels(self) -> List[str]:
        return list(self._channels.keys())
''')

w('escalation.py', '''"""Alert escalation."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class EscalationPolicy:
    def __init__(self, name: str, levels: List[Dict[str, Any]] = None) -> None:
        self.name = name
        self.levels = levels or []
        self.active = True

class EscalationManager:
    def __init__(self) -> None:
        self._policies: Dict[str, EscalationPolicy] = {}
        self._escalations: List[Dict[str, Any]] = []
    def add_policy(self, name: str, levels: List[Dict[str, Any]]) -> EscalationPolicy:
        policy = EscalationPolicy(name, levels)
        self._policies[name] = policy
        return policy
    def remove_policy(self, name: str) -> bool:
        if name in self._policies:
            del self._policies[name]
            return True
        return False
    def escalate(self, alert: Dict[str, Any], policy_name: str) -> Dict[str, Any]:
        policy = self._policies.get(policy_name)
        if not policy:
            return {"error": "policy_not_found"}
        escalation = {"alert": alert, "policy": policy_name, "timestamp": time.time(), "level": 0}
        self._escalations.append(escalation)
        return escalation
    def list_policies(self) -> List[Dict[str, Any]]:
        return [{"name": p.name, "levels": len(p.levels), "active": p.active} for p in self._policies.values()]
    def get_escalations(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._escalations[-limit:]
''')

w('priority.py', '''"""Alert priority."""
from __future__ import annotations
from enum import Enum

class AlertPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class PriorityManager:
    def __init__(self) -> None:
        self._mapping: Dict[str, AlertPriority] = {}
    def set_priority(self, metric_name: str, priority: AlertPriority) -> None:
        self._mapping[metric_name] = priority
    def get_priority(self, metric_name: str) -> AlertPriority:
        return self._mapping.get(metric_name, AlertPriority.LOW)
    def remove_priority(self, metric_name: str) -> bool:
        if metric_name in self._mapping:
            del self._mapping[metric_name]
            return True
        return False
    def list_priorities(self) -> Dict[str, str]:
        return {k: v.value for k, v in self._mapping.items()}
''')

w('suppression.py', '''"""Alert suppression."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class AlertSuppression:
    def __init__(self) -> None:
        self._suppressions: List[Dict[str, Any]] = []
    def suppress(self, alert_type: str, duration_seconds: int = 300, reason: str = "") -> Dict[str, Any]:
        entry = {"type": alert_type, "duration": duration_seconds, "reason": reason, "start_time": time.time(), "end_time": time.time() + duration_seconds}
        self._suppressions.append(entry)
        return entry
    def is_suppressed(self, alert_type: str) -> bool:
        now = time.time()
        return any(s["type"] == alert_type and s["end_time"] > now for s in self._suppressions)
    def unsuppress(self, alert_type: str) -> bool:
        before = len(self._suppressions)
        self._suppressions = [s for s in self._suppressions if s["type"] != alert_type]
        return len(self._suppressions) < before
    def get_active(self) -> List[Dict[str, Any]]:
        now = time.time()
        return [s for s in self._suppressions if s["end_time"] > now]
    def cleanup(self) -> int:
        now = time.time()
        before = len(self._suppressions)
        self._suppressions = [s for s in self._suppressions if s["end_time"] > now]
        return before - len(self._suppressions)
''')

w('history.py', '''"""Alert history."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class AlertHistory:
    def __init__(self, max_entries: int = 1000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def record(self, alert: Dict[str, Any], action: str = "created") -> Dict[str, Any]:
        entry = {"alert": alert, "action": action, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def query(self, alert_type: str = "", action: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._entries
        if alert_type:
            results = [e for e in results if e.get("alert", {}).get("type") == alert_type]
        if action:
            results = [e for e in results if e["action"] == action]
        return results[-limit:]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._entries[-limit:]
''')

w('__init__.py', '''"""Alerting subsystem."""
from .alert_engine import AlertEngine
from .rule_manager import RuleManager
from .notification import AlertNotifier
from .escalation import EscalationManager
from .priority import PriorityManager, AlertPriority
from .suppression import AlertSuppression
from .history import AlertHistory

__all__ = [
    "AlertEngine", "RuleManager", "AlertNotifier", "EscalationManager",
    "PriorityManager", "AlertPriority", "AlertSuppression", "AlertHistory"
]
''')

print("alerting/: 8 files created")
