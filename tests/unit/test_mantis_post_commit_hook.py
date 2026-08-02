"""Automated tests for the Mantis post-commit hook (``.githooks/post-commit``).

The hook is a bash script git executes after *every* commit. To exercise it
**without making a real commit**, each test builds a throwaway git repo in
``tmp_path``, copies the tracked Mantis runtime into it (the same set a fresh
clone ships), stages the files (so the installer's ``--status`` tracked-check
behaves like a real clone) and enables the hook exactly like
``scripts/install_mantis_hooks.sh`` does. Then each test invokes the hook with
``bash`` — the same way git invokes it after a commit — and asserts the fast
security check runs and produces workspace artifacts.

The sandbox repo stays at **zero commits** the whole time, which proves no real
commit is needed to verify the hook.

**Windows note:** bash is invoked with *relative* paths from inside the sandbox
cwd. Absolute Windows paths (``C:/...``) get mangled by Git Bash/MSYS2 argument
conversion when spawned from a Windows Python subprocess, so the scripts are
copied into the sandbox and invoked the same way a developer would use them.

**Python resolution:** when pytest is a Windows Python but the spawned ``bash``
is WSL bash (``/mnt/c/...``), ``command -v python`` cannot resolve Windows
``python.exe`` (bash does no PATHEXT-style resolution). The fixture therefore
installs a ``.testbin/python`` shim in the sandbox that ``exec``s the exact
interpreter running pytest (discovered via ``bash -c 'pwd -P'`` so the path is
bash-visible), and prepends it to PATH in colon-separated form. This makes the
hook's ``command -v python`` guard pass deterministically and runs the real
pipeline with the test interpreter (which has ``jsonschema``).

The tests assume a bash-visible (colon-separated) ``PATH`` in ``os.environ``
— true when pytest itself runs under WSL/Git Bash interop, as in this repo's
environment. The ``_run`` helper prepends with ``:`` accordingly.

Run with the root ``tests/conftest.py``:

    python -m pytest tests/unit/test_mantis_post_commit_hook.py

Requires ``bash`` (Git Bash or WSL bash) and ``git`` on PATH; skipped otherwise.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER = REPO_ROOT / "scripts" / "install_mantis_hooks.sh"

needs_bash_git = pytest.mark.skipif(
    shutil.which("bash") is None or shutil.which("git") is None,
    reason="bash and git are required to simulate the post-commit hook",
)


@lru_cache(maxsize=None)
def _bash_visible(path: Path) -> str:
    """Return how ``bash`` sees a directory (e.g. ``/mnt/c/...`` or ``/c/...``)."""
    try:
        r = subprocess.run(
            ["bash", "-c", "pwd -P"],
            cwd=path, capture_output=True, text=True, timeout=30,
        )
        out = r.stdout.strip()
        if out:
            return out
    except (OSError, subprocess.SubprocessError):
        pass
    return path.as_posix()  # POSIX fallback (Linux CI / Git Bash)


def _run(
    args: list[str],
    cwd: Path,
    env_extra: dict[str, str] | None = None,
    timeout: int = 240,
    prepend_path: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command, optionally prepending a bash-visible dir to PATH."""
    env = dict(os.environ)
    if prepend_path:
        env["PATH"] = prepend_path + ":" + env.get("PATH", "")
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout,
    )


@pytest.fixture
def hook_sandbox(tmp_path: Path) -> Path:
    """A throwaway git repo with the Mantis runtime + hook installed."""
    repo = tmp_path / "sandbox"
    repo.mkdir()
    init = _run(["git", "init", "-q"], cwd=repo)
    assert init.returncode == 0, init.stderr

    # Copy the tracked runtime — the same set a fresh clone ships.
    shutil.copy2(REPO_ROOT / "run_mantis.py", repo / "run_mantis.py")
    (repo / "scripts").mkdir()
    shutil.copy2(REPO_ROOT / "scripts" / "__init__.py", repo / "scripts" / "__init__.py")
    shutil.copy2(REPO_ROOT / "scripts" / "mantis_pipeline.py", repo / "scripts" / "mantis_pipeline.py")
    shutil.copy2(INSTALLER, repo / "scripts" / "install_mantis_hooks.sh")
    skills = repo / ".agents" / "skills"
    skills.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / ".agents" / "skills" / "schema.json", skills / "schema.json")
    shutil.copytree(REPO_ROOT / ".githooks", repo / ".githooks")

    # Python shim: make `python` resolve to the interpreter running pytest,
    # visible to whatever bash flavor is spawned (WSL /mnt/c or Git Bash /c).
    bin_dir = repo / ".testbin"
    bin_dir.mkdir()
    py_dir = _bash_visible(Path(sys.executable).resolve().parent)
    exe = Path(sys.executable).name  # python.exe on Windows, python3 on POSIX
    shim = bin_dir / "python"
    shim.write_bytes(  # LF only — CRLF would break the shebang in bash
        f"#!/usr/bin/env bash\nexec \"{py_dir}/{exe}\" \"$@\"\n".encode("utf-8"),
    )
    chmod = _run(["bash", "-c", "chmod +x .testbin/python"], cwd=repo)
    assert chmod.returncode == 0, chmod.stderr

    # Stage the files (no commit!) so the installer's --status tracked-hook
    # check sees a versioned hook exactly like a real clone would.
    stage = _run(["git", "add", "."], cwd=repo)
    assert stage.returncode == 0, stage.stderr

    # Enable the hook through the real installer (relative path, sandbox cwd).
    install = _run(["bash", "scripts/install_mantis_hooks.sh"], cwd=repo)
    assert install.returncode == 0, install.stderr
    return repo


