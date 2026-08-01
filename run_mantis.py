"""run_mantis.py — full-pipeline runner for the Google Mantis skill suite.

Executes the 16 Mantis pipeline stages in sequence (per ``mantis-meta-agent``),
driving the deterministic parts automatically (init, plan, validate, archive)
and delegating each LLM stage by generating its delegation prompt.

Because the Mantis stages are *agent skills* (they read their ``SKILL.md`` and
act), the runner works as a **state machine with resume**:

* It records stage completion in ``workspace/.run_mantis.json``.
* ``run`` walks the pipeline in order; completed stages are skipped, pending
  stages get their delegation prompt printed (and saved to
  ``workspace/runbook/``) for the executing agent to follow.
* ``--auto`` prints every pending stage and advances without waiting;
  ``--interactive`` pauses after each stage and re-checks the expected output
  artifact before continuing.
* ``status`` shows per-stage progress; ``mark``/``reset`` allow manual
  control for resumes and re-runs.

Commands
--------
* ``init``             Bootstrap workspace (delegates to the harness)
* ``plan``             Mode-A crawl → plan.json (delegates to the harness)
* ``run``              Walk the full pipeline in order (resumable)
* ``status``           Show per-stage progress
* ``mark <stage> <done|pending>``  Set one stage's status manually
* ``reset [--stages ...]``  Clear recorded statuses (default: all)
* ``validate``         Validate state/plan/findings against schema.json
* ``archive``          Stage 15: archive findings + increment pass
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Reuse the deterministic harness (control flow + prompts live there).
from scripts import mantis_pipeline as mp

RUNBOOK_DIR = mp.WORKSPACE / "runbook"
PIPELINE_STATE_FILE = mp.WORKSPACE / ".run_mantis.json"

# ── Completion probes (deterministic "did the artifact appear?" checks) ─────
def _finding_files() -> list[Path]:
    """Finding JSON files, excluding dotfiles (single source of truth in the
    harness). pathlib ``glob("*.json")`` matches ``.mantis_state.json``, which
    lives in workspace/findings/ and is NOT a finding."""
    return mp._finding_files()


def stage_complete(stage_name: str, target_root: Path | None = None) -> bool:
    """Return True when the stage's expected output artifact exists."""
    w = mp.WORKSPACE
    root = target_root or mp.ROOT
    if stage_name == "history":
        return (mp.HISTORICAL_LEARNINGS_FILE.exists()
                and mp.HISTORICAL_LEARNINGS_FILE.stat().st_size > 0)
    if stage_name == "structural-index":
        return (w / "kb" / "structural_index" / "manifest.json").exists()
    if stage_name == "summarize":
        # Bounded walk (skip vendor/build/state dirs) — rglob over node_modules
        # would be far too slow on this monorepo.
        try:
            for dirpath, dirnames, filenames in os.walk(root):
                dirnames[:] = [d for d in dirnames if d not in mp.EXCLUDED_DIRS]
                if "mantis-summary.md" in filenames:
                    return True
        except OSError:
            pass
        return False
    if stage_name == "architecture":
        return (w / "kb" / "index.md").exists() and (w / "kb" / "architecture.md").exists()
    if stage_name == "threat-model":
        return (w / "kb" / "THREAT_MODEL.md").exists()
    if stage_name == "plan":
        if not mp.PLAN_FILE.exists():
            return False
        try:
            data = json.loads(mp.PLAN_FILE.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return False
            # Defensive: `investigations: null` must not crash the probe.
            investigations = data.get("investigations") or []
            return len(investigations) > 0
        except (json.JSONDecodeError, OSError, TypeError, AttributeError):
            return False
    if stage_name == "researcher":
        return any(_finding_files())
    if stage_name == "dedupe":
        # Dedupe consolidates duplicate findings; complete when every finding
        # carries a distinct signature (nothing left to consolidate).
        findings = _finding_files()
        if not findings:
            return False
        signatures: set[str] = set()
        for f in findings:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                return False
            if not isinstance(data, dict) or not data.get("signature"):
                return False
            signatures.add(data["signature"])
        return len(signatures) == len(findings)
    if stage_name == "review":
        # Review updates every finding in-place with a `reviewer` history entry.
        findings = _finding_files()
        if not findings:
            return False
        for f in findings:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    return False
                # Defensive: `history: null` (key present, None value), a
                # truthy non-array (e.g. 42), or a non-dict finding must not
                # crash the probe.
                history = data.get("history") or []
                if not isinstance(history, list):
                    return False
                if not any(
                    e.get("stage") == "reviewer" for e in history
                ):
                    return False
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                return False
        return True
    if stage_name == "critic":
        # Critic completes when at least one finding carries the viability
        # verdict (dismissed FALSE_POSITIVEs may be skipped by the driver).
        for f in _finding_files():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                continue
            if isinstance(data, dict) and data.get("critic_reasoning"):
                return True
        return False
    if stage_name == "reproduce":
        if _finding_files() and mp.REPRODUCERS_DIR.exists():
            if any(mp.REPRODUCERS_DIR.iterdir()):
                return True
        return False
    if stage_name == "chain":
        # Chain may legitimately produce zero chain findings (no combinable
        # primitives this pass). Treat the stage as complete when a chain
        # analysis record exists OR any active finding is a chain.
        if (w / "kb" / "chains.md").exists():
            return True
        for f in _finding_files():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                continue
            if isinstance(data, dict) and data.get("constituent_findings"):
                return True
        return False
    if stage_name == "patch":
        findings = _finding_files()
        if not findings:
            return False
        for f in findings:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("patch_diff"):
                    return True
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                continue
        return False
    if stage_name == "calibrate":
        # Calibrate completes when at least one finding carries risk scoring
        # (dismissed FALSE_POSITIVEs are intentionally left unscored).
        findings = _finding_files()
        if not findings:
            return False
        for f in findings:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError, TypeError, AttributeError):
                continue
            if not isinstance(data, dict):
                continue
            if data.get("mantis_risk_score") is not None or data.get("calibration_checklist"):
                return True
        return False
    if stage_name == "reflect":
        return mp.LEARNINGS_FILE.exists() and mp.LEARNINGS_FILE.stat().st_size > 0
    if stage_name == "report":
        return (mp.REPORT_DIR / "review_packet-latest.md").exists()
    return False


