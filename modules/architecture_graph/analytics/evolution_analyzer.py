"""Evolution analyzer: how the architecture changes over time (via git)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.scanner.git_scanner import scan as git_scan


def analyze_evolution(root: str) -> dict[str, Any]:
    """Git-derived evolution report: activity, hotspots, trend."""
    data = git_scan(root)
    if not data.get("available"):
        return {"available": False, "reason": "no git repository"}

    changed = data.get("changed_files", [])
    per_dir: dict[str, int] = {}
    for item in changed:
        path = item.get("path", "")
        top = path.split("/", 1)[0] if "/" in path else "."
        per_dir[top] = per_dir.get(top, 0) + 1

    hotspots = sorted(per_dir.items(), key=lambda kv: kv[1], reverse=True)[:10]
    commits = data.get("recent_commits", [])
    added = sum(1 for c in changed if c.get("status") == "??")
    modified = sum(1 for c in changed if c.get("status") in {"M", "MM"})
    deleted = sum(1 for c in changed if c.get("status") in {"D", "DD"})

    return {
        "available": True,
        "head": data.get("head", ""),
        "branch": data.get("branch", ""),
        "total_tracked_files": len(data.get("tracked_files", [])),
        "changed_files_total": len(changed),
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "recent_commits": commits[:10],
        "activity_hotspots": [{"path": p, "changes": c} for p, c in hotspots],
        "trend": (
            "growing" if added > deleted else
            "stable" if added == deleted else
            "shrinking"
        ),
    }
