"""Eval harness — runs the autonomous loop over a bug corpus.

Measures the two headline numbers of the module: the **fix rate** (share of
cases where the loop ended with the repo's real tests passing) and the
**cost** (estimated LLM spend per case, derived from token usage recorded by
the mocked planner). Results are returned as an :class:`EvalReport` and can
be dumped to JSON for trend tracking.
"""
from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.constants import (
    PHASE_IMPLEMENT,
    PHASE_MERGE,
    PHASE_PLAN,
    PHASE_REVIEW,
    PHASE_TEST,
)
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime
from modules.autonomous_developer.evaluation.corpus import EvalCase
from modules.autonomous_developer.core.costs import estimate_cost
from modules.autonomous_developer.execution.merge import GitPrExecutor
from modules.autonomous_developer.generator.generator import CodeGenerator
from modules.autonomous_developer.llm.client import LLMClient, estimate_tokens
from modules.autonomous_developer.planner.project_planner import ProjectPlanner
from modules.autonomous_developer.review.reviewer import CodeReviewer
from modules.autonomous_developer.validation.test_runner import TestRunnerValidator

__all__ = ["CaseResult", "EvalReport", "EvalHarness", "estimate_cost"]

PHASES = (PHASE_PLAN, PHASE_IMPLEMENT, PHASE_TEST, PHASE_REVIEW, PHASE_MERGE)


@dataclass(slots=True)
class CaseResult:
    """Outcome of running one benchmark case."""

    name: str
    success: bool
    expected_success: bool
    tests_passed: int = 0
    tests_failed: int = 0
    duration_seconds: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    pr_artifact: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "success": self.success,
            "expected_success": self.expected_success,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "duration_seconds": round(self.duration_seconds, 2),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_usd": round(self.cost_usd, 6),
            "pr_artifact": self.pr_artifact,
            "error": self.error,
        }


@dataclass(slots=True)
class EvalReport:
    """Aggregate benchmark results."""

    cases: list[CaseResult] = field(default_factory=list)

    @property
    def total_cases(self) -> int:
        return len(self.cases)

    @property
    def fixed_cases(self) -> int:
        return sum(1 for case in self.cases if case.success)

    @property
    def fix_rate(self) -> float:
        if not self.cases:
            return 0.0
        return self.fixed_cases / len(self.cases)

    @property
    def total_cost_usd(self) -> float:
        return round(sum(case.cost_usd for case in self.cases), 6)

    @property
    def avg_duration_seconds(self) -> float:
        if not self.cases:
            return 0.0
        return round(sum(case.duration_seconds for case in self.cases) / len(self.cases), 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "fixed_cases": self.fixed_cases,
            "fix_rate": round(self.fix_rate, 4),
            "total_cost_usd": self.total_cost_usd,
            "avg_duration_seconds": self.avg_duration_seconds,
            "cases": [case.to_dict() for case in self.cases],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class _EvalPlanner:
    """Planner whose 'brain' is the case's plan JSON (mocked LLM).

    Records token usage into the context so the harness can estimate cost.
    """

    def __init__(self, case: EvalCase) -> None:
        self.llm = LLMClient(mock_response=json.dumps(case.plan))
        self._planner = ProjectPlanner()

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        prompt = f"Goal: {goal}"
        response = self.llm.complete(prompt)
        payload = json.loads(response.text)
        plan = self._planner.plan(payload["goal"], tasks=payload["tasks"])
        prompt_tokens = estimate_tokens(prompt)
        completion_tokens = estimate_tokens(response.text)
        ctx.record_usage("plan", prompt_tokens, completion_tokens)
        ctx.record("llm_prompt_tokens", prompt_tokens)
        ctx.record("llm_completion_tokens", completion_tokens)
        ctx.publish("plan.ready", {"goal": plan.goal, "task_count": len(plan.tasks)})
        return plan


class EvalHarness:
    """Runs the full loop per case and aggregates the results."""

    def __init__(
        self,
        *,
        test_timeout: int = 120,
        create_pr: bool = True,
        llm_provider: str | None = None,
    ) -> None:
        self.test_timeout = test_timeout
        self.create_pr = create_pr
        self.llm_provider = llm_provider

    def run_case(self, case: EvalCase, base_dir: Path) -> CaseResult:
        repo = base_dir / case.name
        repo.mkdir(parents=True, exist_ok=True)
        for name, content in case.files.items():
            (repo / name).write_text(content, encoding="utf-8")
        self._git(repo, "init", "-b", "main")
        self._git(repo, "add", ".")
        self._git(repo, "commit", "-m", f"initial {case.name}")

        registry = DeveloperRegistry()
        registry.register("planner", "default", _EvalPlanner(case))
        registry.register("generator", "default", CodeGenerator())
        registry.register(
            "validator", "default", TestRunnerValidator(timeout_seconds=self.test_timeout)
        )
        registry.register("reviewer", "default", CodeReviewer())
        registry.register("executor", "default", GitPrExecutor())
        config = DeveloperConfig(
            project_root=str(repo),
            mode="supervised",
            work_branch=case.work_branch,
            run_tests=True,
            run_review=True,
            create_pr=self.create_pr,
        )
        runtime = DeveloperRuntime(config=config, registry=registry)

        start = time.time()
        error: str | None = None
        ctx: DeveloperContext
        try:
            ctx = runtime.execute(case.goal, phases=PHASES)
        except Exception as exc:  # noqa: BLE001 — harness must not die
            error = str(exc)
            ctx = runtime.context

        impl = ctx.get_artifact(PHASE_IMPLEMENT)
        tests_passed = int(ctx.stats.get("tests_passed", 0) or 0)
        tests_failed = int(ctx.stats.get("tests_failed", 0) or 0)
        merge = ctx.get_artifact(PHASE_MERGE)
        success = error is None and tests_failed == 0 and (
            impl is None or impl.success
        )
        prompt_tokens = int(ctx.stats.get("llm_prompt_tokens", 0) or 0)
        completion_tokens = int(ctx.stats.get("llm_completion_tokens", 0) or 0)
        return CaseResult(
            name=case.name,
            success=success,
            expected_success=not case.expect_failure,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            duration_seconds=time.time() - start,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=estimate_cost(prompt_tokens, completion_tokens),
            pr_artifact=merge.pr_artifact if merge is not None else None,
            error=error,
        )

    def run(self, cases: list[EvalCase], base_dir: Path) -> EvalReport:
        return EvalReport(cases=[self.run_case(case, base_dir) for case in cases])

    def _git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-c", "user.name=eval", "-c", "user.email=eval@local", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )


def run_eval(
    cases: list[EvalCase],
    base_dir: Path,
    *,
    test_timeout: int = 120,
    create_pr: bool = True,
) -> EvalReport:
    """Convenience entry point: run ``cases`` under ``base_dir``."""
    return EvalHarness(
        test_timeout=test_timeout, create_pr=create_pr
    ).run(cases, base_dir)