# ── Pipeline state file (workspace/.run_mantis.json) ────────────────────────
def load_pipeline_state() -> dict[str, Any]:
    if PIPELINE_STATE_FILE.exists():
        try:
            return json.loads(PIPELINE_STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_pipeline_state(state: dict[str, Any]) -> None:
    PIPELINE_STATE_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )


def stage_statuses() -> dict[str, str]:
    state = load_pipeline_state()
    return state.setdefault("stages", {})


def set_stage(stage_name: str, status: str) -> None:
    state = load_pipeline_state()
    state.setdefault("stages", {})[stage_name] = status
    state["last_updated"] = now_iso()
    save_pipeline_state(state)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Runbook writer ───────────────────────────────────────────────────────────
def write_runbook_prompt(index: int, stage: dict[str, Any], prompt: str) -> Path:
    RUNBOOK_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNBOOK_DIR / f"{index:02d}_{stage['name']}.md"
    path.write_text(prompt + "\n", encoding="utf-8")
    return path


# ── Core: run the pipeline ───────────────────────────────────────────────────
def run_pipeline(args: argparse.Namespace) -> int:
    target = Path(args.target_root).resolve()
    stages = [s for s in mp.STAGES if args.stages is None or s["name"] in args.stages]
    statuses = stage_statuses()
    # Default is automatic (print pending prompts to runbook, advance).
    # --interactive opts into pausing + artifact verification per stage.
    auto = args.auto or not args.interactive
    interactive = args.interactive and not args.auto and not args.dry_run

    # Deterministic prerequisites (delegate to harness).
    if not args.skip_init:
        mp.init_workspace(target)
        print(f"[init] workspace ready at {mp.WORKSPACE}")
    if args.skip_plan:
        print("[plan] skipped (--skip-plan)")
    elif not stage_complete("plan", target):
        plan = mp.write_plan(target)
        print(f"[plan] wrote {plan} (Mode A crawl)")
    else:
        print("[plan] plan.json already has investigations — skipping")

    dry_pending = 0
    for i, stage in enumerate(stages, start=1):
        name = stage["name"]
        recorded = statuses.get(name)
        if recorded == "done" or stage_complete(name, target):
            if recorded != "done":
                statuses[name] = "done"
            print(f"[{i:02d}/{len(stages)}] {name:16s} done")
            continue

        prompt = mp.stage_prompt(name, target)
        book = write_runbook_prompt(i, stage, prompt)
        print(f"[{i:02d}/{len(stages)}] {name:16s} PENDING -> {book.relative_to(mp.WORKSPACE).as_posix()}")
        if args.dry_run:
            dry_pending += 1
            continue
        if interactive:
            print(prompt)
            try:
                input(f"  Execute stage '{name}' now, then press Enter to verify... ")
            except EOFError:
                break
            if stage_complete(name, target):
                statuses[name] = "done"
                print(f"  -> {name} verified complete")
            else:
                print(f"  -> {name} artifact not detected; marking pending (use 'mark {name} done' if it ran)")
                continue
        else:
            statuses[name] = "pending"

    if args.dry_run:
        print(f"\n[dry-run] {dry_pending} stage(s) would run; prompts saved under workspace/runbook/")
        return 0

    # Persist statuses.
    state = load_pipeline_state()
    state["stages"] = statuses
    state["last_updated"] = now_iso()
    save_pipeline_state(state)

    # Validate what exists so far.
    errors = mp.validate_artifacts()
    if errors:
        print(f"\n[validate] {len(errors)} error(s):")
        for e in errors:
            print(f"  [FAIL] {e}")
        return 1
    print("[validate] artifacts valid against schema.json [OK]")

    # Remaining check spans ALL stages (not just the --stages filter) so a
    # partial run can never trigger a premature Stage-15 archive.
    all_statuses = {s["name"]: statuses.get(s["name"], "pending") for s in mp.STAGES}
    remaining = [n for n, s in all_statuses.items() if s != "done"]
    if remaining:
        print(f"\n[status] {len(remaining)} stage(s) pending: {', '.join(remaining)}")
        print("[status] Re-run `python run_mantis.py run --auto` after executing them to advance.")
        return 0

    # Archive + increment pass (Stage 15).
    if not args.no_archive:
        result = mp.archive_pass()
        print(f"[archive] pass {result['archived_pass']} -> pass {result['new_pass']} "
              f"({result['moved_findings']} findings archived)")
        # Reset stage statuses for the next pass (load once, mutate once, save once).
        state = load_pipeline_state()
        state["stages"] = {s["name"]: "pending" for s in mp.STAGES}
        state["last_updated"] = now_iso()
        save_pipeline_state(state)
    print("\n[run] pipeline pass complete.")
    return 0


