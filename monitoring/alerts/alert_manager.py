from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import Alert, AlertSeverity, AlertStatus


@dataclass
class AlertManagerConfig:
    max_alerts: int = 1000
    auto_resolve_after: float = 300.0  # 5 minutes
    dedup_window: float = 60.0
    aggregation_window: float = 300.0


class AlertManager:
    """Central alert manager that coordinates rule evaluation, dedup, notification."""

    def __init__(self, config: AlertManagerConfig | None = None) -> None:
        self._config = config or AlertManagerConfig()
        self._alerts: dict[str, Alert] = {}
        self._history: list[Alert] = []
        self._rules: list[Any] = []
        self._notifiers: list[Callable[[Alert], None]] = []
        self._on_fire: list[Callable[[Alert], None]] = []
        self._on_resolve: list[Callable[[Alert], None]] = []

    @property
    def config(self) -> AlertManagerConfig:
        return self._config

    def register_rule(self, rule: Any) -> None:
        self._rules.append(rule)

    def add_notifier(self, notifier: Callable[[Alert], None]) -> None:
        self._notifiers.append(notifier)

    def on_alert_fire(self, handler: Callable[[Alert], None]) -> None:
        self._on_fire.append(handler)

    def on_alert_resolve(self, handler: Callable[[Alert], None]) -> None:
        self._on_resolve.append(handler)

    def fire(self, alert: Alert) -> None:
        key = alert.name
        if key in self._alerts:
            existing = self._alerts[key]
            if existing.status == AlertStatus.FIRING:
                return
            existing.status = AlertStatus.FIRING
            existing.fired_at = time.time()
            existing.resolved_at = None
        else:
            self._alerts[key] = alert

        self._history.append(alert)
        self._prune()
        self._notify(alert)
        for handler in self._on_fire:
            try:
                handler(alert)
            except Exception:
                pass

    def resolve(self, alert_name: str) -> None:
        alert = self._alerts.get(alert_name)
        if not alert:
            return
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = time.time()
        for handler in self._on_resolve:
            try:
                handler(alert)
            except Exception:
                pass

    def acknowledge(self, alert_name: str) -> None:
        alert = self._alerts.get(alert_name)
        if alert:
            alert.status = AlertStatus.ACKNOWLEDGED

    def suppress(self, alert_name: str) -> None:
        alert = self._alerts.get(alert_name)
        if alert:
            alert.status = AlertStatus.SUPPRESSED

    def get_active(self) -> list[Alert]:
        return [
            a for a in self._alerts.values()
            if a.status in (AlertStatus.FIRING, AlertStatus.ACKNOWLEDGED)
        ]

    def get_by_name(self, name: str) -> Alert | None:
        return self._alerts.get(name)

    def get_history(self, limit: int = 100) -> list[Alert]:
        return list(self._history[-limit:])

    def evaluate_all(self) -> None:
        for rule in self._rules:
            try:
                rule.evaluate(self)
            except Exception:
                pass
        self._auto_resolve()

    def _auto_resolve(self) -> None:
        now = time.time()
        for alert in list(self._alerts.values()):
            if (
                alert.status == AlertStatus.FIRING
                and self._config.auto_resolve_after > 0
                and (now - alert.fired_at) > self._config.auto_resolve_after
            ):
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = now

    def _notify(self, alert: Alert) -> None:
        for notifier in self._notifiers:
            try:
                notifier(alert)
            except Exception:
                pass

    def _prune(self) -> None:
        if len(self._history) <= self._config.max_alerts:
            return
        excess = len(self._history) - self._config.max_alerts
        self._history = self._history[excess:]
