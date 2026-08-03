#!/usr/bin/env python3
"""Validate repository file quality and metadata consistency.

Checks performed (stdlib only, no external dependencies):

  1. ``coverage.json`` is valid JSON with no duplicate keys and contains the
     required top-level keys (``schema_version``, ``totals``, ``files``,
     ``summary``).
  2. ``VERSION`` first line matches ``^\\d+\\.\\d+\\.\\d+$`` (semver).
  3. Every ``__init__.py`` under the core Python packages parses as valid
     Python (via ``ast.parse``).

Exits 0 when all checks pass, 1 otherwise. Intended for CI quality gates and
pre-commit hooks.

Usage:
  python scripts/check_file_quality.py
  python scripts/check_file_quality.py --verbose
  python scripts/check_file_quality.py --path coverage.json
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Packages whose __init__.py files must parse as valid Python.
PACKAGE_ROOTS = ["backend", "agents", "api", "ai_platform", "workflow_engine"]

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_REQUIRED_COVERAGE_KEYS = {"schema_version", "totals", "files", "summary"}


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def check_coverage_json(path: Path, verbose: bool) -> list[str]:
    """Validate coverage.json is well-formed JSON with required keys."""
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
        json.loads(text)  # raises on invalid JSON / duplicate keys
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON ({exc})")
        return errors
    data = json.loads(text)
    missing = _REQUIRED_COVERAGE_KEYS - set(data)
    if missing:
        errors.append(f"{_rel(path)}: missing required keys: {sorted(missing)}")
    if verbose:
        print(f"  coverage.json: OK ({len(errors)} errors)")
    return errors


def check_version(path: Path, verbose: bool) -> list[str]:
    """Validate the first line of VERSION is a bare semver."""
    errors: list[str] = []
    first = path.read_text(encoding="utf-8").splitlines()[0].strip()
    if not _SEMVER_RE.match(first):
        errors.append(f"{_rel(path)}: first line {first!r} is not a valid X.Y.Z version")
    if verbose:
        print(f"  VERSION: first line = {first!r}")
    return errors


def check_init_files(verbose: bool) -> list[str]:
    """Parse every __init__.py under the core packages."""
    errors: list[str] = []
    checked = 0
    for root in PACKAGE_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        for init in base.rglob("__init__.py"):
            checked += 1
            try:
                ast.parse(init.read_text(encoding="utf-8"))
            except SyntaxError as exc:
                errors.append(f"{_rel(init)}: syntax error ({exc})")
    if verbose:
        print(f"  __init__.py: parsed {checked} files")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        help="check a single file (coverage.json or VERSION) instead of the full suite",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print per-check progress"
    )
    args = parser.parse_args()

    errors: list[str] = []

    if args.path:
        target = ROOT / args.path
        if not target.exists():
            print(f"error: {args.path} not found")
            return 1
        if target.name == "coverage.json":
            errors = check_coverage_json(target, args.verbose)
        elif target.name == "VERSION":
            errors = check_version(target, args.verbose)
        else:
            print(f"error: unsupported path {args.path}")
            return 1
    else:
        errors += check_coverage_json(ROOT / "coverage.json", args.verbose)
        errors += check_version(ROOT / "VERSION", args.verbose)
        errors += check_init_files(args.verbose)

    if errors:
        print("File quality check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("OK: all file quality checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())