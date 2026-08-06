"""Deterministic kernel loop for the Digital Twin module.

The kernel is tick-based: callers advance time explicitly with ``tick()``,
so tests never depend on a wall clock. A cycle runs when the configured
interval has elapsed.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
from modules.digital_twin.core.digital_twin_engine import DigitalTwinEngine


@dataclass(slots=True)
class KernelStatus:
    """Snapshot of kernel state."""

    running: bool
    ticks: int
    cycles: int
    interval_seconds: int
    next_cycle_in_ticks: int

    def to_dict(self) -> dict[str, object]:
        return {
            "running": self.running,
            "ticks": self.ticks,
            "cycles": self.cycles,
            "interval_seconds": self.interval_seconds,
            "next_cycle_in_ticks": self.next_cycle_in_ticks,
        }


class DigitalTwinKernel:
    """Ticks forward; runs an engine cycle every ``interval_seconds`` ticks."""

    def __init__(
        self,
        ctx: DigitalTwinContext,
        engine: DigitalTwinEngine | None = None,
        interval_seconds: int | None = None,
    ) -> None:
        self._ctx = ctx
        self._engine = engine or DigitalTwinEngine()
        self._explicit_interval = interval_seconds
        self._ticks = 0
        self._running = False

    @property
    def interval_seconds(self) -> int:
        """Effective interval: explicit value wins, otherwise live from config."""
        if self._explicit_interval is not None:
            return max(1, self._explicit_interval)
        return max(1, self._ctx.config.sync.interval_seconds)

    @property
    def ticks(self) -> int:
        return self._ticks

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def tick(self, steps: int = 1) -> int:
        """Advance the clock by ``steps`` ticks, running cycles as due."""
        cycles_run = 0
        if not self._running:
            self._running = True
        for _ in range(steps):
            self._ticks += 1
            if self._ticks % self.interval_seconds == 0:
                self._engine.run(self._ctx)
                cycles_run += 1
        return cycles_run

    def status(self) -> KernelStatus:
        interval = self.interval_seconds
        next_in = interval - (self._ticks % interval)
        return KernelStatus(
            running=self._running,
            ticks=self._ticks,
            cycles=self._engine.cycles,
            interval_seconds=interval,
            next_cycle_in_ticks=next_in,
        )
