"""Unit tests: scheduler, memory, governance, monitoring, telemetry, analytics."""
from __future__ import annotations

from modules.super_ai_orchestrator.analytics import OrchestratorAnalytics
from modules.super_ai_orchestrator.config import (
    KernelConfig,
    OrchestratorConfig,
    RoutingConfig,
)
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.governance import GovernanceEngine, GovernancePolicy
from modules.super_ai_orchestrator.kernel import OrchestrationKernel
from modules.super_ai_orchestrator.memory import MemoryStore
from modules.super_ai_orchestrator.monitoring import OrchestratorMonitor
from modules.super_ai_orchestrator.scheduler import PeriodicScheduler
from modules.super_ai_orchestrator.telemetry import Telemetry

from modules.super_ai_orchestrator.tests.helpers import make_api, make_task


# ---------------------------------------------------------------------- #
# Config
# ---------------------------------------------------------------------- #
def test_config_defaults_and_dict_roundtrip():
    config = OrchestratorConfig()
    assert config.default_priority == 5
    assert config.audit_enabled is True
    assert OrchestratorConfig.from_dict(config.to_dict()) == config

    kernel_config = KernelConfig()
    assert kernel_config.slices_per_tick == 3
    assert kernel_config.max_concurrent == 4
    assert KernelConfig.from_dict(kernel_config.to_dict()) == kernel_config

    routing = RoutingConfig()
    assert routing.fallback_owner == "coordinator"
    assert "develop" in routing.capability_map
    assert RoutingConfig.from_dict(routing.to_dict()) == routing


def test_config_resolve_applies_overrides():
    config = OrchestratorConfig().resolve({"default_priority": 9})
    assert config.default_priority == 9
    kernel = KernelConfig().resolve({"slices_per_tick": 7})
    assert kernel.slices_per_tick == 7


# ---------------------------------------------------------------------- #
# PeriodicScheduler
# ---------------------------------------------------------------------- #
def test_scheduler_fires_job_on_interval():
    scheduler = PeriodicScheduler()
    scheduler.add("health", interval_ticks=2, builder=lambda: make_task(title="h"))
    scheduler.add("reports", interval_ticks=3, builder=lambda: make_task(title="r"))
    # tick() returns the tasks fired during that advance.
    assert scheduler.tick(1) == []  # tick 1: nothing due
    assert scheduler.fired == []
    fired = scheduler.tick(1)  # tick 2: health fires
    assert [t.title for t in fired] == ["h"]
    assert [t.title for t in scheduler.fired] == ["h"]
    scheduler.fired.clear()
    fired = scheduler.tick(1)  # tick 3: reports fires
    assert [t.title for t in fired] == ["r"]
    assert [t.title for t in scheduler.fired] == ["r"]


def test_scheduler_submit_fn_receives_fired_tasks():
    received: list = []
    scheduler = PeriodicScheduler(submit_fn=lambda task: received.append(task.title))
    scheduler.add("job", interval_ticks=1, builder=lambda: make_task(title="t"))
    scheduler.tick(2)
    assert received == ["t", "t"]


def test_scheduler_validation_and_control():
    scheduler = PeriodicScheduler()
    try:
        scheduler.add("bad", 0, lambda: make_task())
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    scheduler.add("job", 1, lambda: make_task())
    try:
        scheduler.add("job", 1, lambda: make_task())
        raise AssertionError("expected ValueError")
    except ValueError:
        pass

    assert scheduler.pause("job") is True
    assert scheduler.tick(3) == []
    assert scheduler.resume("job") is True
    assert scheduler.remove("job") is True
    assert scheduler.remove("job") is False
    assert scheduler.pause("missing") is False


# ---------------------------------------------------------------------- #
# MemoryStore
# ---------------------------------------------------------------------- #
def test_memory_store_crud_and_versions():
    memory = MemoryStore()
    entry = memory.remember("goals", "a", {"value": 1})
    assert entry.version == 1
    memory.remember("goals", "a", {"value": 2})
    assert memory.version("goals", "a") == 2
    assert memory.recall("goals", "a") == {"value": 2}
    assert memory.recall("goals", "missing", default="dflt") == "dflt"

    assert memory.namespaces() == ("goals",)
    assert memory.keys("goals") == ("a",)
    assert memory.entries_in("goals") == (("a", {"value": 2}),)
    assert memory.forget("goals", "a") is True
    assert memory.forget("goals", "a") is False


def test_memory_snapshot_restore_roundtrip():
    memory = MemoryStore()
    memory.remember("ns", "k", [1, 2, 3])
    snapshot = memory.snapshot()
    fresh = MemoryStore()
    fresh.restore(snapshot)
    assert fresh.recall("ns", "k") == [1, 2, 3]
    assert fresh.version("ns", "k") == 1


