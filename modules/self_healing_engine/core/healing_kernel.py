"""Healing kernel: deterministic tick loop over the healing engine."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.automation.tasks import AutomationRunner
from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.core.healing_engine import HealingEngine


@dataclass(slots=True)
class KernelStatus:
    """Public status snapshot reported by the kernel."""

    running: bool
    cycles: int
    ticks: int

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "cycles": self.cycles,
            "ticks": self.ticks,
        }


class HealingKernel:
    """Advances engine cycles and automation tasks on each tick.

    Deterministic: ticks are explicit call steps, never wall-clock driven.
    """

    def __init__(
        self,
        ctx: HealingContext,
        engine: HealingEngine,
        automation: AutomationRunner | None = None,
    ) -> None:
        self._ctx = ctx
        self._engine = engine
        self._automation = automation or AutomationRunner()
        self._ticks = 0

    @property
    def ticks(self) -> int:
        return self._ticks

    def start(self) -> None:
        self._ctx.state.set_running(True)
        self._ctx.publish("kernel.started", {})

    def stop(self) -> None:
        self._ctx.state.set_running(False)
        self._ctx.publish("kernel.stopped", {})

    def tick(
        self, steps: int = 1, incident: dict[str, object] | None = None
    ) -> int:
        """Advance ``steps`` ticks; returns the number of cycles run."""
        cycles_run = 0
        for _ in range(steps):
            if not self._ctx.state.running:
                break
            self._ticks += 1
            self._engine.run(self._ctx, incident)
            self._automation.tick(self._ctx, 1)
            cycles_run += 1
        return cycles_run

    def status(self) -> KernelStatus:
        return KernelStatus(
            running=self._ctx.state.running,
            cycles=self._engine.cycles,
            ticks=self._ticks,
        )
