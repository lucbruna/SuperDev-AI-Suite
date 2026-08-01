"""Unit tests for run_mantis.py — the full-pipeline runner for the Mantis suite.

Covers:
* ``stage_complete`` — the deterministic per-stage artifact probes.
* Checkpoint logic — load/save pipeline state, stage statuses, mark/reset.
* ``run_pipeline`` — dry-run, auto-run, runbook writing, full-pass archive.

The runner reads/writes through module-level globals that derive from
``scripts.mantis_pipeline`` (``mp.WORKSPACE`` etc.). The ``runner_state``
fixture repoints both the harness globals and the runner's ``RUNBOOK_DIR`` /
``PIPELINE_STATE_FILE`` at an isolated ``tmp_path``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import run_mantis as rm
from scripts import mantis_pipeline as mp


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def runner_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repoint harness + runner path globals at an isolated temp state root."""
    root = tmp_path / "state"
    root.mkdir()
    workspace = root / "workspace"
    workspace.mkdir(parents=True)  # files are written directly by probes/tests
    monkeypatch.setattr(mp, "STATE_ROOT", root)
    monkeypatch.setattr(mp, "WORKSPACE", workspace)
    monkeypatch.setattr(mp, "STATE_FILE", workspace / ".mantis_state.json")
    monkeypatch.setattr(mp, "PLAN_FILE", workspace / "plan.json")
    monkeypatch.setattr(mp, "FINDINGS_DIR", workspace / "findings")
    monkeypatch.setattr(mp, "KB_DIR", workspace / "kb")
    monkeypatch.setattr(mp, "ARCHIVE_DIR", workspace / "archive")
    monkeypatch.setattr(mp, "REPORT_DIR", workspace / "report")
    monkeypatch.setattr(mp, "HELPERS_DIR", workspace / "helpers")
    monkeypatch.setattr(mp, "REPRODUCERS_DIR", workspace / "reproducers")
    monkeypatch.setattr(mp, "LEARNINGS_FILE", workspace / "learnings.jsonl")
    monkeypatch.setattr(mp, "HISTORICAL_LEARNINGS_FILE", workspace / "historical_learnings.jsonl")
    # Runner-level globals computed at import time from mp.WORKSPACE.
    monkeypatch.setattr(rm, "RUNBOOK_DIR", workspace / "runbook")
    monkeypatch.setattr(rm, "PIPELINE_STATE_FILE", workspace / ".run_mantis.json")
    return root


@pytest.fixture
def code_root(tmp_path: Path) -> Path:
    """A small fake codebase to audit (used as --target-root)."""
    root = tmp_path / "code"
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("import os\nx = 1\n", encoding="utf-8")
    return root


def _write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


# ── stage_complete probes ─────────────────────────────────────────────────


class TestStageCompleteHistory:
    def test_true_when_learnings_non_empty(self, runner_state: Path):
        mp.HISTORICAL_LEARNINGS_FILE.write_text("line\n", encoding="utf-8")
        assert rm.stage_complete("history") is True

    def test_false_when_missing(self, runner_state: Path):
        assert rm.stage_complete("history") is False

    def test_false_when_empty(self, runner_state: Path):
        mp.HISTORICAL_LEARNINGS_FILE.write_text("", encoding="utf-8")
        assert rm.stage_complete("history") is False


class TestStageCompleteStructuralIndex:
    def test_true_with_manifest(self, runner_state: Path):
        manifest = mp.WORKSPACE / "kb" / "structural_index" / "manifest.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text("{}", encoding="utf-8")
        assert rm.stage_complete("structural-index") is True

    def test_false_without_manifest(self, runner_state: Path):
        assert rm.stage_complete("structural-index") is False


class TestStageCompleteSummarize:
    def test_true_with_summary_in_tree(self, runner_state: Path, code_root: Path):
        (code_root / "mantis-summary.md").write_text("# summary\n", encoding="utf-8")
        assert rm.stage_complete("summarize", code_root) is True

    def test_false_without_summary(self, runner_state: Path, code_root: Path):
        assert rm.stage_complete("summarize", code_root) is False

    def test_true_nested_in_excluded_dir(self, runner_state: Path, code_root: Path):
        """Summaries only inside EXCLUDED_DIRS must not count (bounded walk)."""
        if "node_modules" not in mp.EXCLUDED_DIRS:
            pytest.skip("node_modules not in EXCLUDED_DIRS")
        excluded = code_root / "node_modules"
        excluded.mkdir(parents=True)
        (excluded / "mantis-summary.md").write_text("# hidden\n", encoding="utf-8")
        assert rm.stage_complete("summarize", code_root) is False


