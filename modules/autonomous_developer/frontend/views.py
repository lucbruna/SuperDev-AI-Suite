"""Deterministic text views for the module frontend."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["DashboardBuilder", "View", "ViewRegistry"]


@dataclass(slots=True)
class View:
    """A named text view rendered to markdown."""

    name: str
    title: str
    body: str = ""

    @property
    def render(self) -> str:
        body = self.body.strip()
        return f"# {self.title}" if not body else f"# {self.title}\n\n{body}"


class ViewRegistry:
    """Holds named views; ``get`` falls back to a default."""

    def __init__(self) -> None:
        self._views: dict[str, View] = {}

    def register(self, view: View) -> View:
        self._views[view.name] = view
        return view

    def get(self, name: str, default: View | None = None) -> View | None:
        return self._views.get(name, default)

    def names(self) -> list[str]:
        return list(self._views)


class DashboardBuilder:
    """Builds a dashboard view from context stats, sorted deterministically."""

    def build(self, ctx: DeveloperContext) -> View:
        lines = [f"- {key}: {value}" for key, value in sorted(ctx.stats.items())]
        body = "\n".join(lines) if lines else "_no stats_"
        return View(name="dashboard", title="Dashboard", body=body)
