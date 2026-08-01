"""Unit tests for scripts.mantis_pipeline — the deterministic Mantis harness.

The harness reads/writes through module-level path globals (``STATE_ROOT``,
``WORKSPACE``, …). The ``state_root`` fixture repoints those globals at an
isolated ``tmp_path`` so tests never touch the real repository ``workspace/``.

Run with the root ``tests/conftest.py`` (no special flags needed):

    python -m pytest tests/unit/test_mantis_pipeline.py

(The root conftest imports ``backend.config``; ``CORS_ALLOW_METHODS`` and the
other comma-separated env lists are handled by the ``StrList`` type in
``backend/settings.py``, so the full suite runs without ``--confcutdir``.)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import mantis_pipeline as mp


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def state_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Repoint the harness path globals at an isolated temp state root."""
    root = tmp_path / "state"
    root.mkdir()
    monkeypatch.setattr(mp, "STATE_ROOT", root)
    monkeypatch.setattr(mp, "WORKSPACE", root / "workspace")
    monkeypatch.setattr(mp, "STATE_FILE", root / "workspace" / ".mantis_state.json")
    monkeypatch.setattr(mp, "PLAN_FILE", root / "workspace" / "plan.json")
    monkeypatch.setattr(mp, "FINDINGS_DIR", root / "workspace" / "findings")
    monkeypatch.setattr(mp, "KB_DIR", root / "workspace" / "kb")
    monkeypatch.setattr(mp, "ARCHIVE_DIR", root / "workspace" / "archive")
    monkeypatch.setattr(mp, "REPORT_DIR", root / "workspace" / "report")
    monkeypatch.setattr(mp, "HELPERS_DIR", root / "workspace" / "helpers")
    monkeypatch.setattr(mp, "REPRODUCERS_DIR", root / "workspace" / "reproducers")
    monkeypatch.setattr(mp, "LEARNINGS_FILE", root / "workspace" / "learnings.jsonl")
    monkeypatch.setattr(mp, "HISTORICAL_LEARNINGS_FILE", root / "workspace" / "historical_learnings.jsonl")
    return root


@pytest.fixture
def target_root(tmp_path: Path) -> Path:
    """A small fake codebase to crawl (src + excluded tests/vendor)."""
    root = tmp_path / "code"
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text(
        "import os\n\ndef main() -> str:\n    return os.getcwd()\n", encoding="utf-8",
    )
    (root / "src" / "helper.py").write_text(
        "def helper() -> int:\n    return 1\n", encoding="utf-8",
    )
    (root / "src" / "test_app.py").write_text(
        "def test_x() -> None:\n    pass\n", encoding="utf-8",
    )
    (root / "tests").mkdir()
    (root / "tests" / "test_real.py").write_text(
        "def test_y() -> None:\n    pass\n", encoding="utf-8",
    )
    (root / "node_modules").mkdir()
    (root / "node_modules" / "dep.js").write_text(
        "module.exports = 1;\n", encoding="utf-8",
    )
    (root / "built.txt").write_text("not a source file\n", encoding="utf-8")
    return root


def _valid_finding(uuid: str) -> dict:
    """A finding object that satisfies the schema's required fields + enums."""
    return {
        "id": uuid,
        "title": "Test finding",
        "description": "A description",
        "code_paths": ["src/app.py:3"],
        "impact": "High",
        "severity": "MEDIUM",
        "mitigation": "Fix it",
        "history": [],
        "attacker_position": "EXTERNAL",
        "privileges_required": "NONE",
        "user_interaction": "NONE",
        "status": "NEEDS_RESEARCH",
    }


# ── detect_vcs ────────────────────────────────────────────────────────────


