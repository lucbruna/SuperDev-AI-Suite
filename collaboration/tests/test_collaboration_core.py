"""Tests for the collaboration core (Volume 26, Fase 1)."""

from __future__ import annotations

from collaboration.collaboration_config import CollaborationConfig
from collaboration.collaboration_context import CollaborationContext
from collaboration.collaboration_engine import CollaborationEngine
from collaboration.collaboration_events import (CollaborationEventType,
                                                CollaborationEvents)
from collaboration.collaboration_metrics import CollaborationMetrics
from collaboration.collaboration_models import (ApprovalStatus, EntityKind,
                                                MemberKind, MemberRole,
                                                ReviewKind, ReviewStatus,
                                                TaskPriority, TaskStatus,
                                                TeamKind)
from collaboration.collaboration_protocols import (coerce_bool, coerce_number,
                                                   extract_mentions, new_id,
                                                   safe_get)
from collaboration.collaboration_registry import CollaborationRegistry
from collaboration.collaboration_runtime import CollaborationRuntime
from collaboration.collaboration_security import CollaborationSecurity
from collaboration.collaboration_factory import build_engine


def make_engine(**kwargs) -> CollaborationEngine:
    return CollaborationEngine(
        config=CollaborationConfig(), events=CollaborationEvents(),
        metrics=CollaborationMetrics(), registry=CollaborationRegistry(),
        security=CollaborationSecurity(), context=CollaborationContext(),
        runtime=CollaborationRuntime(), **kwargs)


class TestConfig:
    def test_merge(self) -> None:
        config = CollaborationConfig(workspace_name="Acme")
        merged = config.merge(workspace_name="Nexus")
        assert merged.workspace_name == "Nexus"
        assert config.workspace_name == "Acme"


class TestModels:
    def test_enums(self) -> None:
        assert MemberKind.AGENT.value == "agent"
        assert TaskStatus.IN_REVIEW.value == "in_review"
        assert ReviewKind.SECURITY.value == "security"
        assert TeamKind.AGENTS.value == "agents"
        assert ApprovalStatus.PENDING.value == "pending"
        assert TaskPriority.URGENT.value == "urgent"


class TestEvents:
    def test_on_publish_off(self) -> None:
        events = CollaborationEvents()
        seen: list[dict] = []
        handler = lambda data: seen.append(data)
        events.on(CollaborationEventType.TASK_CREATED, handler)
        events.publish(CollaborationEventType.TASK_CREATED, {"task_id": "t1"})
        events.off(CollaborationEventType.TASK_CREATED, handler)
        events.publish(CollaborationEventType.TASK_CREATED, {"task_id": "t2"})
        assert len(seen) == 1
        assert seen[0]["task_id"] == "t1"
        assert seen[0]["type"] == "task.created"

    def test_once(self) -> None:
        events = CollaborationEvents()
        count = {"n": 0}
        events.once(CollaborationEventType.MEMBER_JOINED,
                    lambda data: count.__setitem__("n", count["n"] + 1))
        events.publish(CollaborationEventType.MEMBER_JOINED)
        events.publish(CollaborationEventType.MEMBER_JOINED)
        assert count["n"] == 1

    def test_listener_isolation(self) -> None:
        events = CollaborationEvents()
        events.on(CollaborationEventType.MESSAGE_SENT, lambda d: (_ for _ in ()).throw(RuntimeError("boom")))
        # must not raise
        events.publish(CollaborationEventType.MESSAGE_SENT)
        assert events.listener_count(CollaborationEventType.MESSAGE_SENT) == 1


class TestMetrics:
    def test_snapshot(self) -> None:
        metrics = CollaborationMetrics()
        metrics.increment("collab.tasks")
        metrics.increment("collab.tasks")
        metrics.gauge("collab.progress.p1", 74.0)
        snap = metrics.snapshot()
        assert snap["counters"]["collab.tasks"] == 2
        assert snap["gauges"]["collab.progress.p1"] == 74.0

    def test_timing(self) -> None:
        metrics = CollaborationMetrics()
        with metrics.timed("review"):
            pass
        snap = metrics.snapshot()
        assert "review" in snap["timings"]
        assert snap["timings"]["review"][1] == 1


