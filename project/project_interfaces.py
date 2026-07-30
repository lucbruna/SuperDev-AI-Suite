from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .project_models import Project


class ProjectRepositoryInterface(ABC):
    @abstractmethod
    def save(self, project: Project) -> None: ...
    @abstractmethod
    def get(self, project_id: str) -> Project | None: ...
    @abstractmethod
    def delete(self, project_id: str) -> None: ...
    @abstractmethod
    def list_all(self) -> list[Project]: ...


class ProjectEventBus(ABC):
    @abstractmethod
    def emit(self, event: str, **data: Any) -> None: ...
    @abstractmethod
    def on(self, event: str, handler: Any) -> None: ...
