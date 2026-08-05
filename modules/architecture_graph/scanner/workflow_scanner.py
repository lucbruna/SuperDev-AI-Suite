"""Workflow scanner: discovers workflow definitions across the platform.

Looks in ``workflow_engine/``, ``workflow/`` and native module directories
for YAML/JSON/Python workflow definitions and returns a normalized record
per workflow (name, path, format, declared agents/steps).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.architecture_graph.parsers.yaml_parser import parse as yaml_parse

_WORKFLOW_EXT = {".yaml", ".yml", ".json", ".py"}
_ROOT_DIRS = ("workflow_engine", "workflow", "automation", "runtime_engine")


def _extract(text: str, path: str, fmt: str) -> dict[str, Any]:
    name = Path(path).stem
    agents: list[str] = []
    steps: list[str] = []
    if fmt == "yaml":
        data = yaml_parse(text)
        if not data.get("fallback", False):
            for key in ("agents", "nodes"):
                value = data.get(key)
                if isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            agents.append(str(item.get("agent") or item.get("id") or ""))
                        else:
                            agents.append(str(item))
                elif isinstance(value, dict):
                    agents.extend(str(k) for k in value)
            nodes = data.get("nodes") or data.get("steps")
            if isinstance(nodes, list):
                for node in nodes:
                    if isinstance(node, dict):
                        steps.append(str(node.get("id") or node.get("name") or ""))
    elif fmt == "json":
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                agents = [str(a) for a in (data.get("agents") or []) if a]
                steps = [str(s) for s in (data.get("steps") or []) if s]
                name = str(data.get("name") or name)
        except ValueError:
            pass
    return {"name": name, "agents": agents, "steps": steps}


def scan(root: str) -> list[dict[str, Any]]:
    workflows: list[dict[str, Any]] = []
    base = Path(root)
    dirs = [base / d for d in _ROOT_DIRS if (base / d).exists()]
    modules_dir = base / "modules"
    if modules_dir.exists():
        dirs.extend(
            p for p in modules_dir.iterdir() if p.is_dir() and p.name != "__pycache__"
        )
    seen: set[str] = set()
    for directory in dirs:
        if directory.name == "__pycache__":
            continue
        for entry in sorted(directory.rglob("*")):
            if entry.suffix not in _WORKFLOW_EXT or entry.name.startswith("."):
                continue
            if any(part in {".git", "node_modules", "__pycache__", ".venv"} for part in entry.parts):
                continue
            key = entry.relative_to(base).as_posix()
            if key in seen:
                continue
            fmt = "yaml" if entry.suffix in {".yaml", ".yml"} else entry.suffix.lstrip(".")
            try:
                text = entry.read_text(encoding="utf-8", errors="ignore")[:200_000]
            except OSError:
                continue
            if "workflow" not in key.lower() and entry.suffix == ".py":
                continue  # only python files clearly about workflows
            record = _extract(text, key, fmt)
            record["path"] = key
            record["format"] = fmt
            seen.add(key)
            workflows.append(record)
    return workflows
