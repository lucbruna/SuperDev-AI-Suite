from __future__ import annotations

from typing import Any, Literal

ToolStatus = Literal["idle", "running", "completed", "failed", "cancelled"]
ToolCategory = Literal[
    "filesystem",
    "terminal",
    "process",
    "git",
    "github",
    "docker",
    "kubernetes",
    "browser",
    "database",
    "api",
    "llm",
    "rag",
    "network",
    "web",
    "security",
    "system",
    "package_manager",
    "scheduler",
    "compiler",
    "debugger",
    "profiler",
    "benchmark",
    "documents",
    "media",
    "archive",
    "cloud",
    "search",
    "vector",
    "shell",
    "python",
    "node",
    "installers",
]

ToolResult = dict[str, Any]
ToolParams = dict[str, Any]
ExecutionContext = dict[str, Any]
