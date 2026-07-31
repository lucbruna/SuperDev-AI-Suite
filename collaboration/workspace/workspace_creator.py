"""Workspace creation with a default corporate structure."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_protocols import new_id

DEFAULT_SECTIONS = [
    {"key": "codigo", "name": "Código", "kind": "repo"},
    {"key": "documentacao", "name": "Documentação", "kind": "docs"},
    {"key": "tarefas", "name": "Tarefas", "kind": "tasks"},
    {"key": "ia_agents", "name": "IA Agents", "kind": "agents"},
    {"key": "testes", "name": "Testes", "kind": "quality"},
    {"key": "deploy", "name": "Deploy", "kind": "ops"},
]


class WorkspaceCreator:
    """Creates workspace records with an optional default structure."""

    def create(self, workspace_id: str, name: str, owner_id: str,
               description: str = "",
               sections: list[dict[str, Any]] | None = None
               ) -> dict[str, Any]:
        """Returns a workspace dict with the given (or default) sections."""
        structure = [dict(section) for section in (sections or DEFAULT_SECTIONS)]
        for section in structure:
            section.setdefault("section_id", new_id("sec"))
        return {
            "workspace_id": workspace_id,
            "name": name,
            "owner_id": owner_id,
            "description": description,
            "sections": structure,
        }

    def default_sections(self) -> list[dict[str, Any]]:
        return [dict(section) for section in DEFAULT_SECTIONS]
