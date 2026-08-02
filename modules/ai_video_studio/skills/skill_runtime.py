"""Skill runtime — isolated execution of a skill entrypoint with timeout."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from modules.ai_video_studio.skills.skill_registry import SkillDefinition


@dataclass
class SkillResult:
    skill_id: str
    ok: bool
    output: Any = None
    error: str | None = None
    duration_ms: float = 0.0
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "ok": self.ok,
            "output": self.output,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 3),
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class SkillRuntime:
    """Executes a skill's entrypoint, capturing errors and enforcing timeout."""

    def __init__(self, default_timeout: float = 30.0) -> None:
        self._default_timeout = default_timeout

    async def execute(
        self,
        definition: SkillDefinition,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SkillResult:
        started = datetime.now(UTC)
        if definition.entrypoint is None:
            return SkillResult(
                skill_id=definition.id,
                ok=False,
                error="skill has no entrypoint",
                duration_ms=0.0,
            )
        merged = {**(context or {}), **kwargs}
        timeout = float(
            definition.metadata.get("timeout_s", self._default_timeout)
        )
        # Resolve async-ness through instance __call__: iscoroutinefunction is
        # False for a callable instance even when its __call__ is a coroutine.
        entrypoint = definition.entrypoint
        probe = entrypoint
        if not asyncio.iscoroutinefunction(probe):
            probe = getattr(entrypoint, "__call__", None)  # noqa: B004 — need the bound __call__ itself
        is_async = asyncio.iscoroutinefunction(probe)
        try:
            if is_async:
                output = await asyncio.wait_for(entrypoint(**merged), timeout)
            else:
                output = await asyncio.wait_for(
                    asyncio.to_thread(entrypoint, **merged), timeout
                )
        except TimeoutError:
            return SkillResult(
                skill_id=definition.id,
                ok=False,
                error=f"skill timed out after {timeout}s",
                duration_ms=self._elapsed_ms(started),
                completed_at=datetime.now(UTC).isoformat(),
            )
        except Exception as e:  # noqa: BLE001 — runtime must never leak
            return SkillResult(
                skill_id=definition.id,
                ok=False,
                error=str(e),
                duration_ms=self._elapsed_ms(started),
                completed_at=datetime.now(UTC).isoformat(),
            )
        return SkillResult(
            skill_id=definition.id,
            ok=True,
            output=output,
            duration_ms=self._elapsed_ms(started),
            completed_at=datetime.now(UTC).isoformat(),
        )

    @staticmethod
    def _elapsed_ms(started: datetime) -> float:
        return (datetime.now(UTC) - started).total_seconds() * 1000.0


_runtime: SkillRuntime | None = None


def get_skill_runtime() -> SkillRuntime:
    global _runtime
    if _runtime is None:
        _runtime = SkillRuntime()
    return _runtime
