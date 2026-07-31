"""Collaboration & Team Workspace Engine (Volume 26).

Facade that wires the core services and exposes subsystem engines lazily
(``engine.workspace``, ``engine.teams``, ...) once they are attached by
``attach_subsystem``.
"""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_events import CollaborationEvents
from collaboration.collaboration_logger import get_logger
from collaboration.collaboration_manager import CollaborationManager
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_runtime import CollaborationRuntime
from collaboration.collaboration_security import CollaborationSecurity


class CollaborationEngine:
    """Aggregate facade over the Collaboration subsystems."""

    def __init__(self, config: CollaborationConfig | None = None,
                 events: CollaborationEvents | None = None,
                 metrics: CollaborationMetrics | None = None,
                 registry: CollaborationRegistry | None = None,
                 security: CollaborationSecurity | None = None,
                 context: CollaborationContext | None = None,
                 runtime: CollaborationRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or CollaborationConfig()
        self.events = events or CollaborationEvents()
        self.metrics = metrics or CollaborationMetrics()
        self.registry = registry or CollaborationRegistry()
        self.security = security or CollaborationSecurity()
        self.context = context or CollaborationContext()
        self.runtime = runtime or CollaborationRuntime()
        self.manager = CollaborationManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, security=self.security,
            engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        """Attaches a subsystem engine (lazy attribute access)."""
        self._subsystems[name] = engine
        setattr(self, name, engine)
        # Let the manager reach subsystem engines too.
        setattr(self.manager, f"{name}_engine", engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- delegation to manager ----------------------------------------------
    def create_workspace(self, name: str, owner_id: str,
                         description: str = "", **settings: Any) -> Any:
        return self.manager.create_workspace(name, owner_id, description,
                                             **settings)

    def list_workspaces(self) -> list[str]:
        return self.manager.list_workspaces()

    def get_workspace(self, workspace_id: str) -> Any:
        return self.manager.get_workspace(workspace_id)

    def remove_workspace(self, workspace_id: str) -> bool:
        return self.manager.remove_workspace(workspace_id)

    def create_team(self, workspace_id: str, name: str, **kwargs: Any) -> Any:
        return self.manager.create_team(workspace_id, name, **kwargs)

    def list_teams(self) -> list[str]:
        return self.manager.list_teams()

    def get_team(self, team_id: str) -> Any:
        return self.manager.get_team(team_id)

    def remove_team(self, team_id: str) -> bool:
        return self.manager.remove_team(team_id)

    def add_member(self, workspace_id: str, name: str, **kwargs: Any) -> Any:
        return self.manager.add_member(workspace_id, name, **kwargs)

    def add_agent(self, workspace_id: str, name: str, **kwargs: Any) -> Any:
        return self.manager.add_agent(workspace_id, name, **kwargs)

    def list_members(self) -> list[str]:
        return self.manager.list_members()

    def get_member(self, member_id: str) -> Any:
        return self.manager.get_member(member_id)

    def remove_member(self, member_id: str) -> bool:
        return self.manager.remove_member(member_id)

    def create_project(self, workspace_id: str, name: str,
                       **kwargs: Any) -> Any:
        return self.manager.create_project(workspace_id, name, **kwargs)

    def list_projects(self) -> list[str]:
        return self.manager.list_projects()

    def get_project(self, project_id: str) -> Any:
        return self.manager.get_project(project_id)

    def update_project_progress(self, project_id: str,
                                progress: float) -> Any:
        return self.manager.update_project_progress(project_id, progress)

    def remove_project(self, project_id: str) -> bool:
        return self.manager.remove_project(project_id)

    def create_task(self, project_id: str, workspace_id: str, title: str,
                    **kwargs: Any) -> Any:
        return self.manager.create_task(project_id, workspace_id, title,
                                        **kwargs)

    def assign_task(self, task_id: str, assignee_id: str) -> Any:
        return self.manager.assign_task(task_id, assignee_id)

    def update_task_status(self, task_id: str, status: Any) -> Any:
        return self.manager.update_task_status(task_id, status)

    def list_tasks(self) -> list[str]:
        return self.manager.list_tasks()

    def get_task(self, task_id: str) -> Any:
        return self.manager.get_task(task_id)

    def remove_task(self, task_id: str) -> bool:
        return self.manager.remove_task(task_id)

    def add_comment(self, target_kind: Any, target_id: str,
                    author_id: str, body: str) -> Any:
        return self.manager.add_comment(target_kind, target_id, author_id,
                                        body)

    def comments_for(self, target_id: str) -> list[Any]:
        return self.manager.comments_for(target_id)

    def create_review(self, target_kind: Any, target_id: str,
                      author_id: str) -> Any:
        return self.manager.create_review(target_kind, target_id, author_id)

    def decide_review(self, review_id: str, status: Any, score: float,
                      findings: list[dict[str, Any]]) -> Any:
        return self.manager.decide_review(review_id, status, score, findings)

    def get_review(self, review_id: str) -> Any:
        return self.manager.get_review(review_id)

    def start_approval(self, target_kind: Any, target_id: str,
                       requested_by: str, flow: str = "manager") -> Any:
        return self.manager.start_approval(target_kind, target_id,
                                           requested_by, flow)

    def decide_approval(self, approval_id: str, approved: bool,
                        decider: str, reason: str = "") -> Any:
        return self.manager.decide_approval(approval_id, approved, decider,
                                            reason)

    def get_approval(self, approval_id: str) -> Any:
        return self.manager.get_approval(approval_id)

    def create_channel(self, workspace_id: str, name: str,
                       topic: str = "") -> Any:
        return self.manager.create_channel(workspace_id, name, topic)

    def send_message(self, channel_id: str, author_id: str, body: str) -> Any:
        return self.manager.send_message(channel_id, author_id, body)

    def messages_for(self, channel_id: str) -> list[Any]:
        return self.manager.messages_for(channel_id)

    def add_document(self, workspace_id: str, title: str, body: str,
                     author_id: str = "", tags: list[str] | None = None) -> Any:
        return self.manager.add_document(workspace_id, title, body,
                                         author_id, tags)

    def get_document(self, document_id: str) -> Any:
        return self.manager.get_document(document_id)

    def list_documents(self) -> list[str]:
        return self.manager.list_documents()

    def search_documents(self, query: str) -> list[Any]:
        return self.manager.search_documents(query)

    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "subsystems": list(self._subsystems),
            "metrics": self.metrics.snapshot(),
            "runtime": self.runtime.state(),
        }

    def run(self) -> bool:
        """Convenience alias for start()."""
        return self.start()
