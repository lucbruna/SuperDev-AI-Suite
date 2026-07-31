"""DDoS protection."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class DDoSRule:
    def __init__(self, name: str, threshold: int, window_seconds: int, action: str = "block") -> None:
        self.name = name
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.action = action

class DDoSProtection:
    def __init__(self) -> None:
        self._rules: Dict[str, DDoSRule] = {}
        self._request_counts: Dict[str, List[float]] = {}
        self._blocked_sources: Dict[str, Dict[str, Any]] = {}
        self._alerts: List[Dict[str, Any]] = []
    def add_rule(self, name: str, threshold: int, window_seconds: int, action: str = "block") -> DDoSRule:
        rule = DDoSRule(name, threshold, window_seconds, action)
        self._rules[name] = rule
        return rule
    def check_request(self, source_ip: str) -> Dict[str, Any]:
        if source_ip in self._blocked_sources:
            blocked_until = self._blocked_sources[source_ip].get("until", 0)
            if time.time() < blocked_until:
                return {"allowed": False, "reason": "blocked", "until": blocked_until}
            else:
                del self._blocked_sources[source_ip]
        now = time.time()
        requests = self._request_counts.setdefault(source_ip, [])
        for rule in self._rules.values():
            window_start = now - rule.window_seconds
            recent = [r for r in requests if r >= window_start]
            if len(recent) >= rule.threshold:
                self._blocked_sources[source_ip] = {"until": now + rule.window_seconds * 2, "rule": rule.name, "blocked_at": now}
                self._alerts.append({"source": source_ip, "rule": rule.name, "count": len(recent), "threshold": rule.threshold, "timestamp": now})
                return {"allowed": False, "reason": "rate_exceeded", "rule": rule.name}
        requests.append(now)
        return {"allowed": True}
    def block_source(self, source_ip: str, duration_seconds: int = 3600) -> None:
        self._blocked_sources[source_ip] = {"until": time.time() + duration_seconds, "rule": "manual", "blocked_at": time.time()}
    def unblock_source(self, source_ip: str) -> bool:
        if source_ip in self._blocked_sources:
            del self._blocked_sources[source_ip]
            return True
        return False
    def get_blocked(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._blocked_sources)
    def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._alerts[-limit:]
    def list_rules(self) -> List[str]:
        return list(self._rules.keys())
