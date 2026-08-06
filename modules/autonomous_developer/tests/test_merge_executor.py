"""Edge cases of the merge phase executor (branch/commit/diff/PR)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from modules.autonomous_developer.config.constants import PHASE_IMPLEMENT
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.execution.merge import GitPrExecutor
from modules.autonomous_developer.generator.generator import GenerationResult


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "user.name=test", "-c", "user.email=test@local", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _ctx(
    repo: Path,
    *,
    create_pr: bool = True,
    allow_main: bool = False,
    work_branch: str = "autonomous-dev",
) -> DeveloperContext:
    cfg = DeveloperConfig(
        project_root=str(repo),
        create_pr=create_pr,
        allow_main_branch_writes=allow_main,
        work_branch=work_branch,
    )
    cfg.resolve()
    return DeveloperContext(config=cfg)


def _with_change(ctx: DeveloperContext, repo: Path) -> None:
    (repo / "file.txt").write_text("changed\n", encoding="utf-8")
    ctx.set_artifact(PHASE_IMPLEMENT, GenerationResult(written=["file.txt"]))


@pytest.fixture()
def git_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "file.txt").write_text("original\n", encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "add", "file.txt")
    _git(repo, "commit", "-m", "initial")
    return repo


class TestMergeExecutor:
    def test_full_merge_on_git_repo(self, git_repo: Path):
        ctx = _ctx(git_repo)
        _with_change(ctx, git_repo)
        result = GitPrExecutor().run(ctx, goal="Fix the file content")
        assert result.skipped is None
        assert result.base_branch == "main"
        assert result.branch == "autonomous-dev"
        assert result.commit
        assert result.files == ["file.txt"]
        assert "+changed" in result.diff
        assert result.pr_artifact and Path(result.pr_artifact).exists()
        # Real git state: commit landed on the work branch, main untouched.
        branch = _git(git_repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        assert branch == "autonomous-dev"
        log = _git(git_repo, "log", "-1", "--format=%s").stdout.strip()
        assert log == "Fix the file content"
        main_log = _git(git_repo, "log", "main", "-1", "--format=%s").stdout.strip()
        assert main_log == "initial"

    def test_skipped_when_create_pr_disabled(self, git_repo: Path):
        ctx = _ctx(git_repo, create_pr=False)
        _with_change(ctx, git_repo)
        result = GitPrExecutor().run(ctx, goal="goal")
        assert result.skipped == "create_pr disabled"
        assert result.commit is None

    def test_skipped_when_not_a_git_repo(self, tmp_path: Path):
        plain = tmp_path / "plain"
        plain.mkdir()
        (plain / "file.txt").write_text("x\n", encoding="utf-8")
        ctx = _ctx(plain)
        _with_change(ctx, plain)
        result = GitPrExecutor().run(ctx, goal="goal")
        assert result.skipped == "not a git repository"
        assert result.commit is None

    def test_protected_branch_refuses(self, git_repo: Path):
        ctx = _ctx(git_repo, allow_main=False, work_branch="main")
        _with_change(ctx, git_repo)
        with pytest.raises(DeveloperError, match="protected branch"):
            GitPrExecutor().run(ctx, goal="goal")

    def test_protected_branch_allowed(self, git_repo: Path):
        ctx = _ctx(git_repo, allow_main=True, work_branch="main")
        _with_change(ctx, git_repo)
        result = GitPrExecutor().run(ctx, goal="goal")
        assert result.base_branch == "main"
        assert result.branch == "main"
        assert result.commit