# ── Status ───────────────────────────────────────────────────────────────────
def print_pipeline_status(target_root: Path | None = None) -> None:
    statuses = stage_statuses()
    target = target_root or mp.ROOT
    done_count = 0
    for stage in mp.STAGES:
        name = stage["name"]
        recorded = statuses.get(name)
        complete = stage_complete(name, target)
        if recorded == "done" or complete:
            state_label = "done"
            done_count += 1
        else:
            state_label = "pending"
        marker = "[x]" if state_label == "done" else "[ ]"
        hint = " (artifact detected)" if complete and recorded != "done" else ""
        print(f"  {marker} {name:16s} {state_label:8s}{hint}")
    print(f"\n{done_count}/{len(mp.STAGES)} stages complete")
    print(f"pipeline state: {PIPELINE_STATE_FILE}")


# ── CLI ──────────────────────────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run-mantis",
        description="Full-pipeline runner for the Google Mantis security-review skills.",
    )
    parser.add_argument("--state-root", default=str(mp.STATE_ROOT),
                        help="Directory that contains workspace/ (default: repo root)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Walk the full pipeline in order (resumable)")
    p_run.add_argument("--target-root", default=str(mp.ROOT), help="Code root to audit")
    p_run.add_argument("--stages", nargs="*", default=None,
                       help="Only run these stages (default: all 16)")
    p_run.add_argument("--auto", action="store_true",
                       help="Print pending prompts and advance without waiting")
    p_run.add_argument("--interactive", action="store_true",
                       help="Pause after each stage and verify its output artifact")
    p_run.add_argument("--dry-run", action="store_true",
                       help="Print the runbook without executing or waiting")
    p_run.add_argument("--skip-init", action="store_true", help="Do not bootstrap the workspace")
    p_run.add_argument("--skip-plan", action="store_true", help="Do not regenerate plan.json")
    p_run.add_argument("--no-archive", action="store_true",
                       help="Do not run Stage 15 (archive) at the end")

    sub.add_parser("init", help="Bootstrap the workspace (delegates to harness)")
    sub.add_parser("plan", help="Mode-A crawl -> plan.json (delegates to harness)")
    sub.add_parser("validate", help="Validate state/plan/findings against schema.json")
    sub.add_parser("archive", help="Stage 15: archive findings + increment pass")

    p_status = sub.add_parser("status", help="Show per-stage progress")
    p_status.add_argument("--target-root", default=str(mp.ROOT), help="Code root (for artifact probes)")

    p_mark = sub.add_parser("mark", help="Set one stage's status manually")
    p_mark.add_argument("stage", help="Stage name")
    p_mark.add_argument("status", choices=["done", "pending"], help="New status")

    p_reset = sub.add_parser("reset", help="Clear recorded stage statuses")
    p_reset.add_argument("--stages", nargs="*", default=None,
                         help="Only reset these stages (default: all)")

    return parser


