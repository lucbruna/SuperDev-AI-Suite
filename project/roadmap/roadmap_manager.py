from __future__ import annotations

import logging
import uuid
from typing import Any


class RoadmapItem:
    """Represents a roadmap item."""

    def __init__(self, title: str, project_id: str, quarter: str) -> None:
        self.id = str(uuid.uuid4())
        self.title = title
        self.project_id = project_id
        self.quarter = quarter
        self.status: str = "planned"


class RoadmapManager:
    """Manages project roadmap."""

    def __init__(self) -> None:
        self._items: dict[str, RoadmapItem] = {}
        self._log = logging.getLogger("superdev.project.roadmap")

    def add(self, title: str, project_id: str, quarter: str) -> RoadmapItem:
        item = RoadmapItem(title=title, project_id=project_id, quarter=quarter)
        self._items[item.id] = item
        return item

    def list_by_project(self, project_id: str) -> list[RoadmapItem]:
        return [i for i in self._items.values() if i.project_id == project_id]

    def update_status(self, item_id: str, status: str) -> None:
        item = self._items.get(item_id)
        if item:
            item.status = status