class TestSecurity:
    def test_permissions(self) -> None:
        security = CollaborationSecurity()
        assert security.can("developer", "tasks") is False
        security.grant("developer", "tasks")
        assert security.can("developer", "tasks") is True

    def test_at_least(self) -> None:
        security = CollaborationSecurity()
        assert security.at_least(MemberRole.ADMIN, MemberRole.DEVELOPER) is True
        assert security.at_least(MemberRole.VIEWER, MemberRole.ADMIN) is False

    def test_sanitize_and_audit(self) -> None:
        security = CollaborationSecurity()
        assert security.sanitize("  a  b  ") == "a b"
        security.audit("mem-1", "review", "proj-1")
        log = security.audit_log()
        assert log[0]["action"] == "review"


class TestProtocols:
    def test_new_id(self) -> None:
        assert new_id("task").startswith("task-")
        assert new_id("task") != new_id("task")

    def test_safe_get_dot_path(self) -> None:
        assert safe_get({"a": {"b": 1}}, "a.b") == 1
        assert safe_get({"a": 1}, "a.b", default=0) == 0

    def test_coerce(self) -> None:
        assert coerce_bool("sim") is True
        assert coerce_bool(0) is False
        assert coerce_number("1,5") == 1.5

    def test_extract_mentions(self) -> None:
        assert extract_mentions("Oi @joao e @maria, revisem @joao") == \
            ["joao", "maria"]


class TestRegistry:
    def test_workspace_crud(self) -> None:
        registry = CollaborationRegistry()
        registry.register_workspace("ws-1", {"name": "Nexus"})
        assert registry.list_workspaces() == ["ws-1"]
        workspace = registry.get_workspace("ws-1")
        assert workspace is not None
        assert workspace["name"] == "Nexus"
        assert registry.remove_workspace("ws-1") is True
        assert registry.remove_workspace("ws-1") is False

    def test_stats(self) -> None:
        registry = CollaborationRegistry()
        registry.register_member("mem-1", object())
        registry.register_team("team-1", object())
        from collaboration.collaboration_models import CommentRecord, EntityKind
        registry.add_comment(CommentRecord(comment_id="c1",
                                           target_kind=EntityKind.TASK,
                                           target_id="t1", author_id="a1",
                                           body="oi"))
        stats = registry.stats()
        assert stats["members"] == 1
        assert stats["teams"] == 1
        assert stats["comments"] == 1


class TestRuntime:
    def test_start_stop_idempotent(self) -> None:
        runtime = CollaborationRuntime()
        assert runtime.start() is True
        assert runtime.start() is False
        assert runtime.stop() is True
        assert runtime.stop() is False
        assert runtime.state()["running"] is False


