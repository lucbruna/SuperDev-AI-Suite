"""Tests for the healing manager and kernel: public operations."""
from __future__ import annotations

from modules.self_healing_engine import HealingManager
from modules.self_healing_engine.tests.helpers import module_smoke


def test_manager_smoke_report() -> None:
    report = module_smoke()
    assert len(report) == 9
    assert all(entry["ok"] for entry in report.values())
    assert all(entry["has_run"] for entry in report.values())


def test_manager_start_stop_state() -> None:
    manager = HealingManager()
    manager.start()
    assert manager.state().running is True

    manager.stop()
    assert manager.state().running is False


def test_manager_diagnose_and_state() -> None:
    manager = HealingManager()
    manager.start()
    health = manager.diagnose()

    assert "score" in health
    state = manager.state()
    assert state.health_score == health["score"]


def test_manager_cycle_with_auto_repair() -> None:
    manager = HealingManager()
    manager.start()
    result = manager.run_cycle(
        {"kind": "dependency", "target": "requirements.txt", "impact_score": 0}
    )

    assert result.pipeline.status == "ok"
    assert manager.state().cycles == 1


def test_manager_cycle_increments_incidents_on_approval() -> None:
    manager = HealingManager()
    manager.start()
    manager.run_cycle(
        {"kind": "dependency", "target": "requirements.txt", "impact_score": 10}
    )

    assert manager.state().active_incidents == 1


def test_manager_tick_runs_cycles() -> None:
    manager = HealingManager()
    manager.start()
    cycles = manager.tick(steps=2)

    assert cycles == 2
    assert manager.state().cycles == 2


def test_manager_plan_execute_approve_rollback() -> None:
    manager = HealingManager()
    plan = manager.plan_repair("dependency", "requirements.txt", impact_score=10)

    assert plan.requires_approval is True
    pending = manager.execute_repair(plan)
    assert pending["status"] == "pending"

    approved = manager.approve_repair(plan)
    assert approved["status"] == "approved"

    # Sem snapshot criado, nada a reverter -> rollback_latest False
    assert manager.rollback_latest() is False
    # Após snapshot, o rollback reverte com sucesso
    manager.snapshots.create("repair", manager.context)
    assert manager.rollback_latest() is True
