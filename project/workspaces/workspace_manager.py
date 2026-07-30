from __future__ import annotations

import logging
import uuid
from typing import Any


class Workspace:
    """Represents an isolated project workspace."""

    def __init__(self, name: str, owner: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.owner = owner
        self.members: list[str] = []
        self.metadata: dict[str, Any] = {}


class WorkspaceManager:
    """Manages workspaces for project isolation."""

    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}
        self._log = logging.getLogger("superdev.project.workspaces")

    def create(self, name: str, owner: str) -> Workspace:
        ws = Workspace(name=name, owner=owner)
        self._workspaces[ws.id] = ws
        self._log.info("Created workspace %s", ws.id)
        return ws

    def get(self, ws_id: str) -> Workspace | None:
        return self._workspaces.get(ws_id)

    def delete(self, ws_id: str) -> None:
        self._workspaces.pop(ws_id, None)

    def add_member(self, ws_id: str, user: str) -> None:
        ws = self._workspaces.get(ws_id)
        if ws and user not in ws.members:
            ws.members.append(user)