class TestManagerAndEngine:
    def test_workspace_team_member_flow(self) -> None:
        engine = make_engine()
        ws = engine.create_workspace("NEXUS ERP PROJECT", owner_id="joao")
        assert ws.name == "NEXUS ERP PROJECT"
        team = engine.create_team(ws.workspace_id, "Desenvolvimento",
                                  kind=TeamKind.DEVELOPMENT)
        member = engine.add_member(ws.workspace_id, "João",
                                   role=MemberRole.DEVELOPER)
        agent = engine.add_agent(ws.workspace_id, "Coding Agent",
                                 skills=["python"])
        assert member.kind == MemberKind.HUMAN
        assert agent.kind == MemberKind.AGENT
        assert agent.name == "Coding Agent"
        assert engine.registry.stats()["workspaces"] == 1

    def test_project_task_lifecycle(self) -> None:
        engine = make_engine()
        ws = engine.create_workspace("Supermercado", owner_id="ana")
        project = engine.create_project(ws.workspace_id, "Sistema ERP")
        task = engine.create_task(project.project_id, ws.workspace_id,
                                  "Criar módulo financeiro",
                                  priority=TaskPriority.HIGH)
        assert task.title == "Criar módulo financeiro"
        assert engine.assign_task(task.task_id, "ana") is not None
        done = engine.update_task_status(task.task_id, TaskStatus.DONE)
        assert done is not None and done.progress == 100.0
        updated = engine.update_project_progress(project.project_id, 74.0)
        assert updated is not None and updated.progress == 74.0

    def test_comment_review_approval(self) -> None:
        engine = make_engine()
        ws = engine.create_workspace("WS", owner_id="x")
        project = engine.create_project(ws.workspace_id, "P1")
        comment = engine.add_comment(EntityKind.PROJECT, project.project_id,
                                     "dev-1", "Essa função precisa melhorar")
        assert comment.target_id == project.project_id
        assert len(engine.comments_for(project.project_id)) == 1

        review = engine.manager.create_review(ReviewKind.CODE, "pr-42", "dev-1")
        decided = engine.manager.decide_review(
            review.review_id, ReviewStatus.CHANGES_REQUESTED, 62.0,
            [{"severity": "high", "message": "índice ausente"}])
        assert decided is not None
        assert decided.status == ReviewStatus.CHANGES_REQUESTED
        assert decided.score == 62.0

        approval = engine.start_approval(EntityKind.PROJECT,
                                         project.project_id, "dev-1")
        final = engine.manager.decide_approval(approval.approval_id, True,
                                               "diretor", "aprovado")
        assert final is not None
        assert final.status == ApprovalStatus.APPROVED
        assert final.decided_by == "diretor"

    def test_communication_and_knowledge(self) -> None:
        engine = make_engine()
        ws = engine.create_workspace("WS", owner_id="x")
        channel = engine.manager.create_channel(ws.workspace_id, "#dev")
        message = engine.send_message(channel.channel_id, "mem-1",
                                      "Ajustei o índice da query")
        assert message.body == "Ajustei o índice da query"
        assert len(engine.messages_for(channel.channel_id)) == 1

        doc = engine.manager.add_document(ws.workspace_id, "Guia de deploy",
                                          "Passo a passo de release",
                                          tags=["devops"])
        found = engine.manager.search_documents("deploy")
        assert len(found) == 1
        assert found[0].document_id == doc.document_id

    def test_events_and_metrics(self) -> None:
        engine = make_engine()
        seen: list[str] = []
        engine.events.on(CollaborationEventType.TASK_COMPLETED,
                         lambda d: seen.append(d["task_id"]))
        ws = engine.create_workspace("WS", owner_id="x")
        project = engine.create_project(ws.workspace_id, "P")
        task = engine.create_task(project.project_id, ws.workspace_id, "T1")
        engine.update_task_status(task.task_id, TaskStatus.DONE)
        assert seen == [task.task_id]
        counters = engine.metrics.snapshot()["counters"]
        assert counters["collab.workspaces"] == 1
        assert counters["collab.tasks"] == 1

    def test_factory_overrides(self) -> None:
        engine = build_engine(workspace_name="Acme Corp")
        assert engine.config.workspace_name == "Acme Corp"
        assert isinstance(engine, CollaborationEngine)

    def test_attach_subsystem_and_backref(self) -> None:
        engine = make_engine()
        fake = object()
        engine.attach_subsystem("workspace", fake)
        assert engine.workspace is fake
        assert getattr(engine.manager, "workspace_engine") is fake
        assert "workspace" in engine.stats()["subsystems"]

    def test_stats(self) -> None:
        engine = make_engine()
        ws = engine.create_workspace("WS", owner_id="x")
        stats = engine.stats()
        assert stats["registry"]["workspaces"] == 1
        assert stats["metrics"]["counters"]["collab.workspaces"] == 1
        assert ws.workspace_id in engine.list_workspaces()
