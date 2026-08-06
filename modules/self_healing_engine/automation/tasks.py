"""Maintenance and validation tasks driven by a deterministic tick counter."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field

from modules.self_healing_engine.config.automation_config import AutomationConfig
from modules.self_healing_engine.config.security_policy import SecurityPolicy
from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.validation.validators import ValidatorRunner

_MAX_CLEANUP_CANDIDATES = 200
_MAX_VALIDATION_FILES = 20


class AutomationTask(ABC):
    """Base class for a periodic automation task."""

    name: str = "task"
    interval: int = 1
    last_run: int = 0

    @abstractmethod
    def run(self, ctx: HealingContext) -> None:
        raise NotImplementedError


class CleanupTask(AutomationTask):
    """Collects __pycache__ directories; removes them only if allowed."""

    name = "cleanup"
    interval = 12

    def __init__(
        self, security_policy: SecurityPolicy | None = None
    ) -> None:
        self._security_policy = security_policy or SecurityPolicy()

    def run(self, ctx: HealingContext) -> None:
        candidates: list[str] = []
        root = ctx.config.project_root
        if root:
            for dirpath, dirnames, _filenames in os.walk(root):
                if len(candidates) >= _MAX_CLEANUP_CANDIDATES:
                    break
                if self._security_policy.is_path_protected(dirpath):
                    dirnames[:] = []
                    continue
                kept: list[str] = []
                for name in dirnames:
                    if name == "__pycache__":
                        candidates.append(os.path.join(dirpath, name))
                    else:
                        kept.append(name)
                dirnames[:] = kept
        removed = False
        if self._security_policy.allow_destructive_operations:
            for candidate in candidates:
                try:
                    os.rmdir(candidate)
                    removed = True
                except OSError:
                    pass
        ctx.publish(
            "automation.cleanup",
            {
                "candidates": candidates,
                "candidate_count": len(candidates),
                "removed": removed,
            },
        )


class ContinuousValidationTask(AutomationTask):
    """Runs validators over a bounded sample of project Python files."""

    name = "continuous_validation"
    interval = 1

    def __init__(self, runner: ValidatorRunner | None = None) -> None:
        self._runner = runner or ValidatorRunner()

    def run(self, ctx: HealingContext) -> None:
        targets: list[str] = []
        root = ctx.config.project_root
        if root:
            for dirpath, dirnames, filenames in os.walk(root):
                if len(targets) >= _MAX_VALIDATION_FILES:
                    break
                dirnames[:] = [
                    d for d in dirnames if d not in ("__pycache__", ".superdev", ".git")
                ]
                for filename in filenames:
                    if len(targets) >= _MAX_VALIDATION_FILES:
                        break
                    if filename.endswith(".py"):
                        targets.append(os.path.join(dirpath, filename))
        passed = 0
        failed = 0
        for target in targets:
            results = self._runner.run(target, ctx)
            passed += sum(1 for r in results if r.passed)
            failed += len(results) - sum(1 for r in results if r.passed)
        ctx.publish(
            "automation.validation",
            {"targets": len(targets), "passed": passed, "failed": failed},
        )


class OptimizationTask(AutomationTask):
    """Placeholder deterministic optimization task."""

    name = "optimization"
    interval = 48

    def run(self, ctx: HealingContext) -> None:
        ctx.publish(
            "automation.optimization",
            {"optimized": 0, "message": "no optimization configured"},
        )


class AutomationRunner:
    """Advances a tick counter and runs due tasks deterministically."""

    def __init__(
        self,
        automation_config: AutomationConfig | None = None,
        tasks: Sequence[AutomationTask] | None = None,
    ) -> None:
        self._config = automation_config or AutomationConfig()
        self._tasks: list[AutomationTask] = list(
            tasks
            if tasks is not None
            else (CleanupTask(), ContinuousValidationTask(), OptimizationTask())
        )
        self._ticks = 0

    def register(self, task: AutomationTask) -> None:
        self._tasks.append(task)

    def tick(self, ctx: HealingContext, steps: int = 1) -> int:
        self._ticks += steps
        executed = 0
        for task in self._tasks:
            if self._ticks - task.last_run >= task.interval:
                task.run(ctx)
                task.last_run = self._ticks
                executed += 1
        return executed

    def tasks(self) -> list[AutomationTask]:
        return list(self._tasks)

    @property
    def ticks(self) -> int:
        return self._ticks
