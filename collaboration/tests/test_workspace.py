"""Tests for the workspace subsystem (Volume 26, Fase 2)."""

from __future__ import annotations

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import MemberRole
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.workspace.workspace_engine import WorkspaceEngine
from collaboration.workspace.workspace_manager import WorkspaceManager
from collaboration.workspace.workspace_settings import WorkspaceSettings


def make_engine(**kwargs) -> WorkspaceEngine:
    return WorkspaceEngine(events=CollaborationEvents(),
                           metrics=CollaborationMetrics(),
                           config=CollaborationConfig(),
                           context=CollaborationContext(),
                           security=CollaborationSecurity(),
                           registry=CollaborationRegistry(), **kwargs)


class TestWorkspaceCreator:
    def test_default_structure(self) -> None:
        engine = make_engine()
        ws = engine.create("NEXUS ERP PROJECT", owner_id="joao")
        structure = engine.structure(ws.workspace_id)
        names = [s["name"] for s in structure["sections"]]
        assert "Código" in names
        assert "Documentação" in names
        assert "Tarefas" in names
        assert "IA Agents" in names
        assert "Testes" in names
        assert "Deploy" in names

    def test_custom_sections(self) -> None:
        manager = WorkspaceManager()
        ws = manager.create("WS", "joao")
        layout = manager.structure(ws.workspace_id)
        assert layout["owner_id"] == "joao"
        assert all("section_id" in s for s in layout["sections"])


class TestWorkspaceSettings:
    def test_defaults_and_update(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao", timezone="America/Sao_Paulo")
        settings = engine.get_settings(ws.workspace_id)
        assert settings["settings"]["allow_agents"] is True
        assert settings["settings"]["timezone"] == "America/Sao_Paulo"

    def test_validate_timezone(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao")
        try:
            engine.update_settings(ws.workspace_id, timezone="Invalida")
            raised = False
        except ValueError:
            raised = True
        assert raised is True
        updated = engine.update_settings(ws.workspace_id,
                                         require_review=False)
        assert updated["settings"]["require_review"] is False

    def test_static_defaults(self) -> None:
        assert WorkspaceSettings.validate({"timezone": "UTC"}) == []
        assert WorkspaceSettings.validate({"timezone": "X"}) != []


class TestWorkspacePermissions:
    def test_role_matrix(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao")
        assert engine.can(ws.workspace_id, MemberRole.OWNER,
                          "manage_workspace") is True
        assert engine.can(ws.workspace_id, MemberRole.DEVELOPER,
                          "manage_workspace") is False
        assert engine.can(ws.workspace_id, MemberRole.DEVELOPER,
                          "create_task") is True
        assert engine.can(ws.workspace_id, MemberRole.VIEWER,
                          "view") is True

    def test_require_audits_deny(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao")
        assert engine.require(ws.workspace_id, MemberRole.VIEWER,
                              "deploy") is False
        log = engine.security.audit_log()
        assert any("deny" in e["action"] for e in log)


class TestWorkspaceActivity:
    def test_record_and_filter(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao")
        engine.record_activity(ws.workspace_id, "task.created", "joao",
                               {"task_id": "t1"})
        engine.record_activity(ws.workspace_id, "review.completed", "maria")
        entries = engine.activity(ws.workspace_id, limit=10)
        assert len(entries) >= 2
        activity = engine.manager.activity(ws.workspace_id)
        assert activity.filter(action="task.created")[0]["actor_id"] == "joao"
        assert activity.filter(action="review.completed")[0][
            "actor_id"] == "maria"

    def test_engine_records_create(self) -> None:
        engine = make_engine()
        ws = engine.create("WS", "joao")
        activity = engine.manager.activity(ws.workspace_id)
        assert activity.filter(action="workspace.created")[0]["actor_id"] == \
            "joao"


class TestWorkspaceEngine:
    def test_crud_and_stats(self) -> None:
        engine = make_engine()
        ws1 = engine.create("WS Alpha", "joao")
        ws2 = engine.create("WS Beta", "maria")
        assert sorted(engine.list()) == sorted([ws1.workspace_id,
                                                ws2.workspace_id])
        first = engine.get(ws1.workspace_id)
        assert first is not None
        assert first.name == "WS Alpha"
        assert engine.stats()["workspaces"] == 2
        assert engine.remove(ws1.workspace_id) is True
        assert engine.remove(ws1.workspace_id) is False
        assert engine.stats()["workspaces"] == 1

    def test_unknown_workspace_raises(self) -> None:
        engine = make_engine()
        try:
            engine.structure("ws-inexistente")
            raised = False
        except KeyError:
            raised = True
        assert raised is True

    def test_events_and_metrics(self) -> None:
        engine = make_engine()
        seen: list[str] = []
        engine.events.on(CollaborationEventType.WORKSPACE_CREATED,
                         lambda d: seen.append(d["name"]))
        engine.create("NEXUS", "joao")
        assert seen == ["NEXUS"]
        counters = engine.metrics.snapshot()["counters"]
        assert counters["collab.workspaces"] == 1

    def test_manager_registry_sync(self) -> None:
        registry = CollaborationRegistry()
        manager = WorkspaceManager(registry=registry)
        ws = manager.create("WS", "joao")
        assert registry.get_workspace(ws.workspace_id) is not None
        assert manager.remove(ws.workspace_id) is True
        assert registry.get_workspace(ws.workspace_id) is None
