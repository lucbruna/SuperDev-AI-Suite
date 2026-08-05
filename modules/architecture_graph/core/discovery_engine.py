"""Discovery engine: incremental change detection between scans.

Stores a file snapshot (rel_path -> size/mtime) and reports added, modified
and removed files since the last scan — the input for incremental graph
refreshes and real-time change notifications.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.scanner.filesystem_scanner import FileInfo


def current_snapshot(files: list[FileInfo]) -> dict[str, dict[str, Any]]:
    return {
        info.rel_path: {"size": info.size, "mtime": info.mtime} for info in files
    }


def diff_snapshots(
    old: dict[str, dict[str, Any]] | None,
    new: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Diff two snapshots. ``old`` may be None (first scan)."""
    old = old or {}
    old_paths = set(old)
    new_paths = set(new)

    added = sorted(new_paths - old_paths)
    removed = sorted(old_paths - new_paths)
    modified: list[str] = []
    for path in new_paths & old_paths:
        if old[path].get("mtime") != new[path].get("mtime") or old[path].get("size") != new[path].get("size"):
            modified.append(path)
    modified.sort()

    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "total_added": len(added),
        "total_removed": len(removed),
        "total_modified": len(modified),
        "unchanged": len(new_paths & old_paths) - len(modified),
    }