class TestDetectVcs:
    def test_no_vcs_directory(self, target_root: Path):
        vcs = mp.detect_vcs(target_root)
        assert vcs["vcs_type"] == "none"
        assert vcs["dirty"] is False

    def test_git_repo(self, tmp_path: Path):
        import shutil
        import subprocess

        if shutil.which("git") is None:
            pytest.skip("git not available")
        repo = tmp_path / "gitrepo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "t@t.t"], check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "t"], check=True, capture_output=True,
        )
        (repo / "a.py").write_text("x = 1\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "init"], check=True, capture_output=True)

        vcs = mp.detect_vcs(repo)
        assert vcs["vcs_type"] == "git"
        assert vcs["commit_hash"]
        assert vcs["dirty"] is False

        # Make the tree dirty and re-detect.
        (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
        vcs2 = mp.detect_vcs(repo)
        assert vcs2["dirty"] is True


# ── init ──────────────────────────────────────────────────────────────────


class TestInitWorkspace:
    def test_init_creates_dirs_and_state(self, state_root: Path, target_root: Path):
        state = mp.init_workspace(target_root)
        assert mp.WORKSPACE.exists()
        assert mp.FINDINGS_DIR.exists()
        assert (mp.FINDINGS_DIR / ".trash").exists()
        assert mp.KB_DIR.exists()
        assert (mp.KB_DIR / "entities").exists()
        assert (mp.KB_DIR / "vulnerabilities").exists()
        assert mp.ARCHIVE_DIR.exists()
        assert mp.REPORT_DIR.exists()
        assert mp.HELPERS_DIR.exists()
        assert mp.REPRODUCERS_DIR.exists()
        assert state["pass_number"] == 1
        assert state["vcs_info"]["vcs_type"] in {"git", "hg", "multi-vcs", "none", "unknown"}

    def test_init_creates_state_file(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        assert mp.STATE_FILE.exists()
        data = json.loads(mp.STATE_FILE.read_text(encoding="utf-8"))
        assert data["pass_number"] == 1
        assert "last_updated" in data
        assert "vcs_info" in data

    def test_init_creates_plan_and_learnings_files(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        assert mp.PLAN_FILE.exists()
        assert json.loads(mp.PLAN_FILE.read_text(encoding="utf-8")) == {"investigations": []}
        assert mp.LEARNINGS_FILE.exists()
        assert mp.HISTORICAL_LEARNINGS_FILE.exists()

    def test_init_is_idempotent(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        state2 = mp.init_workspace(target_root)
        assert state2["pass_number"] == 1
        assert mp.PLAN_FILE.exists()

    def test_load_state_roundtrip(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        state = mp.load_state()
        assert state["pass_number"] == 1
        assert mp.save_state(state) is None  # no error
        assert json.loads(mp.STATE_FILE.read_text(encoding="utf-8"))["pass_number"] == 1


# ── crawl + plan ──────────────────────────────────────────────────────────


class TestCrawlAndPlan:
    def test_crawl_excludes_tests_and_vendor(self, target_root: Path):
        files = mp.crawl_production_files(target_root)
        rels = [f.relative_to(target_root).as_posix() for f in files]
        assert "src/app.py" in rels
        assert "src/helper.py" in rels
        assert "src/test_app.py" not in rels          # test_ prefix excluded
        assert "tests/test_real.py" not in rels        # tests/ dir excluded
        assert "node_modules/dep.js" not in rels       # vendor excluded
        assert "built.txt" not in rels                 # non-source excluded

    def test_write_plan_creates_investigations(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)  # plan writes under workspace/ — init first
        path = mp.write_plan(target_root)
        plan = json.loads(path.read_text(encoding="utf-8"))
        titles = [inv["title"] for inv in plan["investigations"]]
        assert any("src/app.py" in t for t in titles)
        assert any("src/helper.py" in t for t in titles)
        for inv in plan["investigations"]:
            assert inv["title"]
            assert inv["target_files"]
            assert inv["kb_references"] == []
            assert inv["question"]

    def test_write_plan_empty_for_empty_tree(self, state_root: Path, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir()
        mp.init_workspace(empty)
        path = mp.write_plan(empty)
        assert json.loads(path.read_text(encoding="utf-8")) == {"investigations": []}

    def test_plan_schema_valid(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        mp.write_plan(target_root)
        assert mp.validate_artifacts() == []


# ── validate ──────────────────────────────────────────────────────────────


class TestValidateArtifacts:
    def test_validate_ok_on_fresh_state(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        assert mp.validate_artifacts() == []

    def test_validate_reports_invalid_finding(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        bad = mp.FINDINGS_DIR / "bad.json"
        bad.write_text('{"id": "x"}', encoding="utf-8")  # missing required fields
        errors = mp.validate_artifacts()
        assert any("bad.json" in e for e in errors)

    def test_validate_reports_invalid_json(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        (mp.FINDINGS_DIR / "broken.json").write_text("{not json", encoding="utf-8")
        errors = mp.validate_artifacts()
        assert any("broken.json" in e and "invalid JSON" in e for e in errors)

    def test_validate_accepts_valid_finding(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        (mp.FINDINGS_DIR / "ok.json").write_text(
            json.dumps(_valid_finding("11111111-1111-4111-8111-111111111111")), encoding="utf-8",
        )
        assert mp.validate_artifacts() == []

    def test_validate_reports_missing_schema(self, state_root: Path, target_root: Path, monkeypatch):
        monkeypatch.setattr(mp, "SCHEMA_PATH", state_root / "nope.json")
        assert mp.validate_artifacts()[0].startswith("schema.json not found")


# ── archive (Stage 15) ────────────────────────────────────────────────────


class TestArchivePass:
    def test_archive_moves_findings_and_increments(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        (mp.FINDINGS_DIR / "f1.json").write_text(
            json.dumps(_valid_finding("11111111-1111-4111-8111-111111111111")), encoding="utf-8",
        )
        (mp.FINDINGS_DIR / "f2.json").write_text(
            json.dumps(_valid_finding("22222222-2222-4222-8222-222222222222")), encoding="utf-8",
        )

        result = mp.archive_pass()
        assert result["archived_pass"] == 1
        assert result["new_pass"] == 2
        assert result["moved_findings"] == 2
        assert not list(mp.FINDINGS_DIR.glob("*.json"))
        archive = mp.ARCHIVE_DIR / "findings_pass_1"
        assert (archive / "f1.json").exists()
        assert (archive / "f2.json").exists()
        assert json.loads(mp.STATE_FILE.read_text(encoding="utf-8"))["pass_number"] == 2

    def test_archive_copies_state_and_kb(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        (mp.KB_DIR / "index.md").write_text("# Index\n", encoding="utf-8")
        (mp.KB_DIR / "entities").mkdir(exist_ok=True)
        (mp.KB_DIR / "entities" / "auth.md").write_text("# Auth\n", encoding="utf-8")

        mp.archive_pass()
        archive = mp.ARCHIVE_DIR / "findings_pass_1"
        assert (archive / ".mantis_state.json").exists()
        assert (archive / "kb" / "index.md").exists()
        assert (archive / "kb" / "entities" / "auth.md").exists()
        # Live KB survives (copy, not move).
        assert (mp.KB_DIR / "index.md").exists()

    def test_archive_with_no_findings(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        result = mp.archive_pass()
        assert result["moved_findings"] == 0
        assert result["new_pass"] == 2

    def test_archive_moves_trash(self, state_root: Path, target_root: Path):
        mp.init_workspace(target_root)
        (mp.FINDINGS_DIR / "f1.json").write_text(
            json.dumps(_valid_finding("11111111-1111-4111-8111-111111111111")), encoding="utf-8",
        )
        trash = mp.FINDINGS_DIR / ".trash"
        trash.mkdir(exist_ok=True)
        (trash / "dup.json").write_text("{}", encoding="utf-8")
        mp.archive_pass()
        assert (mp.ARCHIVE_DIR / "findings_pass_1" / ".trash" / "dup.json").exists()


# ── stage_prompt / read_skill_description ─────────────────────────────────


class TestStagePrompt:
    def test_known_stage(self):
        prompt = mp.stage_prompt("researcher", Path.cwd())
        assert "/mantis-researcher" in prompt
        assert "mantis-researcher/SKILL.md" in prompt
        assert "workspace/" in prompt
        assert "Pass:" in prompt

    def test_findings_only_stage(self):
        prompt = mp.stage_prompt("report")
        assert "/mantis-report" in prompt
        assert "findings-only stage" in prompt

    def test_unknown_stage(self):
        with pytest.raises(SystemExit, match="Unknown stage"):
            mp.stage_prompt("nope")

    def test_read_skill_description_yaml_block(self):
        desc = mp.read_skill_description(mp.SKILLS_DIR / "mantis-architecture")
        assert "Knowledge Base" in desc
