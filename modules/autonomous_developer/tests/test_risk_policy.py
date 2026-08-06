"""Risk policy: plans above the allowed risk level are blocked at execution."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.autonomous_developer.config.constants import (
    PHASE_PLAN,
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LEVELS,
    RISK_LOW,
    RISK_MEDIUM,
)
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.config.risk_policy import (
    enforce_task_risks,
    risk_exceeds,
    risk_rank,
)
from modules.autonomous_developer.core.exceptions import SecurityError
from modules.autonomous_developer.core.models import FileChange, Task, TaskPlan
from modules.autonomous_developer.generator.generator import CodeGenerator
from modules.autonomous_developer.tests.helpers import make_context


class TestRiskRanking:
    def test_ordering(self):
        assert RISK_LEVELS == (RISK_LOW, RISK_MEDIUM, RISK_HIGH, RISK_CRITICAL)
        assert [risk_rank(r) for r in RISK_LEVELS] == [0, 1, 2, 3]

    def test_unknown_ranks_highest(self):
        assert risk_rank("unpredictable") > risk_rank(RISK_CRITICAL)

    def test_exceeds_boundaries(self):
        assert not risk_exceeds(RISK_LOW, RISK_HIGH)
        assert not risk_exceeds(RISK_HIGH, RISK_HIGH)
        assert risk_exceeds(RISK_CRITICAL, RISK_HIGH)
        assert risk_exceeds("unknown", RISK_CRITICAL)  # fail closed


class TestEnforceTaskRisks:
    def _task(self, risk: str) -> Task:
        return Task(title="t", risk=risk)

    def test_no_violations_within_limit(self):
        tasks = [self._task(RISK_LOW), self._task(RISK_MEDIUM)]
        assert enforce_task_risks(tasks, RISK_HIGH) == []

    def test_returns_violation_ids(self):
        tasks = [self._task(RISK_LOW), self._task(RISK_CRITICAL), self._task(RISK_HIGH)]
        violations = enforce_task_risks(tasks, RISK_MEDIUM)
        assert len(violations) == 2
        assert tasks[1].task_id in violations[0]
        assert tasks[2].task_id in violations[1]

    def test_unknown_task_risk_blocks(self):
        tasks = [self._task("chaotic")]
        assert len(enforce_task_risks(tasks, RISK_CRITICAL)) == 1

    def test_invalid_max_raises(self):
        with pytest.raises(SecurityError):
            enforce_task_risks([self._task(RISK_LOW)], "turbo")


class TestGeneratorGate:
    def _plan(self, risk: str) -> TaskPlan:
        task = Task(title="t", risk=risk)
        task.add_file(FileChange(path="out.txt", content="x"))
        return TaskPlan(goal="g", tasks=[task])

    def test_high_risk_blocked_no_writes(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        ctx.set_artifact(PHASE_PLAN, self._plan(RISK_HIGH))
        generator = CodeGenerator(config=GeneratorConfig(max_risk_level=RISK_LOW))
        with pytest.raises(SecurityError) as exc:
            generator.run(ctx, goal="g")
        assert "risk policy" in str(exc.value)
        assert not (tmp_path / "out.txt").exists()

    def test_within_limit_applies(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        ctx.set_artifact(PHASE_PLAN, self._plan(RISK_MEDIUM))
        generator = CodeGenerator(config=GeneratorConfig(max_risk_level=RISK_HIGH))
        result = generator.run(ctx, goal="g")
        assert result.written == ["out.txt"]
        assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "x"

    def test_default_config_allows_critical(self, tmp_path: Path):
        # Default policy must not change existing behaviour.
        ctx = make_context(tmp_path)
        ctx.set_artifact(PHASE_PLAN, self._plan(RISK_CRITICAL))
        generator = CodeGenerator()
        result = generator.run(ctx, goal="g")
        assert result.written == ["out.txt"]

    def test_env_configures_max_risk(self, monkeypatch):
        monkeypatch.setenv("SUPERDEV_AD_GENERATOR_MAX_RISK", "medium")
        cfg = GeneratorConfig.from_env()
        assert cfg.max_risk_level == RISK_MEDIUM