class TestStageCompleteArchitecture:
    def test_true_with_index_and_architecture(self, runner_state: Path):
        kb = mp.WORKSPACE / "kb"
        kb.mkdir(parents=True)
        (kb / "index.md").write_text("# Index\n", encoding="utf-8")
        (kb / "architecture.md").write_text("# Arch\n", encoding="utf-8")
        assert rm.stage_complete("architecture") is True

    def test_false_with_only_index(self, runner_state: Path):
        kb = mp.WORKSPACE / "kb"
        kb.mkdir(parents=True)
        (kb / "index.md").write_text("# Index\n", encoding="utf-8")
        assert rm.stage_complete("architecture") is False


class TestStageCompleteThreatModel:
    def test_true_with_threat_model(self, runner_state: Path):
        kb = mp.WORKSPACE / "kb"
        kb.mkdir(parents=True)
        (kb / "THREAT_MODEL.md").write_text("# TM\n", encoding="utf-8")
        assert rm.stage_complete("threat-model") is True

    def test_false_without(self, runner_state: Path):
        assert rm.stage_complete("threat-model") is False


class TestStageCompletePlan:
    def test_true_with_investigations(self, runner_state: Path):
        mp.WORKSPACE.mkdir(parents=True, exist_ok=True)
        _write_json(mp.PLAN_FILE, {"investigations": [{"title": "x"}]})
        assert rm.stage_complete("plan") is True

    def test_false_with_empty_investigations(self, runner_state: Path):
        mp.WORKSPACE.mkdir(parents=True, exist_ok=True)
        _write_json(mp.PLAN_FILE, {"investigations": []})
        assert rm.stage_complete("plan") is False

    def test_false_with_invalid_json(self, runner_state: Path):
        mp.WORKSPACE.mkdir(parents=True, exist_ok=True)
        mp.PLAN_FILE.write_text("{not json", encoding="utf-8")
        assert rm.stage_complete("plan") is False

    def test_false_when_investigations_is_null(self, runner_state: Path):
        """`investigations: null` (present-but-None) must not crash the probe."""
        mp.WORKSPACE.mkdir(parents=True, exist_ok=True)
        _write_json(mp.PLAN_FILE, {"investigations": None})
        assert rm.stage_complete("plan") is False

    def test_false_when_plan_is_non_dict(self, runner_state: Path):
        """Valid-JSON-but-non-dict plan (e.g. a list) must not crash the probe."""
        mp.WORKSPACE.mkdir(parents=True, exist_ok=True)
        _write_json(mp.PLAN_FILE, [1, 2, 3])
        assert rm.stage_complete("plan") is False

    def test_false_when_missing(self, runner_state: Path):
        assert rm.stage_complete("plan") is False


