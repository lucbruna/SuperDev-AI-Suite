"""Tests for the recovery subpackage (Volume 37, Fase 5)."""

from __future__ import annotations

import pytest

from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (IncidentStatus, RestoreStatus,
                                         Severity)
from devops_engine.recovery import RecoveryEngine, Runbook


@pytest.fixture()
def recovery() -> RecoveryEngine:
    return RecoveryEngine()


class TestIncidentManager:
    def test_lifecycle(self, recovery: RecoveryEngine) -> None:
        incident = recovery.incidents.raise_incident("db down",
                                                     Severity.CRITICAL)
        assert incident.status == IncidentStatus.OPEN
        assert recovery.incidents.investigate(incident.incident_id) is True
        assert incident.status == IncidentStatus.INVESTIGATING
        assert recovery.incidents.mitigate(incident.incident_id) is True
        assert incident.status == IncidentStatus.MITIGATED
        assert recovery.incidents.resolve(incident.incident_id) is True
        assert incident.status == IncidentStatus.RESOLVED

    def test_list_open(self, recovery: RecoveryEngine) -> None:
        resolved = recovery.incidents.raise_incident("done")
        recovery.incidents.resolve(resolved.incident_id)
        recovery.incidents.raise_incident("still open")
        assert len(recovery.incidents.list_open()) == 1


class TestFailoverManager:
    def test_activate_and_failback(self, recovery: RecoveryEngine) -> None:
        assert recovery.failovers.activate("primary", "standby") is True
        assert recovery.failovers.standby_for("primary") == "standby"
        assert recovery.failovers.active_count() == 1
        assert recovery.failovers.failback("primary") is True
        assert recovery.failovers.active_count() == 0


class TestRunbookManager:
    def test_create_and_steps_for(self, recovery: RecoveryEngine) -> None:
        runbook = recovery.create_runbook(
            "critical-recovery", ["check", "failover", "verify"],
            Severity.CRITICAL)
        assert isinstance(runbook, Runbook)
        assert runbook.steps == ["check", "failover", "verify"]
        assert len(recovery.runbooks.steps_for(Severity.CRITICAL)) == 1
        assert recovery.runbooks.count() == 1


class TestRecoveryEngine:
    def test_restore_flow(self, recovery: RecoveryEngine) -> None:
        events = DevopsEvents()
        recovery.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.RESTORE_SUCCEEDED, seen.append)
        job = recovery.restore("b1", target="postgres-new")
        assert job.backup_id == "b1"
        assert job.status == RestoreStatus.SUCCEEDED
        assert len(seen) == 1
        assert recovery.metrics.count("devops.recovery.restores") == 1

    def test_raise_incident_event(self, recovery: RecoveryEngine) -> None:
        events = DevopsEvents()
        recovery.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.INCIDENT_DETECTED, seen.append)
        incident = recovery.raise_incident("api down", Severity.CRITICAL)
        assert incident.status == IncidentStatus.OPEN
        assert len(seen) == 1

    def test_resolve_incident_event(self, recovery: RecoveryEngine) -> None:
        incident = recovery.raise_incident("api down")
        events = DevopsEvents()
        recovery.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.INCIDENT_RESOLVED, seen.append)
        assert recovery.resolve_incident(incident.incident_id) is True
        assert len(seen) == 1

    def test_activate_failover_event(self, recovery: RecoveryEngine) -> None:
        events = DevopsEvents()
        recovery.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.FAILOVER_ACTIVATED, seen.append)
        assert recovery.activate_failover("primary", "standby") is True
        assert len(seen) == 1

    def test_stats(self, recovery: RecoveryEngine) -> None:
        recovery.raise_incident("x")
        recovery.activate_failover("p", "s")
        recovery.create_runbook("rb", ["step"])
        stats = recovery.stats()
        assert stats["incidents"] == 1
        assert stats["failovers"] == 1
        assert stats["runbooks"] == 1
