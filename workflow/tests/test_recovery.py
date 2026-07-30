from __future__ import annotations

from workflow.recovery.recovery_models import RecoveryPlan, RecoveryStatus
from workflow.recovery.recovery_manager import RecoveryManager
from workflow.recovery.recovery_planner import RecoveryPlanner
from workflow.recovery.recovery_audit import RecoveryAudit
from workflow.recovery.recovery_monitor import RecoveryMonitor


class TestRecovery:
    def test_recovery_plan_defaults(self) -> None:
        plan = RecoveryPlan(target_type="workflow", target_id="w1")
        assert plan.target_type == "workflow"
        assert plan.status == RecoveryStatus.PENDING

    def test_recovery_manager(self) -> None:
        mgr = RecoveryManager()
        plan = RecoveryPlan(target_type="workflow", target_id="w1")
        mgr.register(plan)
        assert mgr.get(plan.id) == plan

    def test_recovery_planner(self) -> None:
        planner = RecoveryPlanner()
        plan = planner.create_plan("workflow", "w1")
        assert len(plan.steps) == 1
        assert plan.steps[0]["action"] == "restore"

    def test_recovery_audit(self) -> None:
        audit = RecoveryAudit()
        audit.log("started", "p1")
        audit.log("completed", "p1")
        history = audit.get_history("p1")
        assert len(history) == 2

    def test_recovery_monitor(self) -> None:
        monitor = RecoveryMonitor()
        plan = RecoveryPlan(target_type="test", target_id="t1")
        from workflow.recovery.recovery_models import RecoveryStatus
        plan.status = RecoveryStatus.COMPLETED
        monitor.record(plan)
        summary = monitor.summary()
        assert summary["total"] == 1
        assert summary["succeeded"] == 1
