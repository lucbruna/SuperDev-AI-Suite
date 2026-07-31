"""Recovery engine (Volume 37, Fase 5)."""

from __future__ import annotations

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (Incident, RestoreJob,
                                         RestoreStatus, Severity)
from devops_engine.devops_protocols import new_id, now
from devops_engine.recovery.failover_manager import FailoverManager
from devops_engine.recovery.incident_manager import IncidentManager
from devops_engine.recovery.runbook_manager import Runbook, RunbookManager


class RecoveryEngine:
    """Facade over restores, incidents, failovers and runbooks."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.incidents = IncidentManager()
        self.failovers = FailoverManager()
        self.runbooks = RunbookManager()

    def restore(self, backup_id: str, target: str = "") -> RestoreJob:
        job = RestoreJob(
            restore_id=new_id("restore"),
            backup_id=backup_id,
            target=target,
            status=RestoreStatus.RESTORING,
            started_at=now(),
        )
        self.events.publish(DevopsEventType.RESTORE_STARTED,
                            {"restore_id": job.restore_id,
                             "backup_id": backup_id})
        job.status = RestoreStatus.SUCCEEDED
        job.finished_at = now()
        self.events.publish(DevopsEventType.RESTORE_SUCCEEDED,
                            {"restore_id": job.restore_id})
        self.metrics.increment("devops.recovery.restores")
        return job

    def raise_incident(self, title: str,
                       severity: Severity = Severity.WARNING,
                       source: str = "") -> Incident:
        incident = self.incidents.raise_incident(title, severity, source)
        self.events.publish(DevopsEventType.INCIDENT_DETECTED,
                            {"incident_id": incident.incident_id,
                             "title": title})
        return incident

    def resolve_incident(self, incident_id: str) -> bool:
        if not self.incidents.resolve(incident_id):
            return False
        self.events.publish(DevopsEventType.INCIDENT_RESOLVED,
                            {"incident_id": incident_id})
        return True

    def activate_failover(self, primary: str, standby: str) -> bool:
        self.failovers.activate(primary, standby)
        self.events.publish(DevopsEventType.FAILOVER_ACTIVATED,
                            {"primary": primary, "standby": standby})
        return True

    def create_runbook(self, name: str,
                       steps: list[str] | None = None,
                       severity: Severity = Severity.WARNING) -> Runbook:
        return self.runbooks.create(name, steps, severity)

    def stats(self) -> dict[str, int]:
        return {
            "incidents": self.incidents.count(),
            "failovers": self.failovers.active_count(),
            "runbooks": self.runbooks.count(),
        }
