"""Workspace lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import WorkspaceRecord
from collaboration.collaboration_protocols import new_id
from collaboration.workspace.workspace_activity import WorkspaceActivity
from collaboration.workspace.workspace_creator import WorkspaceCreator
from collaboration.workspace.workspace_permissions import WorkspacePermissions
from collaboration.workspace.workspace_settings import WorkspaceSettings


class WorkspaceManager:
    """CRUD and configuration for collaborative workspaces."""

    def __init__(self, registry: Any = None,
                 security: Any = None) -> None:
        self.registry = registry
        self.security = security
        self._workspaces: dict[str, WorkspaceRecord] = {}
        self.creator = WorkspaceCreator()
        self._settings: dict[str, WorkspaceSettings] = {}
        self._permissions: dict[str, WorkspacePermissions] = {}
        self._activity: dict[str, WorkspaceActivity] = {}

    def create(self, name: str, owner_id: str,
               description: str = "", **settings: Any) -> WorkspaceRecord:
        workspace = WorkspaceRecord(workspace_id=new_id("ws"), name=name,
                                    owner_id=owner_id, description=description,
                                    settings=settings)
        self._workspaces[workspace.workspace_id] = workspace
        if self.registry is not None:
            self.registry.register_workspace(workspace.workspace_id, workspace)
        self._settings[workspace.workspace_id] = WorkspaceSettings(
            workspace.workspace_id, settings)
        self._permissions[workspace.workspace_id] = WorkspacePermissions(
            workspace.workspace_id, security=self.security)
        self._activity[workspace.workspace_id] = WorkspaceActivity(
            workspace.workspace_id)
        return workspace

    def get(self, workspace_id: str) -> WorkspaceRecord | None:
        return self._workspaces.get(workspace_id)

    def list(self) -> list[str]:
        return list(self._workspaces)

    def remove(self, workspace_id: str) -> bool:
        removed = self._workspaces.pop(workspace_id, None) is not None
        self._settings.pop(workspace_id, None)
        self._permissions.pop(workspace_id, None)
        self._activity.pop(workspace_id, None)
        if removed and self.registry is not None:
            self.registry.remove_workspace(workspace_id)
        return removed

    def structure(self, workspace_id: str) -> dict[str, Any]:
        """Returns the workspace record plus its default section layout."""
        workspace = self.get(workspace_id)
        if workspace is None:
            raise KeyError(f"unknown workspace: {workspace_id}")
        layout = self.creator.create(workspace.workspace_id, workspace.name,
                                     workspace.owner_id,
                                     workspace.description)
        return layout

    def settings(self, workspace_id: str) -> WorkspaceSettings:
        settings = self._settings.get(workspace_id)
        if settings is None:
            raise KeyError(f"unknown workspace: {workspace_id}")
        return settings

    def permissions(self, workspace_id: str) -> WorkspacePermissions:
        permissions = self._permissions.get(workspace_id)
        if permissions is None:
            raise KeyError(f"unknown workspace: {workspace_id}")
        return permissions

    def activity(self, workspace_id: str) -> WorkspaceActivity:
        activity = self._activity.get(workspace_id)
        if activity is None:
            raise KeyError(f"unknown workspace: {workspace_id}")
        return activity

    def update_settings(self, workspace_id: str,
                        **overrides: Any) -> WorkspaceSettings:
        settings = self.settings(workspace_id)
        errors = WorkspaceSettings.validate(overrides)
        if errors:
            raise ValueError("; ".join(errors))
        settings.update(**overrides)
        return settings

    def count(self) -> int:
        return len(self._workspaces)
