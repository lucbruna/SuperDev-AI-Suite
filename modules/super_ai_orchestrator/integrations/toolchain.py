"""Toolchain connectors: git, docker, k8s, mcp, llm, db, monitoring, ...

These connectors expose the toolchain surface the orchestrator plans around.
Availability is probed deterministically (binary on PATH or standard
library presence). Like all connectors, calls degrade gracefully — the
orchestrator decides and delegates; actual tool invocation belongs to the
sibling modules and integrations.
"""
from __future__ import annotations

import shutil
from importlib.util import find_spec
from typing import Any

from modules.super_ai_orchestrator.integrations.base import Connector

# name -> (display, tools, probe)
def _has_binary(*names: str) -> bool:
    return any(shutil.which(name) for name in names)


def _has_module(path: str) -> bool:
    try:
        return find_spec(path) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def _make(
    name: str,
    display: str,
    tools: tuple[str, ...],
    available: bool,
    note: str,
) -> Connector:
    return Connector(name=name, display=display, tools=tools, available=available, note=note)


def make_toolchain_connectors() -> tuple[Connector, ...]:
    """Build the toolchain connectors with live availability probes."""
    return (
        _make("git", "Git", ("git",), _has_binary("git"), "git binary on PATH"),
        _make("github", "GitHub CLI", ("github",), _has_binary("gh"), "gh CLI on PATH"),
        _make("docker", "Docker", ("docker",), _has_binary("docker"), "docker binary on PATH"),
        _make("kubernetes", "Kubernetes", ("kubernetes",), _has_binary("kubectl"), "kubectl on PATH"),
        _make("mcp", "MCP", ("mcp",), True, "model context protocol surface"),
        _make("api", "External APIs", ("api",), True, "external REST/HTTP integrations"),
        _make("database", "Database", ("db",), True, "persistence integrations"),
        _make("llm", "LLM Providers", ("llm",), True, "provider registry (openai, claude, gemini, ...)"),
        _make("workflow_engine", "Workflow Engine", ("workflow_engine",), True, "multi-step workflow runner"),
        _make("multi_agent", "Multi-Agent", ("multi_agent",), True, "multi-agent collaboration"),
        _make("plugins", "Plugins", ("plugins",), True, "plugin surface"),
        _make("memory_engine", "Memory Engine", ("memory_engine", "memory"), True, "long-term memory integrations"),
        _make("vector_db", "Vector DB", ("vector_db", "rag"), _has_module("chromadb") or _has_module("faiss"), "vector store available"),
        _make("event_bus", "Event Bus", ("event_bus",), True, "event surface (websocket hub)"),
        _make("monitoring", "Monitoring", ("monitoring", "telemetry"), True, "health and metric surface"),
        _make("dashboard", "Dashboard", ("dashboard",), True, "frontend dashboard surface"),
    )
