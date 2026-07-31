"""Regression tests for the secrets-detector directory skip fix.

The detector previously failed to skip ``node_modules``/``.git``/``.venv``
during tree traversal because the whitelist patterns (with trailing ``/``)
were matched against directory basenames, so full-tree scans walked every
vendored directory. It now skips known vendor/VCS/venv dir names up front.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from security.secrets_detector.detector import SecretsDetector


def _run(coro):  # noqa: ANN001
    return asyncio.run(coro)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_skips_vendor_and_vcs_dirs(tmp_path: Path) -> None:
    # A very real-looking AWS key inside a vendored dir must NOT be flagged.
    secret = 'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
    _write(tmp_path / "src" / "app.py", "x = 1\n")
    _write(tmp_path / "node_modules" / "dep" / "index.js", secret)
    _write(tmp_path / ".git" / "config", secret)
    _write(tmp_path / ".venv" / "lib" / "site.py", secret)

    detector = SecretsDetector()
    report = _run(detector.analyze(str(tmp_path)))
    paths = [f.file_path for f in report.findings]
    assert not any("node_modules" in p for p in paths)
    assert not any(".git" in p for p in paths)
    assert not any(".venv" in p for p in paths)


def test_still_detects_secrets_in_source(tmp_path: Path) -> None:
    secret = 'aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
    _write(tmp_path / "src" / "app.py", secret)

    detector = SecretsDetector()
    report = _run(detector.analyze(str(tmp_path)))
    assert any("app.py" in f.file_path for f in report.findings)


def test_skip_dir_names_are_effective_set() -> None:
    expected = {"node_modules", ".git", ".venv", "__pycache__", "dist"}
    assert expected <= SecretsDetector.SKIP_DIR_NAMES
