"""Workspace subsystem (Volume 26, Fase 2): ambientes de trabalho.

WorkspaceEngine orquestra a criação de workspaces corporativos com
estrutura padrão, settings, permissões por papel e atividade.
"""
from __future__ import annotations

from .workspace_activity import WorkspaceActivity
from .workspace_creator import WorkspaceCreator
from .workspace_engine import WorkspaceEngine
from .workspace_manager import WorkspaceManager
from .workspace_permissions import WorkspacePermissions
from .workspace_settings import WorkspaceSettings

__all__ = [
    "WorkspaceActivity",
    "WorkspaceCreator",
    "WorkspaceEngine",
    "WorkspaceManager",
    "WorkspacePermissions",
    "WorkspaceSettings",
]
