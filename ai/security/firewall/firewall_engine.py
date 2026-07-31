"""Firewall engine."""
from __future__ import annotations

import time
from enum import Enum
from typing import Any


class FirewallAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    LOG = "log"
    RATE_LIMIT = "rate_limit"

class FirewallRule:
    def __init__(self, rule_id: str, name: str, source: str = "*", destination: str = "*", port: int = 0, action: FirewallAction = FirewallAction.ALLOW) -> None:
        self.rule_id = rule_id
        self.name = name
        self.source = source
        self.destination = destination
        self.port = port
        self.action = action
        self.priority = 0
        self.enabled = True
        self.created_at = time.time()

class FirewallEngine:
    def __init__(self) -> None:
        self._rules: dict[str, FirewallRule] = {}
        self._traffic_log: list[dict[str, Any]] = []
        self._blocked_ips: set[str] = set()
        self._rate_limits: dict[str, list[float]] = {}
    def add_rule(self, rule_id: str, name: str, source: str = "*", destination: str = "*", port: int = 0, action: FirewallAction = FirewallAction.ALLOW) -> FirewallRule:
        rule = FirewallRule(rule_id, name, source, destination, port, action)
        self._rules[rule_id] = rule
        return rule
    def remove_rule(self, rule_id: str) -> bool:
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    def check_traffic(self, source_ip: str, dest_ip: str, dest_port: int) -> dict[str, Any]:
        if source_ip in self._blocked_ips:
            return {"allowed": False, "action": "blocked_ip", "reason": "IP is blocked"}
        for rule in sorted(self._rules.values(), key=lambda r: r.priority):
            if not rule.enabled:
                continue
            if self._match(rule.source, source_ip) and self._match(rule.destination, dest_ip) and (rule.port == 0 or rule.port == dest_port):
                self._traffic_log.append({"source": source_ip, "dest": dest_ip, "port": dest_port, "action": rule.action.value, "rule": rule.rule_id, "timestamp": time.time()})
                return {"allowed": rule.action == FirewallAction.ALLOW, "action": rule.action.value, "rule": rule.rule_id}
        return {"allowed": True, "action": "default_allow"}
    def _match(self, pattern: str, value: str) -> bool:
        if pattern == "*":
            return True
        return value == pattern
    def block_ip(self, ip: str) -> None:
        self._blocked_ips.add(ip)
    def unblock_ip(self, ip: str) -> bool:
        if ip in self._blocked_ips:
            self._blocked_ips.remove(ip)
            return True
        return False
    def get_rules(self, enabled_only: bool = True) -> list[dict[str, Any]]:
        rules = list(self._rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return [{"id": r.rule_id, "name": r.name, "source": r.source, "dest": r.destination, "port": r.port, "action": r.action.value, "enabled": r.enabled} for r in rules]
    def get_traffic_log(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._traffic_log[-limit:]
    def stats(self) -> dict[str, Any]:
        return {"rules": len(self._rules), "blocked_ips": len(self._blocked_ips), "log_entries": len(self._traffic_log)}
