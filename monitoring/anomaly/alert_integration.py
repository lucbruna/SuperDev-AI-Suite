from __future__ import annotations

from typing import Any

from ..monitoring_models import Alert, AlertSeverity, AlertStatus, AnomalyScore

from .detector import AnomalyDetector


class AnomalyAlertIntegration:
    """Integrates anomaly detection with the alerting system."""

    def __init__(self, detector: AnomalyDetector) -> None:
        self._detector = detector
        self._alert_callbacks: list[Any] = []

    def on_alert(self, callback: Any) -> None:
        self._alert_callbacks.append(callback)

    def score_to_alert(self, score: AnomalyScore) -> Alert:
        severity: AlertSeverity
        if score.deviation > 5.0:
            severity = AlertSeverity.CRITICAL
        elif score.deviation > 3.0:
            severity = AlertSeverity.ERROR
        elif score.deviation > 2.0:
            severity = AlertSeverity.WARN
        else:
            severity = AlertSeverity.INFO

        return Alert(
            name=f"anomaly_{score.metric}",
            severity=severity,
            status=AlertStatus.FIRING,
            message=f"Anomaly detected in {score.metric}: "
                    f"current={score.current:.2f}, baseline={score.baseline:.2f}, "
                    f"deviation={score.deviation:.1f}x",
            labels={"metric": score.metric, "type": "anomaly"},
            value=float(score.score),
            threshold=float(score.baseline),
        )

    def _notification_handler(self, score: AnomalyScore) -> None:
        alert = self.score_to_alert(score)
        for cb in self._alert_callbacks:
            try:
                cb(alert)
            except Exception:
                pass

    def connect(self) -> None:
        self._detector.on_anomaly(self._notification_handler)
