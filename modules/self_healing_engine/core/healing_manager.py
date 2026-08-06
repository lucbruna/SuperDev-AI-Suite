"""Lifecycle manager for the Self-Healing Engine.

Owns the runtime wiring (config, context, monitor, planner, executor, kernel)
and provides the public operations the CLI/API call.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config.healing_config import HealingConfig
from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.core.healing_engine import (
    EngineResult,
    HealingEngine,
)
from modules.self_healing_engine.core.healing_kernel import HealingKernel
from modules.self_healing_engine.core.healing_pipeline import HealingPipeline
from modules.self_healing_engine.monitoring.health_monitor import HealthMonitor
from modules.self_healing_engine.recovery.rollback import RollbackManager
from modules.self_healing_engine.recovery.snapshot import SnapshotManager
from modules.self_healing_engine.repair.executor import RepairExecutor
from modules.self_healing_engine.repair.planner import RepairPlan, RepairPlanner


@dataclass(slots=True)
class ManagerState:
    """Public state snapshot reported by the manager."""

    running: bool
    cycles: int
    health_status: str
    health_score: float
    active_incidents: int

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "cycles": self.cycles,
            "health_status": self.health_status,
            "health_score": self.health_score,
            "active_incidents": self.active_incidents,
        }


class HealingManager:
    """High-level operations for a Self-Healing Engine instance."""

    def __init__(
        self,
        config: HealingConfig | None = None,
        context: HealingContext | None = None,
        monitor: HealthMonitor | None = None,
        planner: RepairPlanner | None = None,
        executor: RepairExecutor | None = None,
        snapshots: SnapshotManager | None = None,
        pipeline: HealingPipeline | None = None,
        engine: HealingEngine | None = None,
        kernel: HealingKernel | None = None,
    ) -> None:
        self._config = config or HealingConfig()
        self._ctx = context or HealingContext(config=self._config)
        self._snapshots = snapshots or SnapshotManager(
            self._config.recovery
        )
        self._rollback = RollbackManager(self._snapshots)
        self._monitor = monitor or HealthMonitor()
        self._planner = planner or RepairPlanner()
        self._executor = executor or RepairExecutor()
        self._pipeline = pipeline or HealingPipeline(
            monitor=self._monitor,
            planner=self._planner,
            executor=self._executor,
            snapshots=self._snapshots,
            rollback=self._rollback,
        )
        self._engine = engine or HealingEngine(self._pipeline)
        self._kernel = kernel or HealingKernel(self._ctx, self._engine)

    @property
    def context(self) -> HealingContext:
        return self._ctx

    @property
    def monitor(self) -> HealthMonitor:
        return self._monitor

    @property
    def planner(self) -> RepairPlanner:
        return self._planner

    @property
    def executor(self) -> RepairExecutor:
        return self._executor

    @property
    def snapshots(self) -> SnapshotManager:
        return self._snapshots

    @property
    def rollback(self) -> RollbackManager:
        return self._rollback

    def resolve(self, project_root: str | None = None) -> None:
        self._config.resolve(project_root)

    def start(self) -> None:
        self._kernel.start()

    def stop(self) -> None:
        self._kernel.stop()

    def run_cycle(
        self, incident: dict[str, object] | None = None
    ) -> EngineResult:
        result = self._engine.run(self._ctx, incident)
        if result.pipeline.status == "needs_approval":
            self._ctx.state.set_active_incidents(
                self._ctx.state.active_incidents + 1
            )
        return result

    def tick(self, steps: int = 1) -> int:
        return self._kernel.tick(steps)

    def diagnose(self) -> object:
        return self._monitor.run(self._ctx).to_dict()

    def plan_repair(
        self,
        kind: str,
        target: str,
        impact_score: int = 0,
        description: str = "",
    ) -> RepairPlan:
        return self._planner.plan(
            kind, target, self._ctx, impact_score=impact_score,
            description=description,
        )

    def execute_repair(self, plan: RepairPlan) -> object:
        return self._executor.execute(plan, self._ctx).to_dict()

    def approve_repair(self, plan: RepairPlan) -> object:
        return self._executor.approve(plan, self._ctx).to_dict()

    def rollback_latest(self, kind: str | None = None) -> bool:
        return self._rollback.rollback_latest(self._ctx, kind)

    def state(self) -> ManagerState:
        return ManagerState(
            running=self._ctx.state.running,
            cycles=self._engine.cycles,
            health_status=self._ctx.state.health_status,
            health_score=self._ctx.state.last_health_score,
            active_incidents=self._ctx.state.active_incidents,
        )
