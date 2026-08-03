"""Process tree — build and inspect process hierarchies."""
from __future__ import annotations

import psutil
from dataclasses import dataclass, field
from typing import Any

from modules.aios import get_kernel_logger, get_kernel_metrics
from modules.aios.process.acl import require_process_action


@dataclass
class ProcessNode:
    """Node in a process tree."""
    pid: int
    name: str
    cmdline: list[str]
    parent_pid: int | None
    children: list[ProcessNode] = field(default_factory=list)
    cpu_percent: float = 0.0
    memory_mb: float = 0.0


class ProcessTree:
    """Build and query process trees."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def build(self, root_pid: int | None = None) -> ProcessNode | list[ProcessNode] | None:
        """Build process tree from root PID (or all roots if None)."""
        require_process_action("tree")
        all_procs = {}
        for proc in psutil.process_iter(["pid", "ppid", "name", "cmdline", "cpu_percent", "memory_info"]):
            try:
                info = proc.info
                all_procs[info["pid"]] = ProcessNode(
                    pid=info["pid"],
                    name=info["name"] or "unknown",
                    cmdline=info["cmdline"] or [],
                    parent_pid=info["ppid"],
                    cpu_percent=info["cpu_percent"] or 0,
                    memory_mb=(info["memory_info"].rss / 1024 / 1024) if info["memory_info"] else 0,
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Build tree
        roots = []
        for node in all_procs.values():
            if node.parent_pid and node.parent_pid in all_procs:
                all_procs[node.parent_pid].children.append(node)
            else:
                roots.append(node)

        if root_pid is not None:
            if root_pid in all_procs:
                return all_procs[root_pid]
            return None

        return roots

    def find_by_name(self, name: str, root: ProcessNode | list[ProcessNode] | None = None) -> list[ProcessNode]:
        """Find all processes matching name in tree."""
        require_process_action("tree")
        if root is None:
            root = self.build()
        if root is None:
            return []
        if isinstance(root, ProcessNode):
            root = [root]

        results = []
        for node in root:
            if name.lower() in node.name.lower():
                results.append(node)
            results.extend(self.find_by_name(name, node.children))
        return results

    def find_by_pid(self, pid: int, root: ProcessNode | list[ProcessNode] | None = None) -> ProcessNode | None:
        """Find process by PID in tree."""
        require_process_action("tree")
        if root is None:
            root = self.build()
        if root is None:
            return None
        if isinstance(root, ProcessNode):
            root = [root]

        for node in root:
            if node.pid == pid:
                return node
            found = self.find_by_pid(pid, node.children)
            if found:
                return found
        return None

    def to_dict(self, node: ProcessNode) -> dict[str, Any]:
        """Serialize node to dict."""
        return {
            "pid": node.pid,
            "name": node.name,
            "cmdline": node.cmdline,
            "parent_pid": node.parent_pid,
            "cpu_percent": node.cpu_percent,
            "memory_mb": node.memory_mb,
            "children": [self.to_dict(c) for c in node.children],
        }


__all__ = ["ProcessTree", "ProcessNode"]
