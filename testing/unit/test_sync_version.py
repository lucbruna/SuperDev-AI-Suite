"""Unit tests for scripts/sync_version.py — single-source version propagation.

Covers: drift detection (--check), section-anchored pyproject replacement,
dependency-range preservation in package.json, and invalid-input rejection.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.sync_version import sync_package_json, sync_pyproject


def test_pyproject_drift_detected_then_synced(tmp_path: Path) -> None:
    f = tmp_path / "pyproject.toml"
    f.write_text(
        '[build-system]\nrequires = ["x"]\n\n[project]\nname = "a"\nversion = "5.0.0"\n\n[tool.other]\nflag = true\n',
        encoding="utf-8",
    )
    # check mode fails on drift
    with pytest.raises(SystemExit):
        sync_pyproject(f, "6.0.0", check=True)
    # sync mode fixes it
    sync_pyproject(f, "6.0.0", check=False)
    assert 'version = "6.0.0"' in f.read_text(encoding="utf-8")
    # check mode passes once in sync
    sync_pyproject(f, "6.0.0", check=True)


def test_pyproject_only_touches_project_table(tmp_path: Path) -> None:
    """A `version = "..."` in a [tool.*] table must never be clobbered."""
    f = tmp_path / "pyproject.toml"
    f.write_text(
        '[tool.other]\nversion = "9.9.9"\n\n[project]\nname = "a"\nversion = "5.0.0"\n',
        encoding="utf-8",
    )
    sync_pyproject(f, "6.0.0", check=False)
    text = f.read_text(encoding="utf-8")
    assert 'version = "9.9.9"' in text  # [tool.other] untouched
    assert 'version = "6.0.0"' in text


def test_pyproject_missing_project_table_rejected(tmp_path: Path) -> None:
    f = tmp_path / "pyproject.toml"
    f.write_text('[tool.other]\nversion = "9.9.9"\n', encoding="utf-8")
    with pytest.raises(SystemExit):
        sync_pyproject(f, "6.0.0", check=False)


def test_package_json_sync_preserves_dependency_ranges(tmp_path: Path) -> None:
    f = tmp_path / "package.json"
    f.write_text(
        json.dumps({"name": "x", "version": "0.1.0", "deps": {"a": "^5.0.0"}}, indent=2),
        encoding="utf-8",
    )
    sync_package_json(f, "6.0.0", check=False)
    data = json.loads(f.read_text(encoding="utf-8"))
    assert data["version"] == "6.0.0"
    assert data["deps"]["a"] == "^5.0.0"  # dependency semver untouched


def test_package_json_missing_version_key_rejected(tmp_path: Path) -> None:
    f = tmp_path / "package.json"
    f.write_text(json.dumps({"name": "x", "deps": {"a": "^5.0.0"}}), encoding="utf-8")
    with pytest.raises(SystemExit):
        sync_package_json(f, "6.0.0", check=False)


def test_package_json_invalid_input_rejected(tmp_path: Path) -> None:
    f = tmp_path / "package.json"
    f.write_text('{"name": "x", "version": "broken', encoding="utf-8")
    with pytest.raises(SystemExit):
        sync_package_json(f, "6.0.0", check=False)
