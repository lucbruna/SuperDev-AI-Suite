"""Git scanner: reads repository state through the git CLI (read-only).

Provides the data used by the evolution analyzer and the discovery engine:
current head, recent commits, changed files and the full tracked file list.
All calls are wrapped so a missing/offline git never breaks a scan.
"""
from __future__ import annotations

import subprocess
from typing import Any


def _run(cmd: list[str], root: str) -> str:
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, cwd=root, timeout=30,
            check=False,
        )
        return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def scan(root: str) -> dict[str, Any]:
    """Return git repository metadata + change information."""
    head = _run(["git", "rev-parse", "--short", "HEAD"], root)
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)

    log = _run(["git", "log", "--oneline", "-30"], root)
    commits: list[dict[str, str]] = []
    for line in log.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            commits.append({"hash": parts[0], "subject": parts[1]})

    status = _run(["git", "status", "--porcelain"], root)
    changed: list[dict[str, str]] = []
    for line in status.splitlines():
        if len(line) > 3:
            changed.append({"status": line[:2].strip(), "path": line[3:]})

    tracked = [
        line for line in _run(["git", "ls-files"], root).splitlines() if line
    ]

    return {
        "available": bool(head),
        "head": head,
        "branch": branch,
        "recent_commits": commits,
        "changed_files": changed,
        "tracked_files": tracked,
    }
