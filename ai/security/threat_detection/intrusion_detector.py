"""Intrusion detection system."""

from __future__ import annotations

import re
import time
import uuid
from typing import Any


class IDSRule:
    def __init__(self, rule_id: str, name: str, pattern: str, severity: str = "medium") -> None:
        self.rule_id = rule_id
        self.name = name
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.severity = severity
        self.enabled = True


class IntrusionDetector:
    def __init__(self) -> None:
        self._rules: dict[str, IDSRule] = {}
        self._alerts: list[dict[str, Any]] = []
        self._blocked_ips: set[str] = set()

    def add_rule(self, rule_id: str, name: str, pattern: str, severity: str = "medium") -> IDSRule:
        rule = IDSRule(rule_id, name, pattern, severity)
        self._rules[rule_id] = rule
        return rule

    def analyze(self, data: str, source_ip: str = "") -> list[dict[str, Any]]:
        findings: list[dict[str, Any]] = []
        for rule in self._rules.values():
            if rule.enabled and rule.pattern.search(data):
                alert = {
                    "alert_id": str(uuid.uuid4())[:8],
                    "rule": rule.name,
                    "severity": rule.severity,
                    "source_ip": source_ip,
                    "timestamp": time.time(),
                    "data_preview": data[:100],
                }
                self._alerts.append(alert)
                findings.append(alert)
                if rule.severity in ("high", "critical"):
                    self._blocked_ips.add(source_ip)
        return findings

    def block_ip(self, ip: str) -> None:
        self._blocked_ips.add(ip)

    def unblock_ip(self, ip: str) -> bool:
        if ip in self._blocked_ips:
            self._blocked_ips.remove(ip)
            return True
        return False

    def is_blocked(self, ip: str) -> bool:
        return ip in self._blocked_ips

    def get_alerts(self, severity: str = "", limit: int = 100) -> list[dict[str, Any]]:
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        return alerts[-limit:]

    def list_rules(self) -> list[str]:
        return list(self._rules.keys())

    def clear_alerts(self) -> int:
        n = len(self._alerts)
        self._alerts.clear()
        return n
