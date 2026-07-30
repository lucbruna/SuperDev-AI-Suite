from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from ..monitoring_models import DashboardWidget


@dataclass
class Dashboard:
    dashboard_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = ""
    description: str = ""
    widgets: list[DashboardWidget] = field(default_factory=list)
    layout: str = "grid"  # grid, flex, freeform
    refresh_interval: int = 60
    tags: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class DashboardManager:
    """Manages dashboard CRUD and persistence."""

    def __init__(self, storage_path: str = "") -> None:
        self._path = storage_path or "dashboards.json"
        self._dashboards: dict[str, Dashboard] = {}
        self._load()

    def create(self, title: str, description: str = "") -> Dashboard:
        dash = Dashboard(title=title, description=description)
        self._dashboards[dash.dashboard_id] = dash
        self._save()
        return dash

    def get(self, dashboard_id: str) -> Dashboard | None:
        return self._dashboards.get(dashboard_id)

    def update(self, dashboard_id: str, **kwargs: Any) -> Dashboard | None:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return None
        for key, value in kwargs.items():
            if hasattr(dash, key):
                setattr(dash, key, value)
        dash.updated_at = time.time()
        self._save()
        return dash

    def delete(self, dashboard_id: str) -> bool:
        if dashboard_id in self._dashboards:
            del self._dashboards[dashboard_id]
            self._save()
            return True
        return False

    def list_dashboards(self) -> list[Dashboard]:
        return list(self._dashboards.values())

    def add_widget(self, dashboard_id: str, widget: DashboardWidget) -> bool:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return False
        dash.widgets.append(widget)
        dash.updated_at = time.time()
        self._save()
        return True

    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return False
        dash.widgets = [w for w in dash.widgets if w.widget_id != widget_id]
        dash.updated_at = time.time()
        self._save()
        return True

    def _save(self) -> None:
        try:
            data = {
                did: {
                    "dashboard_id": d.dashboard_id,
                    "title": d.title,
                    "description": d.description,
                    "widgets": [
                        {
                            "widget_id": w.widget_id,
                            "title": w.title,
                            "widget_type": w.widget_type,
                            "metric": w.metric,
                            "position": w.position,
                            "size": w.size,
                            "config": w.config,
                        }
                        for w in d.widgets
                    ],
                    "layout": d.layout,
                    "refresh_interval": d.refresh_interval,
                    "tags": d.tags,
                    "created_at": d.created_at,
                    "updated_at": d.updated_at,
                }
                for did, d in self._dashboards.items()
            }
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except OSError:
            pass

    def _load(self) -> None:
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for did, item in data.items():
                widgets = [
                    DashboardWidget(**w) for w in item.get("widgets", [])
                ]
                dash = Dashboard(
                    dashboard_id=item["dashboard_id"],
                    title=item["title"],
                    description=item.get("description", ""),
                    widgets=widgets,
                    layout=item.get("layout", "grid"),
                    refresh_interval=item.get("refresh_interval", 60),
                    tags=item.get("tags", []),
                    created_at=item.get("created_at", 0.0),
                    updated_at=item.get("updated_at", 0.0),
                )
                self._dashboards[did] = dash
        except (OSError, json.JSONDecodeError):
            pass