def run_hook(
    repo: Path,
    cwd: Path | None = None,
    rel: str = ".githooks/post-commit",
) -> subprocess.CompletedProcess[str]:
    """Invoke the hook exactly as git would, with the shim dir on PATH."""
    return _run(
        ["bash", rel],
        cwd=cwd or repo,
        prepend_path=_bash_visible(repo / ".testbin"),
    )


@needs_bash_git
class TestPostCommitHook:
    def test_simulated_commit_runs_fast_check(self, hook_sandbox: Path) -> None:
        """Invoking the hook (as git does post-commit) runs the fast check."""
        pytest.importorskip("jsonschema")  # [status] report needs validation to pass
        result = run_hook(hook_sandbox)

        assert result.returncode == 0, result.stderr
        assert "[mantis] fast security check after commit" in result.stdout
        assert "[mantis] check complete" in result.stdout
        # Artifacts the fast check must produce.
        assert (hook_sandbox / "workspace" / ".mantis_state.json").exists()
        assert (hook_sandbox / "workspace" / "runbook" / "01_history.md").exists()
        assert (hook_sandbox / "workspace" / "runbook" / "16_report.md").exists()
        assert "[status]" in result.stdout  # per-stage status report

    def test_no_real_commit_was_made(self, hook_sandbox: Path) -> None:
        """The simulation never creates a commit in the sandbox repo."""
        head = _run(["git", "rev-list", "--count", "HEAD"], cwd=hook_sandbox)
        assert head.returncode != 0 or head.stdout.strip() == "0"

    def test_skip_mantis_env_disables_hook(self, hook_sandbox: Path) -> None:
        """SKIP_MANTIS=1 makes the hook a silent no-op."""
        # Env inheritance through the spawned bash (WSL interop on Windows) is
        # unreliable, so export the var inside the shell before exec'ing the
        # hook — exactly what `SKIP_MANTIS=1 git commit` does at the command line.
        result = _run(
            ["bash", "-c", "SKIP_MANTIS=1 exec .githooks/post-commit"],
            cwd=hook_sandbox,
            prepend_path=_bash_visible(hook_sandbox / ".testbin"),
        )
        assert result.returncode == 0
        assert "mantis" not in result.stdout.lower()
        assert not (hook_sandbox / "workspace").exists()

    def test_noops_when_runner_missing(self, hook_sandbox: Path) -> None:
        """Without run_mantis.py the hook no-ops and never blocks a commit."""
        (hook_sandbox / "run_mantis.py").unlink()
        result = run_hook(hook_sandbox)
        assert result.returncode == 0
        assert "mantis" not in result.stdout.lower()
        assert not (hook_sandbox / "workspace").exists()

    def test_works_from_subdirectory(self, hook_sandbox: Path) -> None:
        """Hooks can be triggered from subdirs; the hook cds to repo root."""
        sub = hook_sandbox / "backend"
        sub.mkdir()
        result = run_hook(hook_sandbox, cwd=sub, rel="../.githooks/post-commit")
        assert result.returncode == 0, result.stderr
        assert "[mantis] fast security check after commit" in result.stdout
        assert (hook_sandbox / "workspace" / ".mantis_state.json").exists()


@needs_bash_git
class TestInstallerStatus:
    def test_status_reports_installed(self, hook_sandbox: Path) -> None:
        """--status verifies all preconditions inside the sandbox clone."""
        result = _run(["bash", "scripts/install_mantis_hooks.sh", "--status"], cwd=hook_sandbox)
        assert result.returncode == 0
        assert "core.hooksPath" in result.stdout
        assert "INSTALLED" in result.stdout

    def test_status_flags_missing_runner(self, hook_sandbox: Path) -> None:
        """--status reports NOT installed when the runner is removed."""
        (hook_sandbox / "run_mantis.py").unlink()
        result = _run(["bash", "scripts/install_mantis_hooks.sh", "--status"], cwd=hook_sandbox)
        assert result.returncode == 0
        assert "NOT fully installed" in result.stdout
        assert "runner" in result.stdout
        assert "MISSING" in result.stdout
