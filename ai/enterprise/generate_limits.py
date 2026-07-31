"""Limits subsystem generator."""
import os

BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\enterprise\limits'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('limit_engine.py', '''"""Limit engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class LimitEngine:
    def __init__(self) -> None:
        self._limits: Dict[str, Dict[str, float]] = {}
        self._usage: Dict[str, Dict[str, float]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def set_limit(self, org_id: str, resource: str, limit: float) -> None:
        self._limits.setdefault(org_id, {})[resource] = limit
    def get_limit(self, org_id: str, resource: str) -> float:
        return self._limits.get(org_id, {}).get(resource, float('inf'))
    def record_usage(self, org_id: str, resource: str, amount: float = 1.0) -> float:
        self._usage.setdefault(org_id, {})
        self._usage[org_id][resource] = self._usage[org_id].get(resource, 0) + amount
        return self._usage[org_id][resource]
    def get_usage(self, org_id: str, resource: str) -> float:
        return self._usage.get(org_id, {}).get(resource, 0.0)
    def is_over_limit(self, org_id: str, resource: str) -> bool:
        return self.get_usage(org_id, resource) > self.get_limit(org_id, resource)
    def remaining(self, org_id: str, resource: str) -> float:
        return max(0, self.get_limit(org_id, resource) - self.get_usage(org_id, resource))
    def usage_percent(self, org_id: str, resource: str) -> float:
        limit = self.get_limit(org_id, resource)
        if limit == 0 or limit == float('inf'):
            return 0.0
        return (self.get_usage(org_id, resource) / limit) * 100
    def list_limits(self, org_id: str) -> Dict[str, float]:
        return dict(self._limits.get(org_id, {}))
    def list_usage(self, org_id: str) -> Dict[str, float]:
        return dict(self._usage.get(org_id, {}))
    def reset_usage(self, org_id: str, resource: str = "") -> float:
        if resource:
            old = self._usage.get(org_id, {}).get(resource, 0)
            self._usage.get(org_id, {}).pop(resource, None)
            return old
        return sum(self._usage.pop(org_id, {}).values())
    def is_running(self) -> bool:
        return self._started
''')

w('quota_manager.py', '''"""Quota manager."""
from __future__ import annotations
from typing import Any, Dict

class QuotaManager:
    def __init__(self) -> None:
        self._quotas: Dict[str, Dict[str, float]] = {}
        self._current: Dict[str, Dict[str, float]] = {}
    def set_quota(self, org_id: str, metric: str, limit: float) -> None:
        self._quotas.setdefault(org_id, {})[metric] = limit
    def get_quota(self, org_id: str, metric: str) -> float:
        return self._quotas.get(org_id, {}).get(metric, 0.0)
    def consume(self, org_id: str, metric: str, amount: float) -> float:
        self._current.setdefault(org_id, {})
        self._current[org_id][metric] = self._current[org_id].get(metric, 0) + amount
        return self._current[org_id][metric]
    def get_consumed(self, org_id: str, metric: str) -> float:
        return self._current.get(org_id, {}).get(metric, 0.0)
    def available(self, org_id: str, metric: str) -> float:
        return max(0, self.get_quota(org_id, metric) - self.get_consumed(org_id, metric))
    def is_exceeded(self, org_id: str, metric: str) -> bool:
        return self.get_consumed(org_id, metric) >= self.get_quota(org_id, metric)
    def percent_used(self, org_id: str, metric: str) -> float:
        quota = self.get_quota(org_id, metric)
        if quota == 0:
            return 0.0
        return (self.get_consumed(org_id, metric) / quota) * 100
    def reset(self, org_id: str, metric: str = "") -> float:
        if metric:
            old = self._current.get(org_id, {}).get(metric, 0)
            self._current.get(org_id, {}).pop(metric, None)
            return old
        return sum(self._current.pop(org_id, {}).values())
    def list_quotas(self, org_id: str) -> Dict[str, Dict[str, float]]:
        return {"limits": dict(self._quotas.get(org_id, {})), "usage": dict(self._current.get(org_id, {}))}
''')

w('enforcement.py', '''"""Limit enforcement."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class LimitEnforcer:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._violations: List[Dict[str, Any]] = []
    def add_policy(self, resource: str, limit: float, action: str = "block", callback: Callable = None) -> None:
        self._policies[resource] = {"limit": limit, "action": action, "callback": callback}
    def check(self, org_id: str, resource: str, current_usage: float) -> Dict[str, Any]:
        policy = self._policies.get(resource)
        if not policy:
            return {"allowed": True, "reason": "no_policy"}
        if current_usage >= policy["limit"]:
            violation = {"org_id": org_id, "resource": resource, "usage": current_usage, "limit": policy["limit"], "action": policy["action"]}
            self._violations.append(violation)
            if policy.get("callback"):
                try:
                    policy["callback"](violation)
                except Exception:
                    pass
            return {"allowed": False, "reason": "limit_exceeded", "action": policy["action"]}
        return {"allowed": True, "reason": "within_limit"}
    def get_violations(self, org_id: str = "", resource: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._violations
        if org_id:
            results = [v for v in results if v["org_id"] == org_id]
        if resource:
            results = [v for v in results if v["resource"] == resource]
        return results[-limit:]
    def list_policies(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"limit": v["limit"], "action": v["action"]} for k, v in self._policies.items()}
    def remove_policy(self, resource: str) -> bool:
        if resource in self._policies:
            del self._policies[resource]
            return True
        return False
    def clear_violations(self) -> int:
        n = len(self._violations)
        self._violations.clear()
        return n