# ---------------------------------------------------------------------- #
# Governance
# ---------------------------------------------------------------------- #
def test_governance_policy_rules_in_order():
    kernel = OrchestrationKernel(KernelConfig(governance_required=True))
    engine = GovernanceEngine(GovernancePolicy())

    monitor = make_task(kind="monitor")
    assert engine.needs_approval(monitor, kernel) == (False, "kind 'monitor' is auto-approved")

    deploy = make_task(kind="deploy")
    needs, reason = engine.needs_approval(deploy, kernel)
    assert needs is True and "always requires approval" in reason

    urgent = make_task(priority=9)
    needs, reason = engine.needs_approval(urgent, kernel)
    assert needs is True and "threshold" in reason

    destructive = make_task(payload={"delete": True})
    needs, reason = engine.needs_approval(destructive, kernel)
    assert needs is True and "destructive" in reason

    gated = make_task(title="plain")
    needs, reason = engine.needs_approval(gated, kernel)
    assert needs is True and "kernel configuration" in reason


def test_governance_without_kernel_gate_auto_approves():
    api = make_api(governance=True)
    task = api.submit(kind="monitor", title="watch")
    assert task["status"] == TaskStatus.QUEUED.value


# ---------------------------------------------------------------------- #
# Monitoring
# ---------------------------------------------------------------------- #
def test_monitor_health_degrades_without_executor():
    # A bare kernel without a registered executor is degraded.
    health = OrchestratorMonitor().health(OrchestrationKernel())
    assert health["status"] == "degraded"
    assert any("no executor" in issue for issue in health["issues"])


def test_monitor_health_healthy_after_execution():
    api = make_api()
    api.kernel.set_executor(lambda context: {"status": "ok"})
    api.submit(kind="develop", title="t", require_approval=False)
    api.tick()
    assert api.health()["status"] == "healthy"


def test_monitor_metrics_success_rate():
    api = make_api()
    api.kernel.set_executor(lambda context: {"status": "ok"})
    api.submit(kind="develop", title="a", require_approval=False)
    api.submit(kind="develop", title="b", require_approval=False)
    api.tick()
    metrics = api.metrics()
    assert metrics["completed"] == 2
    assert metrics["success_rate"] == 1.0
    assert metrics["audit_records"] > 0
    assert metrics["event_records"] > 0


# ---------------------------------------------------------------------- #
# Telemetry
# ---------------------------------------------------------------------- #
def test_telemetry_counters_gauges_and_snapshot():
    telemetry = Telemetry()
    assert telemetry.inc("ticks") == 1
    assert telemetry.inc("ticks") == 2
    assert telemetry.count("ticks") == 2
    telemetry.set("load", 0.5)
    assert telemetry.gauge("load") == 0.5
    snapshot = telemetry.snapshot()
    assert snapshot == {"counters": {"ticks": 2}, "gauges": {"load": 0.5}}
    telemetry.reset()
    assert telemetry.count("ticks") == 0


# ---------------------------------------------------------------------- #
# Analytics
# ---------------------------------------------------------------------- #
def test_analytics_distributions_and_rates():
    api = make_api()
    kernel = api.kernel
    kernel.set_executor(lambda context: {"status": "ok"})
    api.submit(kind="develop", title="ok1", require_approval=False)
    api.submit(kind="analyze", title="ok2", require_approval=False)
    api.tick()

    analytics = OrchestratorAnalytics().analyze(kernel)
    totals = analytics["totals"]
    assert totals["completed"] == 2
    assert totals["success_rate"] == 1.0
    assert totals["rollback_rate"] == 0.0
    assert analytics["by_kind"] == {"analyze": 1, "develop": 1}


def test_analytics_tracks_failures():
    api = make_api()
    kernel = api.kernel
    kernel.set_executor(lambda context: 1 / 0)
    api.submit(kind="develop", title="boom", require_approval=False)
    api.tick()

    analytics = OrchestratorAnalytics().analyze(kernel)
    totals = analytics["totals"]
    assert totals["failed"] == 1
    assert totals["success_rate"] == 0.0
    assert totals["rollback_rate"] == 0.0
    assert analytics["top_failures"][0]["title"] == "boom"


def test_analytics_counts_rolled_back_separately():
    api = make_api()
    kernel = api.kernel
    kernel.set_executor(lambda context: 1 / 0)
    kernel.set_rollback(lambda context: {"rolled_back": True})
    kernel.config.rollback_on_failure = True
    api.submit(kind="develop", title="boom", require_approval=False)
    api.tick()

    totals = OrchestratorAnalytics().analyze(kernel)["totals"]
    # Rollback moves FAILED -> ROLLED_BACK, so 'failed' is zero.
    assert totals["failed"] == 0
    assert totals["rolled_back"] == 1
