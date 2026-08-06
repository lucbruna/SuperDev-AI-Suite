"""Eval harness: fix-rate benchmark over a small bug corpus."""
from __future__ import annotations

from pathlib import Path

from modules.autonomous_developer.evaluation.corpus import CORPUS
from modules.autonomous_developer.evaluation.harness import (
    EvalHarness,
    estimate_cost,
)


class TestCostModel:
    def test_zero_tokens_free(self):
        assert estimate_cost(0, 0) == 0.0

    def test_positive(self):
        # 1k input at $0.15/M + 1k output at $0.60/M = $0.00075
        assert estimate_cost(1000, 1000) == 0.00075


class TestReportMath:
    def test_fix_rate(self):
        from modules.autonomous_developer.evaluation.harness import (
            CaseResult,
            EvalReport,
        )

        report = EvalReport(
            cases=[
                CaseResult(name="a", success=True, expected_success=True),
                CaseResult(name="b", success=True, expected_success=True),
                CaseResult(name="c", success=False, expected_success=True),
            ]
        )
        assert report.fix_rate == 2 / 3
        assert report.fixed_cases == 2
        assert report.total_cases == 3
        assert "fix_rate" in report.to_dict()


class TestHarnessRun:
    def test_small_corpus_run(self, tmp_path: Path):
        # 2 fixable cases + 1 deliberately unfixable (proves failed cases count).
        cases = [CORPUS[0], CORPUS[1], CORPUS[3]]
        report = EvalHarness(test_timeout=120).run(cases, tmp_path)
        assert report.total_cases == 3
        assert report.fixed_cases == 2
        assert report.fix_rate == 2 / 3

        by_name = {case.name: case for case in report.cases}
        fixed = by_name["calc-add-subtract"]
        assert fixed.success is True
        assert fixed.tests_passed >= 3 and fixed.tests_failed == 0
        assert fixed.error is None
        assert fixed.prompt_tokens > 0
        assert fixed.cost_usd > 0
        assert fixed.pr_artifact and Path(fixed.pr_artifact).exists()

        unfixed = by_name["calc-add-unfixed"]
        assert unfixed.success is False
        assert unfixed.expected_success is False  # corpus declared it unfixable
        assert unfixed.tests_failed >= 1

        report_json = report.to_json()
        assert '"fix_rate": 0.6667' in report_json
