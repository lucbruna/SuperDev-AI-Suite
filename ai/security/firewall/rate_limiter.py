"""Rate limiting."""
from __future__ import annotations

import time
from typing import Any


class RateLimitRule:
    def __init__(self, name: str, max_requests: int, window_seconds: int, scope: str = "global") -> None:
        self.name = name
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.scope = scope
        self.enabled = True

class RateLimiter:
    def __init__(self) -> None:
        self._rules: dict[str, RateLimitRule] = {}
        self._requests: dict[str, list[float]] = {}
        self._violations: list[dict[str, Any]] = []
    def add_rule(self, name: str, max_requests: int, window_seconds: int, scope: str = "global") -> RateLimitRule:
        rule = RateLimitRule(name, max_requests, window_seconds, scope)
        self._rules[name] = rule
        return rule
    def check(self, key: str, rule_name: str = "default") -> dict[str, Any]:
        rule = self._rules.get(rule_name)
        if not rule:
            return {"allowed": True, "remaining": -1}
        now = time.time()
        requests = self._requests.setdefault(key, [])
        window_start = now - rule.window_seconds
        requests[:] = [r for r in requests if r >= window_start]
        if len(requests) >= rule.max_requests:
            self._violations.append({"key": key, "rule": rule_name, "timestamp": now, "count": len(requests)})
            return {"allowed": False, "remaining": 0, "retry_after": rule.window_seconds - (now - requests[0]) if requests else rule.window_seconds}
        requests.append(now)
        return {"allowed": True, "remaining": rule.max_requests - len(requests)}
    def remove_rule(self, name: str) -> bool:
        if name in self._rules:
            del self._rules[name]
            return True
        return False
    def get_violations(self, key: str = "", limit: int = 100) -> list[dict[str, Any]]:
        violations = self._violations
        if key:
            violations = [v for v in violations if v["key"] == key]
        return violations[-limit:]
    def list_rules(self) -> list[str]:
        return list(self._rules.keys())
    def reset_key(self, key: str) -> None:
        self._requests.pop(key, None)