''')

w('alerts.py', '''"""Limit alerts."""
from __future__ import annotations
from typing import Any, Callable, Dict, List

class LimitAlerts:
    def __init__(self) -> None:
        self._thresholds: Dict[str, Dict[str, float]] = {}
        self._handlers: Dict[str, Callable] = {}
        self._alerts: List[Dict[str, Any]] = []
    def set_threshold(self, resource: str, warning: float = 80.0, critical: float = 95.0) -> None:
        self._thresholds[resource] = {"warning": warning, "critical": critical}
    def set_handler(self, resource: str, handler: Callable) -> None:
        self._handlers[resource] = handler
    def check(self, org_id: str, resource: str, usage_percent: float) -> str:
        threshold = self._thresholds.get(resource, {"warning": 80, "critical": 95})
        if usage_percent >= threshold["critical"]:
            alert = {"org_id": org_id, "resource": resource, "level": "critical", "percent": usage_percent}
            self._alerts.append(alert)
            handler = self._handlers.get(resource)
            if handler:
                try:
                    handler(alert)
                except Exception:
                    pass
            return "critical"
        if usage_percent >= threshold["warning"]:
            alert = {"org_id": org_id, "resource": resource, "level": "warning", "percent": usage_percent}
            self._alerts.append(alert)
            return "warning"
        return "ok"
    def get_alerts(self, org_id: str = "", resource: str = "", level: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        results = self._alerts
        if org_id:
            results = [a for a in results if a["org_id"] == org_id]
        if resource:
            results = [a for a in results if a["resource"] == resource]
        if level:
            results = [a for a in results if a["level"] == level]
        return results[-limit:]
    def list_thresholds(self) -> Dict[str, Dict[str, float]]:
        return dict(self._thresholds)
    def clear_alerts(self) -> int:
        n = len(self._alerts)
        self._alerts.clear()
        return n
''')

w('policies.py', '''"""Limit policies."""
from __future__ import annotations
from typing import Any, Dict, List

class LimitPolicies:
    def __init__(self) -> None:
        self._policies: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, resource: str, limit: float, period: str = "monthly", action: str = "block") -> Dict[str, Any]:
        policy = {"name": name, "resource": resource, "limit": limit, "period": period, "action": action, "active": True}
        self._policies[name] = policy
        return policy
    def get(self, name: str) -> Dict[str, Any]:
        return self._policies.get(name, {})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._policies.values())
    def list_by_resource(self, resource: str) -> List[Dict[str, Any]]:
        return [p for p in self._policies.values() if p["resource"] == resource]
    def deactivate(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = False
            return True
        return False
    def activate(self, name: str) -> bool:
        if name in self._policies:
            self._policies[name]["active"] = True
            return True
        return False
    def delete(self, name: str) -> bool:
        if name in self._policies:
            del self._policies[name]
            return True
        return False
    def evaluate(self, resource: str, usage: float) -> Dict[str, Any]:
        for policy in self._policies.values():
            if policy["resource"] == resource and policy["active"]:
                if usage >= policy["limit"]:
                    return {"policy": policy["name"], "exceeded": True, "action": policy["action"]}
        return {"exceeded": False}
''')

w('__init__.py', '''"""Limits subsystem."""
from .limit_engine import LimitEngine
from .quota_manager import QuotaManager
from .enforcement import LimitEnforcer
from .alerts import LimitAlerts
from .policies import LimitPolicies

__all__ = [
    "LimitEngine", "QuotaManager", "LimitEnforcer", "LimitAlerts", "LimitPolicies"
]
''')

print("limits/: 6 files created")
