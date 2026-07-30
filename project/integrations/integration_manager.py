from __future__ import annotations

import logging
import uuid
from typing import Any


class Integration:
    """Represents an external integration."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.config: dict[str, Any] = {}
        self.enabled: bool = True


class IntegrationManager:
    """Manages external integrations for projects."""

    def __init__(self) -> None:
        self._integrations: dict[str, Integration] = {}
        self._log = logging.getLogger("superdev.project.integrations")

    def register(self, name: str, project_id: str) -> Integration:
        integration = Integration(name=name, project_id=project_id)
        self._integrations[integration.id] = integration
        return integration

    def get(self, integration_id: str) -> Integration | None:
        return self._integrations.get(integration_id)

    def list_by_project(self, project_id: str) -> list[Integration]:
        return [i for i in self._integrations.values() if i.project_id == project_id]