def main(argv: list[str] | None = None) -> int:
    global RUNBOOK_DIR, PIPELINE_STATE_FILE
    # Windows consoles often default to cp1252; force UTF-8.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    if getattr(args, "state_root", None):
        mp.STATE_ROOT = Path(args.state_root)
        mp.WORKSPACE = mp.STATE_ROOT / "workspace"
        mp.STATE_FILE = mp.WORKSPACE / ".mantis_state.json"
        mp.PLAN_FILE = mp.WORKSPACE / "plan.json"
        mp.FINDINGS_DIR = mp.WORKSPACE / "findings"
        mp.KB_DIR = mp.WORKSPACE / "kb"
        mp.ARCHIVE_DIR = mp.WORKSPACE / "archive"
        mp.REPORT_DIR = mp.WORKSPACE / "report"
        mp.HELPERS_DIR = mp.WORKSPACE / "helpers"
        mp.REPRODUCERS_DIR = mp.WORKSPACE / "reproducers"
        mp.LEARNINGS_FILE = mp.WORKSPACE / "learnings.jsonl"
        mp.HISTORICAL_LEARNINGS_FILE = mp.WORKSPACE / "historical_learnings.jsonl"
        RUNBOOK_DIR = mp.WORKSPACE / "runbook"
        PIPELINE_STATE_FILE = mp.WORKSPACE / ".run_mantis.json"

    if args.command == "run":
        return run_pipeline(args)

    if args.command == "init":
        target = Path(getattr(args, "target_root", str(mp.ROOT))).resolve()
        state = mp.init_workspace(target)
        print(f"Workspace initialized at {mp.WORKSPACE}")
        print(f"pass_number: {state['pass_number']}, vcs_type: {state['vcs_info'].get('vcs_type')}")
        return 0

    if args.command == "plan":
        target = Path(getattr(args, "target_root", str(mp.ROOT))).resolve()
        plan_path = mp.write_plan(target)
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        print(f"Wrote {plan_path} with {len(plan['investigations'])} investigations")
        return 0

    if args.command == "validate":
        errors = mp.validate_artifacts()
        if errors:
            for e in errors:
                print(f"  [FAIL] {e}")
            print(f"\n{len(errors)} validation error(s)")
            return 1
        print("All artifacts valid against schema.json [OK]")
        return 0

    if args.command == "archive":
        result = mp.archive_pass()
        print(f"Archived pass {result['archived_pass']} ({result['moved_findings']} findings) -> pass {result['new_pass']}")
        return 0

    if args.command == "status":
        target = Path(getattr(args, "target_root", str(mp.ROOT))).resolve()
        print_pipeline_status(target)
        return 0

    if args.command == "mark":
        set_stage(args.stage, args.status)
        print(f"mark: {args.stage} = {args.status}")
        return 0

    if args.command == "reset":
        state = load_pipeline_state()
        # Note: use state.setdefault() here — stage_statuses() re-reads the
        # file from disk, returning a DIFFERENT dict than the one loaded above
        # (mutating it would not affect the state that gets saved).
        if args.stages:
            stages = state.setdefault("stages", {})
            for s in args.stages:
                stages.pop(s, None)
        else:
            state.pop("stages", None)
        save_pipeline_state(state)
        print("reset: stage statuses cleared")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
