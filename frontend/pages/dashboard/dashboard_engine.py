from __future__ import annotations

import logging
import time
import sys
import os
import importlib
from typing import Any

from ...frontend_context import FrontendContext

logger = logging.getLogger(__name__)

# Ensure ai/ is on sys.path
_AI_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ai")
_AI_ROOT = os.path.normpath(_AI_ROOT)
if _AI_ROOT not in sys.path:
    sys.path.insert(0, _AI_ROOT)


def _safe_import(module_path: str, class_name: str) -> Any:
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
    except (ImportError, AttributeError):
        return None


class DashboardEngine:
    """Renders the main dashboard page with live AI module data."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.dashboard")
        self._context = context or FrontendContext()
        self._widgets: list[dict[str, Any]] = []

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "dashboard",
            "widgets": self._widgets,
            "metrics": self.metrics(),
            "ai_modules": self.ai_module_stats(),
        }

    def add_widget(self, kind: str, title: str) -> str:
        widget_id = f"widget-{len(self._widgets) + 1}"
        self._widgets.append({"widget_id": widget_id, "kind": kind, "title": title})
        return widget_id

    def remove_widget(self, widget_id: str) -> bool:
        remaining = [w for w in self._widgets if w["widget_id"] != widget_id]
        removed = len(remaining) < len(self._widgets)
        self._widgets = remaining
        return removed

    def metrics(self) -> dict[str, Any]:
        return {
            "active_agents": 12,
            "running_workflows": 4,
            "deployments": 18,
            "alerts": 2,
            "uptime": time.time(),
        }

    def ai_module_stats(self) -> dict[str, Any]:
        """Fetch live stats from all AI modules."""
        stats = {}

        # Cybersecurity Engine
        cls = _safe_import("cybersecurity_engine", "CybersecurityEngine")
        if cls:
            try:
                engine = cls()
                stats["cybersecurity"] = engine.get_stats()
            except Exception as e:
                stats["cybersecurity"] = {"error": str(e)}
        else:
            stats["cybersecurity"] = {"status": "unavailable"}

        # Data Platform
        cls = _safe_import("data_platform", "DataPlatformEngine")
        if cls:
            try:
                engine = cls()
                stats["data_platform"] = engine.get_stats()
            except Exception as e:
                stats["data_platform"] = {"error": str(e)}
        else:
            stats["data_platform"] = {"status": "unavailable"}

        # ERP Operations
        cls = _safe_import("erp_operations", "ERPEngine")
        if cls:
            try:
                engine = cls()
                stats["erp"] = engine.get_stats()
            except Exception as e:
                stats["erp"] = {"error": str(e)}
        else:
            stats["erp"] = {"status": "unavailable"}

        # Knowledge Engine
        cls = _safe_import("ai_knowledge_engine", "KnowledgeEngine")
        if cls:
            try:
                engine = cls()
                stats["knowledge"] = engine.get_stats()
            except Exception as e:
                stats["knowledge"] = {"error": str(e)}
        else:
            stats["knowledge"] = {"status": "unavailable"}

        return stats
