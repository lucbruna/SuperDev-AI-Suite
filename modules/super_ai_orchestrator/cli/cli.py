"""CLI entry point for the Super AI Orchestrator (stdlib argparse only)."""
from __future__ import annotations

import argparse
import json

from modules.super_ai_orchestrator.api import OrchestratorAPI


def _parse_value(raw: str):
    """Parse a CLI string as JSON when possible, else keep the string."""
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return raw


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="orchestrator",
        description="Super AI Orchestrator Core - deterministic task orchestration.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show orchestrator status.")
    sub.add_parser("health", help="Show health assessment.")
    sub.add_parser("metrics", help="Show metric surface.")
    sub.add_parser("analytics", help="Show execution analytics.")
    sub.add_parser("audit", help="Show the audit trail.")
    sub.add_parser("governance", help="Show the governance policy.")
    sub.add_parser("config", help="Show effective configuration.")
    sub.add_parser("dashboard", help="Show the dashboard payload.")
    sub.add_parser("integrations", help="List connector availability.")

    submit = sub.add_parser("submit", help="Submit a task.")
    submit.add_argument("kind")
    submit.add_argument("title")
    submit.add_argument("--payload-json", default="{}", help="Task payload as JSON.")
    submit.add_argument("--priority", type=int, help="Urgency 1..10.")
    submit.add_argument("--owner-hint", help="Preferred owner agent.")
    submit.add_argument(
        "--require-approval", dest="require_approval", action="store_true",
        help="Force the governance gate.",
    )
    submit.add_argument(
        "--no-approval", dest="require_approval", action="store_false",
        help="Bypass the governance gate.",
    )
    submit.set_defaults(require_approval=None)

    tick = sub.add_parser("tick", help="Advance the kernel scheduler.")
    tick.add_argument("--slices", type=int, help="Work slices to process.")

    approve = sub.add_parser("approve", help="Approve a gated task.")
    approve.add_argument("seq", type=int)
    reject = sub.add_parser("reject", help="Reject a gated task.")
    reject.add_argument("seq", type=int)
    reject.add_argument("--reason", default="rejected by CLI")
    cancel = sub.add_parser("cancel", help="Cancel a queued task.")
    cancel.add_argument("seq", type=int)
    pause = sub.add_parser("pause", help="Pause a scheduled task.")
    pause.add_argument("seq", type=int)
    resume = sub.add_parser("resume", help="Resume a paused task.")
    resume.add_argument("seq", type=int)
    rollback = sub.add_parser("rollback", help="Roll back a failed task.")
    rollback.add_argument("seq", type=int)
    task = sub.add_parser("task", help="Show one task.")
    task.add_argument("seq", type=int)

    tasks = sub.add_parser("tasks", help="List tasks.")
    tasks.add_argument("--status", help="Filter by status.")

    events = sub.add_parser("events", help="Show recorded events.")
    events.add_argument("--type", help="Filter by event type.")

    invoke = sub.add_parser("invoke", help="Invoke a connector action.")
    invoke.add_argument("name")
    invoke.add_argument("--action", default="invoke")
    invoke.add_argument(
        "--kw", action="append", default=[], metavar="KEY=VALUE",
        help="Keyword argument (repeatable); values parsed as JSON when possible.",
    )

    memory_set = sub.add_parser("memory-set", help="Remember a value.")
    memory_set.add_argument("namespace")
    memory_set.add_argument("key")
    memory_set.add_argument("value")
    memory_get = sub.add_parser("memory-get", help="Recall a value.")
    memory_get.add_argument("namespace")
    memory_get.add_argument("key")
    memory_del = sub.add_parser("memory-del", help="Forget a value.")
    memory_del.add_argument("namespace")
    memory_del.add_argument("key")
    memory_keys = sub.add_parser("memory-keys", help="List keys in a namespace.")
    memory_keys.add_argument("namespace")
    sub.add_parser("memory-namespaces", help="List memory namespaces.")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    api = OrchestratorAPI()
    try:
        result = _dispatch(api, args)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (KeyError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2, sort_keys=True))
        return 1


def _dispatch(api: OrchestratorAPI, args: argparse.Namespace):
    command = args.command
    if command == "status":
        return api.status()
    if command == "health":
        return api.health()
    if command == "metrics":
        return api.metrics()
    if command == "analytics":
        return api.analytics_report()
    if command == "audit":
        return api.audit()
    if command == "governance":
        return api.governance_policy()
    if command == "config":
        return api.config_dict()
    if command == "dashboard":
        return api.dashboard()
    if command == "integrations":
        return api.integrations()
    if command == "submit":
        return api.submit(
            kind=args.kind,
            title=args.title,
            payload=_parse_value(args.payload_json),
            priority=args.priority,
            owner_hint=args.owner_hint,
            require_approval=args.require_approval,
        )
    if command == "tick":
        return api.tick(args.slices)
    if command == "approve":
        return api.approve(args.seq)
    if command == "reject":
        return api.reject(args.seq, args.reason)
    if command == "cancel":
        return api.cancel(args.seq)
    if command == "pause":
        return api.pause(args.seq)
    if command == "resume":
        return api.resume(args.seq)
    if command == "rollback":
        return api.rollback(args.seq)
    if command == "task":
        return api.get(args.seq)
    if command == "tasks":
        return api.tasks(args.status)
    if command == "events":
        return api.events(args.type)
    if command == "invoke":
        kwargs = {}
        for item in args.kw:
            if "=" in item:
                key, raw = item.split("=", 1)
                kwargs[key] = _parse_value(raw)
        return api.invoke(args.name, args.action, **kwargs)
    if command == "memory-set":
        return api.memory_remember(args.namespace, args.key, _parse_value(args.value))
    if command == "memory-get":
        return {"namespace": args.namespace, "key": args.key, "value": api.memory_recall(args.namespace, args.key)}
    if command == "memory-del":
        return api.memory_forget(args.namespace, args.key)
    if command == "memory-keys":
        return {"namespace": args.namespace, "keys": api.memory_keys(args.namespace)}
    if command == "memory-namespaces":
        return {"namespaces": api.memory_namespaces()}
    return {"error": f"unknown command: {command}"}


if __name__ == "__main__":
    raise SystemExit(main())
