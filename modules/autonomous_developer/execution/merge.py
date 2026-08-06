"""Merge phase executor — branch, commit, diff and PR artifact.

Closes the autonomous loop: after tests pass and review approves, the
executor records the change in git on a dedicated work branch, computes the
diff against the base branch and writes a PR artifact describing the change
under the runtime data directory. If the ``gh`` CLI is available and the
repo has a remote, it also opens a real PR (best effort — the artifact is
the source of truth).

Safety gates:
- skipped entirely when ``config.create_pr`` is False;
- skipped when the project root is not a git work tree;
- refuses to work when the current branch is a protected main branch and
  ``config.allow_main_branch_writes`` is False.

All git calls use argument lists (never a shell) with a pinned bot identity
that only fills in when the environment does not already provide one.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from modules.autonomous_developer.config.constants import PHASE_IMPLEMENT
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.generator.generator import GenerationResult

__all__ = ["GitPrExecutor", "MergeResult"]

_PROTECTED_BRANCHES = ("main", "master")

_DEFAULT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Autonomous Developer",
    "GIT_AUTHOR_EMAIL": "dev@superdev.local",
    "GIT_COMMITTER_NAME": "Autonomous Developer",
    "GIT_COMMITTER_EMAIL": "dev@superdev.local",
}

_MAX_MESSAGE_LEN = 72


def _first_line(text: str, limit: int = _MAX_MESSAGE_LEN) -> str:
    line = next((ln.strip() for ln in (text or "").splitlines() if ln.strip()), "")
    return line[:limit] if line else "autonomous developer change"


class MergeResult:
    """Structured outcome of the merge phase (also dict-serializable)."""

    def __init__(
        self,
        *,
        branch: str,
        base_branch: str,
        commit: str | None,
        files: list[str],
        diff: str,
        pr_artifact: str | None,
        pr_created: bool = False,
        skipped: str | None = None,
    ) -> None:
        self.branch = branch
        self.base_branch = base_branch
        self.commit = commit
        self.files = files
        self.diff = diff
        self.pr_artifact = pr_artifact
        self.pr_created = pr_created
        self.skipped = skipped

    def to_dict(self) -> dict[str, Any]:
        return {
            "branch": self.branch,
            "base_branch": self.base_branch,
            "commit": self.commit,
            "files": self.files,
            "diff": self.diff,
            "pr_artifact": self.pr_artifact,
            "pr_created": self.pr_created,
            "skipped": self.skipped,
        }

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"MergeResult({self.to_dict()!r})"


class GitPrExecutor:
    """Registered component for the ``merge`` phase (kind "executor")."""

    def __init__(self, identity: dict[str, str] | None = None) -> None:
        self.identity = identity or {}

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> MergeResult:
        config = ctx.config
        if not config.create_pr:
            return MergeResult(
                branch=config.work_branch,
                base_branch="",
                commit=None,
                files=[],
                diff="",
                pr_artifact=None,
                skipped="create_pr disabled",
            )
        repo = Path(config.project_root)
        git_env = {**os.environ, **self.identity}
        for key, value in _DEFAULT_IDENTITY.items():
            git_env.setdefault(key, value)

        if not self._is_git_repo(repo, git_env):
            return MergeResult(
                branch=config.work_branch,
                base_branch="",
                commit=None,
                files=[],
                diff="",
                pr_artifact=None,
                skipped="not a git repository",
            )

        base_branch = self._current_branch(repo, git_env)
        if (
            config.work_branch in _PROTECTED_BRANCHES
            and not config.allow_main_branch_writes
        ):
            raise DeveloperError(
                f"Refusing to commit on protected branch {config.work_branch!r}; "
                "set allow_main_branch_writes=True to override",
                context={"branch": config.work_branch, "goal": goal},
            )

        written = self._written_files(repo, ctx, config.work_branch)
        self._ensure_work_branch(repo, config.work_branch, git_env)
        self._stage(repo, written, git_env)
        has_changes = self._has_staged_changes(repo, git_env)
        commit_sha: str | None = None
        if has_changes:
            commit_sha = self._commit(repo, goal, git_env)
        diff = self._diff(repo, base_branch, git_env)

        pr_artifact = self._write_pr_artifact(
            ctx, goal=goal, session_id=session_id or "unknown",
            diff=diff, base_branch=base_branch, commit=commit_sha,
        )
        pr_created = self._try_create_pr(
            repo, git_env, base_branch=base_branch,
            branch=config.work_branch, goal=goal, body=pr_artifact,
        )
        ctx.record("merge_branch", config.work_branch)
        ctx.record("merge_commit", commit_sha or "")
        ctx.record("merge_files", len(written))
        ctx.publish(
            "merge.completed",
            {"branch": config.work_branch, "commit": commit_sha,
             "pr_created": pr_created},
        )
        return MergeResult(
            branch=config.work_branch,
            base_branch=base_branch,
            commit=commit_sha,
            files=written,
            diff=diff,
            pr_artifact=str(pr_artifact) if pr_artifact else None,
            pr_created=pr_created,
        )

    # ── internals ───────────────────────────────────────────────────────────
    def _git(
        self, repo: Path, env: dict[str, str], *args: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def _is_git_repo(self, repo: Path, env: dict[str, str]) -> bool:
        proc = self._git(repo, env, "rev-parse", "--is-inside-work-tree")
        return proc.returncode == 0 and proc.stdout.strip() == "true"

    def _current_branch(self, repo: Path, env: dict[str, str]) -> str:
        proc = self._git(repo, env, "rev-parse", "--abbrev-ref", "HEAD")
        return proc.stdout.strip() or "HEAD"

    def _written_files(self, repo: Path, ctx, work_branch: str) -> list[str]:
        impl = ctx.get_artifact(PHASE_IMPLEMENT)
        if not isinstance(impl, GenerationResult):
            return []
        relative: list[str] = []
        for path in impl.written:
            p = Path(path)
            if p.is_absolute():
                try:
                    p = p.relative_to(repo)
                except ValueError:
                    continue
            relative.append(p.as_posix())
        return sorted(relative)

    def _ensure_work_branch(self, repo: Path, branch: str, env: dict[str, str]) -> None:
        current = self._current_branch(repo, env)
        if current == branch:
            return
        exists = self._git(repo, env, "show-ref", "--verify", "--quiet",
                           f"refs/heads/{branch}").returncode == 0
        checkout = self._git(repo, env, "checkout", "-b", branch) if not exists else (
            self._git(repo, env, "checkout", branch)
        )
        if checkout.returncode != 0:
            raise DeveloperError(
                f"git checkout {branch} failed: {checkout.stderr.strip()[:300]}",
                context={"branch": branch},
            )

    def _stage(self, repo: Path, files: list[str], env: dict[str, str]) -> None:
        if not files:
            return
        add = self._git(repo, env, "add", "--", *files)
        if add.returncode != 0:
            raise DeveloperError(
                f"git add failed: {add.stderr.strip()[:300]}",
                context={"files": files},
            )

    def _has_staged_changes(self, repo: Path, env: dict[str, str]) -> bool:
        proc = self._git(repo, env, "diff", "--cached", "--name-only")
        return bool(proc.stdout.strip())

    def _commit(self, repo: Path, goal: str, env: dict[str, str]) -> str:
        message = _first_line(goal)
        commit = self._git(repo, env, "commit", "-m", message)
        if commit.returncode != 0:
            raise DeveloperError(
                f"git commit failed: {commit.stderr.strip()[:300]}",
                context={"message": message},
            )
        sha = self._git(repo, env, "rev-parse", "HEAD")
        return sha.stdout.strip()

    def _diff(self, repo: Path, base_branch: str, env: dict[str, str]) -> str:
        proc = self._git(repo, env, "diff", f"{base_branch}..HEAD")
        if proc.returncode != 0:
            return ""
        return proc.stdout or ""

    def _write_pr_artifact(
        self,
        ctx,
        *,
        goal: str,
        session_id: str,
        diff: str,
        base_branch: str,
        commit: str | None,
    ) -> Path:
        pr_dir = Path(ctx.config.data_dir) / "pr"
        pr_dir.mkdir(parents=True, exist_ok=True)
        body = (
            f"## {_first_line(goal)}\n\n"
            f"Autonomous Developer session `{session_id}`\n\n"
            f"- base: `{base_branch}`\n"
            f"- branch: `{ctx.config.work_branch}`\n"
            f"- commit: `{commit or 'none'}`\n\n"
            "### Changes\n\n```diff\n" + (diff or "no changes") + "\n```\n"
        )
        artifact = pr_dir / f"pr-{session_id}.md"
        artifact.write_text(body, encoding="utf-8")
        return artifact

    def _try_create_pr(
        self,
        repo: Path,
        env: dict[str, str],
        *,
        base_branch: str,
        branch: str,
        goal: str,
        body: Path,
    ) -> bool:
        if shutil.which("gh") is None:
            return False
        remote = self._git(repo, env, "remote").stdout.strip()
        if not remote:
            return False
        try:
            proc = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--base", base_branch,
                    "--head", branch,
                    "--title", _first_line(goal),
                    "--body-file", str(body),
                ],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return proc.returncode == 0
