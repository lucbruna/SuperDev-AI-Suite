"""Mantis pipeline harness — deterministic orchestrator for the Google Mantis skills.

This harness wraps the 18 `google/mantis` agent skills installed under
``.agents/skills/mantis-*`` and implements the reference architecture from the
``mantis-pipeline-adapter`` skill:

* **Deterministic orchestration**: control flow lives in code, not in the LLM.
* **State on disk**: ``workspace/`` is the single source of truth
  (``.mantis_state.json``, ``plan.json``, ``findings/*.json``, ``kb/``).
* **Delegation prompts**: the harness cannot run LLM stages itself; it
  *generates the exact delegation instruction* for each stage (reading the
  stage's ``SKILL.md``) so a meta-agent / sub-agent can execute it.

Commands
--------
* ``init``            Create the workspace tree + ``.mantis_state.json``
* ``plan``            Mode-A crawl of production source → ``workspace/plan.json``
* ``prompt <stage>``  Print the delegation prompt for one pipeline stage
* ``status``          Print a compact summary of the current pass
* ``validate``        Validate state/plan/findings against ``schema.json``
* ``archive``         Stage 15: archive findings, bump pass number

All commands operate relative to the repository root (the parent of
``workspace/``), which is ``--state_root``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
STATE_ROOT = Path(os.getenv("MANTIS_STATE_ROOT", ROOT))
WORKSPACE = STATE_ROOT / "workspace"
SCHEMA_PATH = ROOT / ".agents" / "skills" / "schema.json"
SKILLS_DIR = ROOT / ".agents" / "skills"

STATE_FILE = WORKSPACE / ".mantis_state.json"
PLAN_FILE = WORKSPACE / "plan.json"
FINDINGS_DIR = WORKSPACE / "findings"
KB_DIR = WORKSPACE / "kb"
ARCHIVE_DIR = WORKSPACE / "archive"
REPORT_DIR = WORKSPACE / "report"
HELPERS_DIR = WORKSPACE / "helpers"
REPRODUCERS_DIR = WORKSPACE / "reproducers"
LEARNINGS_FILE = WORKSPACE / "learnings.jsonl"
HISTORICAL_LEARNINGS_FILE = WORKSPACE / "historical_learnings.jsonl"

# Extension → language map used by the Mode-A crawler.
SOURCE_EXTS = {
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".cxx": "cpp", ".hpp": "cpp",
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".ts": "typescript",
    ".tsx": "typescript", ".go": "go", ".rs": "rust", ".java": "java",
    ".rb": "ruby", ".php": "php", ".kt": "kotlin", ".swift": "swift",
    ".cs": "csharp", ".sh": "bash", ".sql": "sql",
}

# Directories always excluded from the crawl (vendor/build/test/state).
EXCLUDED_DIRS = {
    ".git", ".hg", ".repo", ".svn", ".idea", ".vscode", ".next", ".nuxt",
    "node_modules", "dist", "build", "out", "target", "vendor", "third_party",
    "venv", ".venv", "env", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".agents", ".mantis_snapshots", "workspace", ".terraform",
    "coverage", "htmlcov", ".slim", "tmp", "temp", "loadtests", "tests", "test",
    "testing", "migrations", "alembic", ".docker", "staticfiles", "media",
}

# All 18 stages in pipeline order, with skill dir name + delegation arg hints.
STAGES: list[dict[str, Any]] = [
    {"name": "history",           "skill": "mantis-history",           "needs_code": True,  "output": "workspace/historical_learnings.jsonl"},
    {"name": "structural-index",  "skill": "mantis-structural-index",  "needs_code": True,  "output": "workspace/kb/structural_index/"},
    {"name": "summarize",         "skill": "mantis-summarize",         "needs_code": True,  "output": "mantis-summary.md files"},
    {"name": "architecture",      "skill": "mantis-architecture",      "needs_code": True,  "output": "workspace/kb/"},
    {"name": "threat-model",      "skill": "mantis-threat-model",      "needs_code": False, "output": "workspace/kb/THREAT_MODEL.md"},
    {"name": "plan",              "skill": "mantis-plan",              "needs_code": True,  "output": "workspace/plan.json"},
    {"name": "researcher",        "skill": "mantis-researcher",        "needs_code": True,  "output": "workspace/findings/<uuid>.json"},
    {"name": "dedupe",            "skill": "mantis-dedupe",            "needs_code": False, "output": "workspace/findings/ (merged)"},
    {"name": "review",            "skill": "mantis-review",            "needs_code": True,  "output": "workspace/findings/ (status updated)"},
    {"name": "critic",            "skill": "mantis-critic",            "needs_code": True,  "output": "workspace/findings/ (viability)"},
    {"name": "reproduce",         "skill": "mantis-reproduce",         "needs_code": True,  "output": "workspace/reproducers/ + findings"},
    {"name": "chain",             "skill": "mantis-chain",             "needs_code": False, "output": "workspace/findings/ (super findings)"},
    {"name": "patch",             "skill": "mantis-patch",             "needs_code": True,  "output": "workspace/findings/ (patch_diff)"},
    {"name": "calibrate",         "skill": "mantis-calibrate",         "needs_code": False, "output": "workspace/findings/ (risk scores)"},
    {"name": "reflect",           "skill": "mantis-reflect",           "needs_code": False, "output": "workspace/learnings.jsonl"},
    {"name": "report",            "skill": "mantis-report",            "needs_code": False, "output": "workspace/report/review_packet-latest.md"},
]

STAGE_BY_NAME = {s["name"]: s for s in STAGES}


# ── VCS detection (mirrors meta-agent Block A) ───────────────────────────────
def detect_vcs(target_root: Path) -> dict[str, Any]:
    """Detect VCS state of ``target_root``, mirroring meta-agent Block A."""
    vcs: dict[str, Any] = {"vcs_type": "none", "dirty": False}
    try:
        git_root = subprocess.run(
            ["git", "-C", str(target_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=15,
        )
        if git_root.returncode == 0 and git_root.stdout.strip() == "true":
            vcs["vcs_type"] = "git"
            vcs["commit_hash"] = subprocess.run(
                ["git", "-C", str(target_root), "rev-parse", "HEAD"],
                capture_output=True, text=True, timeout=15,
            ).stdout.strip() or None
            vcs["branch"] = subprocess.run(
                ["git", "-C", str(target_root), "branch", "--show-current"],
                capture_output=True, text=True, timeout=15,
            ).stdout.strip() or None
            porcelain = subprocess.run(
                ["git", "-C", str(target_root), "status", "--porcelain",
                 "--", ":(exclude)**/mantis-summary.md",
                 ":(exclude)**/*.bak-*", ":(exclude)workspace/",
                 ":(exclude).mantis_snapshots/"],
                capture_output=True, text=True, timeout=15,
            ).stdout
            vcs["dirty"] = bool(porcelain.strip())
            return vcs
    except (subprocess.SubprocessError, OSError):
        pass
    if (target_root / ".hg").exists():
        vcs["vcs_type"] = "hg"
        for cmd, key in ((["hg", "-R", str(target_root), "id", "-i"], "commit_hash"),
                         (["hg", "-R", str(target_root), "branch"], "branch")):
            try:
                out = subprocess.run(cmd, capture_output=True, text=True, timeout=15).stdout.strip()
                vcs[key] = out or None
            except (subprocess.SubprocessError, OSError):
                pass
    if (target_root / ".repo").exists():
        vcs["vcs_type"] = "multi-vcs"
    return vcs


# ── State file ───────────────────────────────────────────────────────────────
def load_state() -> dict[str, Any]:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict[str, Any]) -> None:
    STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_state(target_root: Path) -> dict[str, Any]:
    state = load_state()
    state.setdefault("pass_number", 1)
    state["last_updated"] = now_iso()
    state["vcs_info"] = detect_vcs(target_root)
    save_state(state)
    return state


# ── Workspace bootstrap ──────────────────────────────────────────────────────
def workspace_dirs() -> list[Path]:
    """Return workspace dirs, computed lazily so ``--state-root`` overrides apply."""
    return [
        WORKSPACE, FINDINGS_DIR, FINDINGS_DIR / ".trash", KB_DIR, KB_DIR / "entities",
        KB_DIR / "vulnerabilities", KB_DIR / "structural_index", ARCHIVE_DIR,
        ARCHIVE_DIR / "kb", ARCHIVE_DIR / "findings_pass_1", REPORT_DIR,
        HELPERS_DIR, REPRODUCERS_DIR,
    ]


def init_workspace(target_root: Path) -> dict[str, Any]:
    for d in workspace_dirs():
        d.mkdir(parents=True, exist_ok=True)
    if not PLAN_FILE.exists():
        PLAN_FILE.write_text(
            json.dumps({"investigations": []}, indent=2) + "\n", encoding="utf-8",
        )
    for f in (LEARNINGS_FILE, HISTORICAL_LEARNINGS_FILE):
        if not f.exists():
            f.touch()
    state = init_state(target_root)
    return state


# ── Mode-A crawl → plan.json ─────────────────────────────────────────────────
def crawl_production_files(target_root: Path) -> list[Path]:
    """Return production source files, excluding tests/vendor/build/state dirs."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(target_root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix.lower() in SOURCE_EXTS and not name.startswith("test_"):
                files.append(p)
    return sorted(files)


