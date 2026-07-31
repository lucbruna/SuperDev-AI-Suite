"""Metrics collector."""

from datetime import datetime

from .models import (
    MetricAlert,
    MetricDefinition,
    MetricStatus,
    MetricSummary,
    MetricThreshold,
    MetricValue,
)


class MetricsCollector:
    def __init__(self):
        self._definitions: dict[str, MetricDefinition] = {}
        self._values: dict[str, list[MetricValue]] = {}
        self._thresholds: dict[str, MetricThreshold] = {}
        self._alerts: list[MetricAlert] = []

    def register_metric(self, definition: MetricDefinition) -> None:
        self._definitions[definition.name] = definition
        if definition.name not in self._values:
            self._values[definition.name] = []

    def record(self, metric_value: MetricValue) -> MetricAlert | None:
        if metric_value.name not in self._definitions:
            self.register_metric(MetricDefinition(name=metric_value.name, metric_type="dynamic"))
        self._values.setdefault(metric_value.name, []).append(metric_value)
        threshold = self._thresholds.get(metric_value.name)
        if threshold:
            return self._check_threshold(metric_value, threshold)
        return None

    def record_batch(self, values: list[MetricValue]) -> list[MetricAlert]:
        alerts = []
        for v in values:
            a = self.record(v)
            if a:
                alerts.append(a)
        return alerts

    def set_threshold(self, threshold: MetricThreshold) -> None:
        self._thresholds[threshold.metric_name] = threshold

    def get_values(self, name: str, since: datetime | None = None) -> list[MetricValue]:
        values = self._values.get(name, [])
        if since:
            values = [v for v in values if v.timestamp >= since]
        return values

    def get_summary(self, name: str, since: datetime | None = None) -> MetricSummary:
        values = self.get_values(name, since)
        if not values:
            return MetricSummary(name=name)
        vals = [v.value for v in values]
        status = MetricStatus.HEALTHY
        threshold = self._thresholds.get(name)
        if threshold:
            if threshold.critical_max is not None and max(vals) > threshold.critical_max:
                status = MetricStatus.CRITICAL
            elif threshold.warning_max is not None and max(vals) > threshold.warning_max:
                status = MetricStatus.WARNING
        return MetricSummary(
            name=name,
            count=len(vals),
            sum=sum(vals),
            avg=sum(vals) / len(vals),
            min_val=min(vals),
            max_val=max(vals),
            latest=vals[-1],
            status=status,
        )

    def get_alerts(self, status: MetricStatus | None = None) -> list[MetricAlert]:
        if status:
            return [a for a in self._alerts if a.status == status]
        return list(self._alerts)

    def _check_threshold(self, mv: MetricValue, t: MetricThreshold) -> MetricAlert | None:
        status = MetricStatus.HEALTHY
        msg = ""
        if t.critical_max is not None and mv.value > t.critical_max:
            status = MetricStatus.CRITICAL
            msg = f"Value {mv.value} exceeds critical max {t.critical_max}"
        elif t.critical_min is not None and mv.value < t.critical_min:
            status = MetricStatus.CRITICAL
            msg = f"Value {mv.value} below critical min {t.critical_min}"
        elif t.warning_max is not None and mv.value > t.warning_max:
            status = MetricStatus.WARNING
            msg = f"Value {mv.value} exceeds warning max {t.warning_max}"
        elif t.warning_min is not None and mv.value < t.warning_min:
            status = MetricStatus.WARNING
            msg = f"Value {mv.value} below warning min {t.warning_min}"
        if status != MetricStatus.HEALTHY:
            alert = MetricAlert(
                alert_id=f"alert_{mv.name}_{mv.timestamp.timestamp()}",
                metric_name=mv.name,
                status=status,
                current_value=mv.value,
                threshold=t,
                message=msg,
                timestamp=mv.timestamp,
            )
            self._alerts.append(alert)
            return alert
        return None