class TestStageCompleteResearcher:
    def test_true_with_findings(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x"})
        assert rm.stage_complete("researcher") is True

    def test_false_without_findings(self, runner_state: Path):
        assert rm.stage_complete("researcher") is False


class TestStageCompleteReview:
    """Review completes only when EVERY finding carries a reviewer history entry."""

    def _reviewed_finding(self, data: dict) -> dict:
        data.setdefault("history", []).append(
            {"stage": "reviewer", "action": "reviewed", "pass_number": 1}
        )
        return data

    def test_true_when_all_findings_reviewed(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", self._reviewed_finding({"id": "a"}))
        _write_json(mp.FINDINGS_DIR / "f2.json", self._reviewed_finding({"id": "b"}))
        assert rm.stage_complete("review") is True

    def test_false_when_no_findings(self, runner_state: Path):
        assert rm.stage_complete("review") is False

    def test_false_when_one_finding_unreviewed(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", self._reviewed_finding({"id": "a"}))
        _write_json(mp.FINDINGS_DIR / "f2.json", {"id": "b"})  # no reviewer entry
        assert rm.stage_complete("review") is False

    def test_false_when_corrupt_finding(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        (mp.FINDINGS_DIR / "f1.json").write_text("{corrupt", encoding="utf-8")
        assert rm.stage_complete("review") is False

    def test_false_when_history_is_null(self, runner_state: Path):
        """`history: null` (present-but-None) must not crash the probe."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "a", "history": None})
        assert rm.stage_complete("review") is False

    def test_false_when_finding_is_non_dict(self, runner_state: Path):
        """Valid-JSON-but-non-dict finding (e.g. a list) must not crash."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", [1, 2, 3])
        assert rm.stage_complete("review") is False


class TestStageCompleteReproduce:
    def test_true_with_findings_and_reproducers(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        mp.REPRODUCERS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x"})
        (mp.REPRODUCERS_DIR / "r1.py").write_text("print(1)\n", encoding="utf-8")
        assert rm.stage_complete("reproduce") is True

    def test_false_with_findings_but_no_reproducers(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x"})
        assert rm.stage_complete("reproduce") is False


class TestStageCompleteChain:
    """Chain completes when a chains.md analysis record exists OR a finding
    carries a non-empty constituent_findings array (chain may legitimately
    produce zero chain files)."""

    def test_true_with_analysis_record(self, runner_state: Path):
        kb = mp.WORKSPACE / "kb"
        kb.mkdir(parents=True)
        (kb / "chains.md").write_text("# Chain analysis — none found\n", encoding="utf-8")
        assert rm.stage_complete("chain") is True

    def test_true_with_chain_finding(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "c1.json", {"id": "x", "constituent_findings": ["a", "b"]})
        assert rm.stage_complete("chain") is True

    def test_false_without_either(self, runner_state: Path):
        assert rm.stage_complete("chain") is False

    def test_false_with_corrupt_finding_only(self, runner_state: Path):
        """Corrupt/plain findings without the analysis record must not count."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        (mp.FINDINGS_DIR / "f1.json").write_text("{corrupt", encoding="utf-8")
        assert rm.stage_complete("chain") is False


class TestStageCompletePatch:
    def test_true_with_patch_diff(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x", "patch_diff": "--- a\n+++ b\n"})
        assert rm.stage_complete("patch") is True

    def test_false_without_patch_diff(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x"})
        assert rm.stage_complete("patch") is False


class TestStageCompleteCalibrate:
    """Calibrate completes when at least one finding carries risk scoring
    (dismissed FALSE_POSITIVEs are intentionally left unscored)."""

    def test_true_with_risk_score(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x", "mantis_risk_score": 7.9})
        assert rm.stage_complete("calibrate") is True

    def test_true_with_checklist(self, runner_state: Path):
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x", "calibration_checklist": {"rule_01": "DONE"}})
        assert rm.stage_complete("calibrate") is True

    def test_false_without_scored_findings(self, runner_state: Path):
        """Findings exist but none scored (pre-calibrate or all dismissed)."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", {"id": "x"})
        _write_json(mp.FINDINGS_DIR / "f2.json", {"id": "y", "status": "FALSE_POSITIVE"})
        assert rm.stage_complete("calibrate") is False

    def test_false_when_no_findings(self, runner_state: Path):
        assert rm.stage_complete("calibrate") is False

    def test_false_with_corrupt_finding_only(self, runner_state: Path):
        """Corrupt findings must not crash the probe nor count as scored."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        (mp.FINDINGS_DIR / "f1.json").write_text("{corrupt", encoding="utf-8")
        assert rm.stage_complete("calibrate") is False

    def test_true_when_one_corrupt_one_scored(self, runner_state: Path):
        """Null-safe: a corrupt sibling must not mask a genuinely scored finding."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        (mp.FINDINGS_DIR / "f1.json").write_text("{corrupt", encoding="utf-8")
        _write_json(mp.FINDINGS_DIR / "f2.json", {"id": "y", "mantis_risk_score": 3.5})
        assert rm.stage_complete("calibrate") is True

    def test_false_when_finding_is_non_dict(self, runner_state: Path):
        """Valid-JSON-but-non-dict finding (e.g. a list) must not crash."""
        mp.FINDINGS_DIR.mkdir(parents=True)
        _write_json(mp.FINDINGS_DIR / "f1.json", [1, 2, 3])
        assert rm.stage_complete("calibrate") is False


class TestStageCompleteReflect:
    def test_true_with_learnings(self, runner_state: Path):
        mp.LEARNINGS_FILE.write_text("line\n", encoding="utf-8")
        assert rm.stage_complete("reflect") is True

    def test_false_when_empty(self, runner_state: Path):
        mp.LEARNINGS_FILE.write_text("", encoding="utf-8")
        assert rm.stage_complete("reflect") is False


class TestStageCompleteReport:
    def test_true_with_report(self, runner_state: Path):
        mp.REPORT_DIR.mkdir(parents=True)
        (mp.REPORT_DIR / "review_packet-latest.md").write_text("# Report\n", encoding="utf-8")
        assert rm.stage_complete("report") is True

    def test_false_without(self, runner_state: Path):
        assert rm.stage_complete("report") is False


class TestStageCompleteUnknown:
    def test_unknown_stage_is_false(self, runner_state: Path):
        assert rm.stage_complete("does-not-exist") is False


# ── Checkpoint logic (workspace/.run_mantis.json) ─────────────────────────


class TestPipelineState:
    def test_load_returns_empty_when_missing(self, runner_state: Path):
        assert rm.load_pipeline_state() == {}

    def test_load_returns_empty_on_corrupt(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        rm.PIPELINE_STATE_FILE.write_text("{corrupt", encoding="utf-8")
        assert rm.load_pipeline_state() == {}

    def test_save_then_load_roundtrip(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        rm.save_pipeline_state({"stages": {"history": "done"}, "last_updated": "now"})
        state = rm.load_pipeline_state()
        assert state["stages"]["history"] == "done"
        assert state["last_updated"] == "now"

    def test_stage_statuses_creates_dict(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        assert rm.stage_statuses() == {}
        # set_stage materializes the "stages" key in the saved file.
        rm.set_stage("history", "done")
        assert rm.load_pipeline_state()["stages"]["history"] == "done"

    def test_set_stage_persists(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        rm.set_stage("history", "done")
        state = rm.load_pipeline_state()
        assert state["stages"]["history"] == "done"
        assert "last_updated" in state

    def test_set_stage_pending(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        rm.set_stage("researcher", "pending")
        assert rm.load_pipeline_state()["stages"]["researcher"] == "pending"

    def test_stage_statuses_overwrites_previous(self, runner_state: Path):
        rm.PIPELINE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        rm.set_stage("history", "done")
        rm.set_stage("history", "pending")
        assert rm.load_pipeline_state()["stages"]["history"] == "pending"


class TestMarkResetCli:
    """Checkpoint control via the CLI subcommands (mark / reset)."""

    def test_mark_sets_status(self, runner_state: Path, capsys):
        code = rm.main(["mark", "history", "done"])
        assert code == 0
        assert rm.load_pipeline_state()["stages"]["history"] == "done"

    def test_mark_pending(self, runner_state: Path, capsys):
        rm.main(["mark", "researcher", "done"])
        rm.main(["mark", "researcher", "pending"])
        assert rm.load_pipeline_state()["stages"]["researcher"] == "pending"

    def test_reset_all_clears_statuses(self, runner_state: Path, capsys):
        rm.main(["mark", "history", "done"])
        rm.main(["reset"])
        assert "stages" not in rm.load_pipeline_state()

    def test_reset_specific_stage(self, runner_state: Path, capsys):
        rm.main(["mark", "history", "done"])
        rm.main(["mark", "plan", "done"])
        rm.main(["reset", "--stages", "history"])
        state = rm.load_pipeline_state()
        assert "history" not in state["stages"]
        assert state["stages"]["plan"] == "done"


class TestWriteRunbookPrompt:
    def test_writes_prompt_file(self, runner_state: Path):
        stage = {"name": "researcher"}
        path = rm.write_runbook_prompt(7, stage, "PROMPT CONTENT")
        assert path.name == "07_researcher.md"
        assert path.exists()
        assert path.read_text(encoding="utf-8") == "PROMPT CONTENT\n"

    def test_writes_under_runbook_dir(self, runner_state: Path):
        path = rm.write_runbook_prompt(1, {"name": "history"}, "x")
        assert path.parent == rm.RUNBOOK_DIR


# ── run_pipeline orchestration ────────────────────────────────────────────


def _run_args(
    target_root: Path,
    *,
    stages: list[str] | None = None,
    dry_run: bool = False,
    auto: bool = True,
    interactive: bool = False,
    skip_init: bool = True,
    skip_plan: bool = True,
    no_archive: bool = True,
):
    argv = ["run", "--target-root", str(target_root), "--skip-init", "--skip-plan"]
    if no_archive:
        argv.append("--no-archive")
    if dry_run:
        argv.append("--dry-run")
    if interactive:
        argv.append("--interactive")
    if auto:
        argv.append("--auto")
    if stages:
        argv += ["--stages", *stages]
    return rm.build_parser().parse_args(argv)


class TestRunPipeline:
    def test_dry_run_writes_runbook_but_no_state(self, runner_state: Path, code_root: Path):
        args = _run_args(code_root, stages=["history"], dry_run=True)
        code = rm.run_pipeline(args)
        assert code == 0
        assert (rm.RUNBOOK_DIR / "01_history.md").exists()
        # Dry-run returns before persisting statuses.
        assert not rm.PIPELINE_STATE_FILE.exists()

    def test_auto_run_marks_done_via_artifact(self, runner_state: Path, code_root: Path):
        # Make architecture complete via artifact, then run it.
        kb = mp.WORKSPACE / "kb"
        kb.mkdir(parents=True)
        (kb / "index.md").write_text("# Index\n", encoding="utf-8")
        (kb / "architecture.md").write_text("# Arch\n", encoding="utf-8")

        args = _run_args(code_root, stages=["architecture"])
        code = rm.run_pipeline(args)
        assert code == 0
        assert rm.load_pipeline_state()["stages"]["architecture"] == "done"

    def test_auto_run_persists_pending(self, runner_state: Path, code_root: Path):
        args = _run_args(code_root, stages=["history"])
        code = rm.run_pipeline(args)
        assert code == 0
        assert rm.load_pipeline_state()["stages"]["history"] == "pending"
        assert (rm.RUNBOOK_DIR / "01_history.md").exists()

    def test_partial_run_does_not_archive(self, runner_state: Path, code_root: Path):
        """A partial --stages run must never trigger the Stage-15 archive."""
        args = _run_args(code_root, stages=["history"])
        rm.run_pipeline(args)
        # Only history was run; the other 15 stages are pending → no archive.
        assert not (mp.WORKSPACE / "archive").exists()

    def test_full_pass_archives_and_increments(self, runner_state: Path, code_root: Path, monkeypatch):
        # Simulate a complete pass: shrink the stage list to one stage whose
        # artifact we can create, then let the runner archive it.
        monkeypatch.setattr(mp, "STAGES", [{"name": "report"}])
        mp.REPORT_DIR.mkdir(parents=True)
        (mp.REPORT_DIR / "review_packet-latest.md").write_text("# Report\n", encoding="utf-8")

        args = _run_args(code_root, stages=["report"], no_archive=False)
        code = rm.run_pipeline(args)
        assert code == 0
        # Archive ran: pass incremented and statuses reset for the next pass.
        assert json.loads(mp.STATE_FILE.read_text(encoding="utf-8"))["pass_number"] == 2
        assert rm.load_pipeline_state()["stages"]["report"] == "pending"

    def test_remaining_spans_all_stages_not_filter(self, runner_state: Path, code_root: Path, monkeypatch):
        """remaining must cover ALL mp.STAGES so a partial run never archives."""
        monkeypatch.setattr(mp, "STAGES", [{"name": "history"}, {"name": "report"}])
        args = _run_args(code_root, stages=["history"], no_archive=False)
        code = rm.run_pipeline(args)
        assert code == 0
        # history ran (pending), report never ran → remaining non-empty → no archive.
        assert not (mp.WORKSPACE / "archive").exists()
