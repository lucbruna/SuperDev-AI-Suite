"""Team engine: gestão de equipes.

Estrutura corporativa: Projeto ERP -> Equipe Desenvolvimento (Backend,
Frontend, Database), Equipe Qualidade (Tester, Security Analyst) e
Agentes IA (Coding, Testing, Documentation).
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import TeamKind, TeamRecord
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.teams.team_manager import TeamManager
from collaboration.teams.team_roles import TeamRoles


class TeamEngine:
    """Orquestrador de equipes (Fase 3 do Volume 26)."""

    def __init__(self, events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 config: CollaborationConfig | None = None,
                 context: CollaborationContext | None = None,
                 security: CollaborationSecurity | None = None,
                 registry: CollaborationRegistry | None = None,
                 manager: TeamManager | None = None) -> None:
        self._log = get_logger()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.config = config or CollaborationConfig()
        self.context = context or CollaborationContext()
        self.security = security or CollaborationSecurity()
        self.manager = manager or TeamManager(registry=registry)
        self.roles = TeamRoles()

    def create(self, workspace_id: str, name: str,
               kind: TeamKind = TeamKind.DEVELOPMENT,
               lead_id: str | None = None,
               **settings: Any) -> TeamRecord:
        team = self.manager.create(workspace_id, name, kind, lead_id)
        if settings:
            self.manager.update_settings(team.team_id, **settings)
        self.metrics.increment("collab.teams")
        self.events.publish(CollaborationEventType.TEAM_CREATED,
                            {"team_id": team.team_id, "name": name,
                             "workspace_id": workspace_id,
                             "kind": kind.value})
        self.manager.activity(team.team_id).record("team.created",
                                                   lead_id or workspace_id)
        return team

    def get(self, team_id: str) -> TeamRecord | None:
        return self.manager.get(team_id)

    def list(self) -> list[str]:
        return self.manager.list()

    def remove(self, team_id: str) -> bool:
        return self.manager.remove(team_id)

    def by_kind(self, kind: TeamKind) -> list[TeamRecord]:
        return self.manager.structure.by_kind(kind)

    def summary(self, team_id: str) -> dict[str, Any]:
        return self.manager.structure.summary(team_id)

    def set_lead(self, team_id: str, lead_id: str) -> TeamRecord | None:
        return self.manager.set_lead(team_id, lead_id)

    def get_settings(self, team_id: str) -> dict[str, Any]:
        return self.manager.settings(team_id).to_dict()

    def update_settings(self, team_id: str, **overrides: Any) -> dict[str, Any]:
        settings = self.manager.update_settings(team_id, **overrides)
        return settings.to_dict()

    def record_activity(self, team_id: str, action: str, actor_id: str,
                        details: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.manager.activity(team_id).record(action, actor_id,
                                                     details)

    def activity(self, team_id: str,
                 limit: int = 50) -> list[dict[str, Any]]:
        return self.manager.activity(team_id).list(limit)

    def stats(self) -> dict[str, Any]:
        return {"teams": self.manager.count()}