def write_plan(target_root: Path) -> Path:
    """Mode A: build a baseline ``plan.json`` from a crawl of production code."""
    files = crawl_production_files(target_root)
    investigations: list[dict[str, Any]] = []
    if files:
        for f in files:
            rel = f.relative_to(target_root).as_posix()
            investigations.append({
                "title": f"Exhaustive Review: {rel}",
                "target_files": [rel],
                "kb_references": [],
                "question": (
                    "Conduct a baseline security audit of this file: trace input "
                    "pathways, validate all boundary/parsing logic, check for "
                    "memory-safety, injection, authz and logic flaws, and report "
                    "concrete findings with code_paths and repro hints."
                ),
            })
    plan = {"investigations": investigations}
    PLAN_FILE.write_text(
        json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    return PLAN_FILE


# ── Delegation prompt generator ──────────────────────────────────────────────
def read_skill_description(skill_dir: Path) -> str:
    """Extract the ``description`` frontmatter value, handling YAML ``>-`` blocks."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith("description:") and i + 1 < len(lines):
            rest = line.split(":", 1)[1].strip()
            if rest in {">", "|>", ">-", "|-"} and lines[i + 1].strip():
                return lines[i + 1].strip().strip('"')
            if rest:
                return rest.strip('"')
    return ""


def stage_prompt(stage_name: str, target_root: Path | None = None) -> str:
    stage = STAGE_BY_NAME.get(stage_name)
    if not stage:
        known = ", ".join(s["name"] for s in STAGES)
        raise SystemExit(f"Unknown stage '{stage_name}'. Known stages: {known}")
    skill_dir = SKILLS_DIR / stage["skill"]
    skill_desc = read_skill_description(skill_dir)
    args = f"--state_root={STATE_ROOT}"
    if target_root is not None:
        args += f" --target_root={target_root}"
    state = load_state()
    pass_number = state.get("pass_number", 1)
    lines = [
        f"# Stage: {stage_name} ({stage['skill']})",
        f"**Command:** `/mantis-{stage_name}`",
        "",
        f"**Goal:** {skill_desc or 'Run this Mantis pipeline stage.'}",
        f"**Flags:** `{args}`",
        f"**Pass:** {pass_number}",
        "",
        "**Delegation instruction for the executing agent:**",
        "",
        f"1. Load the skill instructions from `{skill_dir.as_posix()}/SKILL.md` "
        f"and follow them exactly.",
        f"2. Read/write state under `{WORKSPACE.as_posix()}/` (STATE-RELATIVE).",
    ]
    if stage["needs_code"] and target_root is not None:
        lines.append(f"3. Read target code under `{target_root}` (CODE_ROOT). Never write there.")
        lines.append("4. Write the stage output and report back a short JSON status.")
    else:
        lines.append("3. This is a findings-only stage: never read target source code.")
        lines.append("4. Write the stage output and report back a short JSON status.")
    lines.append("")
    lines.append(f"**Expected output:** {stage['output']}")
    return "\n".join(lines)


# ── Status ───────────────────────────────────────────────────────────────────
def _finding_files() -> list[Path]:
    """Finding JSONs, excluding dotfiles.

    pathlib ``glob("*.json")`` matches ``.mantis_state.json`` if one ever ends
    up in workspace/findings/; validation, status and archive must never treat
    it as a finding.
    """
    if not FINDINGS_DIR.exists():
        return []
    return [f for f in sorted(FINDINGS_DIR.glob("*.json")) if not f.name.startswith(".")]


def print_status() -> None:
    state = load_state()
    vcs = state.get("vcs_info", {})
    findings = _finding_files()
    print(f"state_root   : {STATE_ROOT}")
    print(f"pass_number  : {state.get('pass_number', 1)}")
    print(f"last_updated : {state.get('last_updated', '-')}")
    print(f"vcs_type     : {vcs.get('vcs_type', 'none')}")
    if vcs.get("commit_hash"):
        print(f"commit_hash  : {vcs.get('commit_hash')}")
    if vcs.get("branch"):
        print(f"branch       : {vcs.get('branch')}")
    print(f"dirty        : {vcs.get('dirty', False)}")
    print(f"active_findings: {len(findings)}")
    plan_exists = PLAN_FILE.exists()
    inv_count = 0
    if plan_exists:
        try:
            inv_count = len(json.loads(PLAN_FILE.read_text(encoding="utf-8")).get("investigations", []))
        except (json.JSONDecodeError, OSError):
            pass
    print(f"plan.json    : {'yes' if plan_exists else 'no'} ({inv_count} investigations)")


# ── Validation against schema.json ───────────────────────────────────────────
def validate_artifacts() -> list[str]:
    errors: list[str] = []
    if not SCHEMA_PATH.exists():
        return [f"schema.json not found at {SCHEMA_PATH}"]
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema is not installed; run `pip install jsonschema`"]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    targets: list[tuple[str, dict[str, Any], str]] = []
    for path, label, ref in (
        (STATE_FILE, "state", "#/$defs/state"),
        (PLAN_FILE, "plan", "#/$defs/plan"),
    ):
        if path.exists():
            try:
                targets.append((label, json.loads(path.read_text(encoding="utf-8")), ref))
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON ({exc})")
    for f in _finding_files():
        try:
            targets.append((f.name, json.loads(f.read_text(encoding="utf-8")), "#/$defs/finding"))
        except json.JSONDecodeError as exc:
            errors.append(f"{f.name}: invalid JSON ({exc})")

    for name, data, ref in targets:
        sub = validator.evolve(schema={"$ref": ref})
        for err in sorted(sub.iter_errors(data), key=lambda e: [str(x) for x in e.path]):
            errors.append(f"{name}: {err.message} (at {'/'.join(map(str, err.path)) or '$'})")
    return errors


# ── Stage 15: archive + increment pass ───────────────────────────────────────
def _ignore_structural_cache(directory: str, names: list[str]) -> set[str]:
    """copytree ignore: only skip the rebuildable structural-index cache."""
    if os.path.basename(directory) == "structural_index":
        return {"units", "tmp"}
    return set()


def archive_pass() -> dict[str, Any]:
    state = load_state()
    n = int(state.get("pass_number", 1))
    archive = ARCHIVE_DIR / f"findings_pass_{n}"
    archive.mkdir(parents=True, exist_ok=True)
    moved = 0

    # State + KB snapshot (copy, never move).
    if STATE_FILE.exists():
        shutil.copy2(STATE_FILE, archive / ".mantis_state.json")
    if KB_DIR.exists():
        # Exclude the rebuildable content-addressed structural-index cache
        # (45k+ tiny JSON files in units/; copying it on OneDrive made every
        # archive/pass transition time out). The manifest + catalog.sqlite
        # carry provenance and the units are regenerable, so nothing is lost.
        # Scoped to the structural_index dir so any legit units/tmp dirs
        # elsewhere under kb/ (e.g. entities/) are never dropped.
        shutil.copytree(
            KB_DIR,
            archive / "kb",
            dirs_exist_ok=True,
            ignore=_ignore_structural_cache,
        )

    # Move findings (never the dotfile state copy that may live beside them).
    for f in _finding_files():
        f.replace(archive / f.name)
        moved += 1
    if FINDINGS_DIR.exists():
        trash = FINDINGS_DIR / ".trash"
        if trash.exists() and any(trash.iterdir()):
            trash_target = archive / ".trash"
            trash_target.mkdir(exist_ok=True)
            for f in trash.iterdir():
                f.replace(trash_target / f.name)

    # Increment pass.
    state["pass_number"] = n + 1
    state["last_updated"] = now_iso()
    save_state(state)
    return {"archived_pass": n, "new_pass": n + 1, "moved_findings": moved}


# ── CLI ──────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mantis-pipeline",
        description="Deterministic orchestrator harness for the Google Mantis security skills.",
    )
    parser.add_argument("--state-root", default=str(STATE_ROOT),
                        help="Directory that contains workspace/ (default: repo root)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create the workspace tree + state file")
    p_init.add_argument("--target-root", default=str(ROOT), help="Code root to audit (default: repo root)")

    p_plan = sub.add_parser("plan", help="Mode-A crawl → write workspace/plan.json")
    p_plan.add_argument("--target-root", default=str(ROOT), help="Code root to crawl")

    p_prompt = sub.add_parser("prompt", help="Print the delegation prompt for one stage")
    p_prompt.add_argument("stage", help="Stage name (e.g. researcher, review, patch)")
    p_prompt.add_argument("--target-root", default=str(ROOT), help="Code root (CODE_ROOT)")

    sub.add_parser("status", help="Print a compact pipeline summary")
    sub.add_parser("validate", help="Validate state/plan/findings against schema.json")

    p_archive = sub.add_parser("archive", help="Stage 15: archive findings + increment pass")

    return parser


def main(argv: list[str] | None = None) -> int:
    global STATE_ROOT, WORKSPACE, STATE_FILE, PLAN_FILE, FINDINGS_DIR, KB_DIR, \
        ARCHIVE_DIR, REPORT_DIR, HELPERS_DIR, REPRODUCERS_DIR, LEARNINGS_FILE, \
        HISTORICAL_LEARNINGS_FILE
    # Windows consoles often default to cp1252; force UTF-8 so skill-derived
    # text (paths, descriptions) can never crash a print statement.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    if getattr(args, "state_root", None):
        STATE_ROOT = Path(args.state_root)
        WORKSPACE = STATE_ROOT / "workspace"
        STATE_FILE = WORKSPACE / ".mantis_state.json"
        PLAN_FILE = WORKSPACE / "plan.json"
        FINDINGS_DIR = WORKSPACE / "findings"
        KB_DIR = WORKSPACE / "kb"
        ARCHIVE_DIR = WORKSPACE / "archive"
        REPORT_DIR = WORKSPACE / "report"
        HELPERS_DIR = WORKSPACE / "helpers"
        REPRODUCERS_DIR = WORKSPACE / "reproducers"
        LEARNINGS_FILE = WORKSPACE / "learnings.jsonl"
        HISTORICAL_LEARNINGS_FILE = WORKSPACE / "historical_learnings.jsonl"

    if args.command == "init":
        target = Path(args.target_root).resolve()
        state = init_workspace(target)
        print(f"Workspace initialized at {WORKSPACE}")
        print(f"pass_number: {state['pass_number']}, vcs_type: {state['vcs_info'].get('vcs_type')}")
        return 0

    if args.command == "plan":
        target = Path(args.target_root).resolve()
        plan_path = write_plan(target)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        print(f"Wrote {plan_path} with {len(plan['investigations'])} investigations")
        return 0

    if args.command == "prompt":
        target = Path(args.target_root).resolve() if getattr(args, "target_root", None) else None
        print(stage_prompt(args.stage, target))
        return 0

    if args.command == "status":
        print_status()
        return 0

    if args.command == "validate":
        errors = validate_artifacts()
        if errors:
            for e in errors:
                print(f"  [FAIL] {e}")
            print(f"\n{len(errors)} validation error(s)")
            return 1
        print("All artifacts valid against schema.json [OK]")
        return 0

    if args.command == "archive":
        result = archive_pass()
        print(f"Archived pass {result['archived_pass']} ({result['moved_findings']} findings) -> pass {result['new_pass']}")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
