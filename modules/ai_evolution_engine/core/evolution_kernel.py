"""Deterministic tick kernel driving periodic evolution cycles."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import EVENT_TICK
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.core.evolution_engine import EvolutionEngine


class EvolutionKernel:
    """Advances a tick counter and runs analysis when due.

    Deterministic: no wall-clock; only the injected tick counter drives
    behaviour.
    """

    def __init__(
        self,
        ctx: EvolutionContext,
        engine: EvolutionEngine,
        interval: int | None = None,
    ) -> None:
        self._ctx = ctx
        self._engine = engine
        self._interval = interval or ctx.config.analysis_interval_ticks
        self._ticks = 0

    @property
    def ticks(self) -> int:
        return self._ticks

    def start(self) -> None:
        self._ctx.state.set_running(True)

    def stop(self) -> None:
        self._ctx.state.set_running(False)

    def tick(self, steps: int = 1) -> int:
        """Advance the counter; return number of analysis cycles triggered."""
        if not self._ctx.state.running:
            return 0
        self._ticks += steps
        self._ctx.publish(EVENT_TICK, {"tick": self._ticks})
        cycles = 0
        while self._ticks % self._interval == 0:
            self._engine.run(self._ctx)
            cycles += 1
            self._ticks += 1
        return cycles
