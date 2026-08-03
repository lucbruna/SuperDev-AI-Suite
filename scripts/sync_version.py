#!/usr/bin/env python3
"""Sync the single-source project version into the suite's metadata files.

Single source of truth: the ``VERSION`` file at the repo root (plain
"X.Y.Z"). The script writes ONLY the suite metadata files:

  - pyproject.toml          (root monorepo)      [project] version
  - backend/pyproject.toml  (FastAPI service)    [project] version
  - package.json            (root monorepo)      top-level "version"
  - frontend/package.json   (Next.js web app)    top-level "version"
  - backend/constants.py    (runtime mirror)     VERSION: Final[str]

Independently versioned packages (sdk/, templates/, builders/, admin-dashboard,
desktop/, extensions/) are intentionally NOT touched.

``backend/constants.py`` VERSION — the value the API exposes at runtime — is
synced too, so ``./VERSION`` stays the single source end to end.

Usage:
  python scripts/sync_version.py           # sync and report
  python scripts/sync_version.py --check   # fail on drift (CI use)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "VERSION"

PYPROJECT_TARGETS = [
    ROOT / "pyproject.toml",
    ROOT / "backend" / "pyproject.toml",
]

PACKAGE_JSON_TARGETS = [
    ROOT / "package.json",
    ROOT / "frontend" / "package.json",
]

# Runtime mirror — the API exposes this; never let it drift from ./VERSION.
CONSTANTS_FILE = ROOT / "backend" / "constants.py"

_PROJECT_HEADER_RE = re.compile(r"^\[project\]\s*$", re.MULTILINE)
_NEXT_SECTION_RE = re.compile(r"^\[", re.MULTILINE)
_VERSION_LINE_RE = re.compile(r'^(?P<indent>\s*)version\s*=\s*"[^"]*"', re.MULTILINE)
_VERSION_KEY_RE = re.compile(r'("version"\s*:\s*")[^"]*(")')
_CONSTANTS_RE = re.compile(r'VERSION\s*:\s*Final\[str\]\s*=\s*"(?P<version>[^"]+)"')
_SAFE_VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def read_source_version() -> str:
    # The first line of VERSION is the single source of truth (bare "X.Y.Z").
    # Any trailing lines are build metadata (comments) and must be ignored.
    first_line = VERSION_FILE.read_text(encoding="utf-8").splitlines()[0].strip()
    if not _SAFE_VERSION.match(first_line):
        sys.exit(f"Invalid version in {VERSION_FILE}: {first_line!r} (expected X.Y.Z)")
    return first_line


def _rel(path: Path) -> str:
    """Path relative to the repo root, falling back to the absolute path."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def sync_pyproject(path: Path, version: str, check: bool) -> None:
    text = path.read_text(encoding="utf-8")
    header = _PROJECT_HEADER_RE.search(text)
    if not header:
        sys.exit(f"{path}: no [project] table found")
    # The version line must live inside the [project] table (before the next
    # section header) so a stray `version = "..."` in a [tool.*] table can
    # never be clobbered.
    section_end = _NEXT_SECTION_RE.search(text, header.end())
    end = section_end.start() if section_end else len(text)
    match = _VERSION_LINE_RE.search(text, header.start(), end)
    if not match:
        sys.exit(f"{path}: no 'version = \"...\"' line inside the [project] table")
    new_text = (
        text[: match.start()]
        + f'{match.group("indent")}version = "{version}"'
        + text[match.end():]
    )
    if check:
        if new_text != text:
            sys.exit(f"{path}: version drifted — run `python scripts/sync_version.py`")
        return
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    print(f"  pyproject    {_rel(path)} -> {version}")


def sync_package_json(path: Path, version: str, check: bool) -> None:
    text = path.read_text(encoding="utf-8")
    match = _VERSION_KEY_RE.search(text)
    if not match:
        sys.exit(f"{path}: no top-level \"version\" key found")
    new_text = f"{text[: match.start()]}{match.group(1)}{version}{match.group(2)}{text[match.end():]}"
    # Guard: result must remain valid JSON.
    json.loads(new_text)
    if check:
        if new_text != text:
            sys.exit(f"{path}: version drifted — run `python scripts/sync_version.py`")
        return
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    print(f"  package.json {_rel(path)} -> {version}")


def sync_constants(path: Path, version: str, check: bool) -> None:
    text = path.read_text(encoding="utf-8")
    match = _CONSTANTS_RE.search(text)
    if not match:
        sys.exit(f"{path}: VERSION constant not found")
    new_text = (
        text[: match.start("version")]
        + version
        + text[match.end("version"):]
    )
    if check:
        if new_text != text:
            sys.exit(
                f"{path}: VERSION={match.group('version')} drifted from {version} "
                f"— run `python scripts/sync_version.py`"
            )
        return
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    print(f"  constants   {_rel(path)} -> {version}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if any metadata drifted from ./VERSION instead of writing",
    )
    args = parser.parse_args()

    version = read_source_version()
    mode = "check" if args.check else "sync"
    print(f"[{mode}] project version: {version}")

    for target in [*PYPROJECT_TARGETS, *PACKAGE_JSON_TARGETS, CONSTANTS_FILE]:
        if not target.exists():
            sys.exit(f"{target}: not found")

    for target in PYPROJECT_TARGETS:
        sync_pyproject(target, version, args.check)
    for target in PACKAGE_JSON_TARGETS:
        sync_package_json(target, version, args.check)
    sync_constants(CONSTANTS_FILE, version, args.check)

    if args.check:
        print("OK: all version metadata matches ./VERSION")
    else:
        print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
