"""Tests for comments/ and communication/ subsystems (Volume 26, Fase 5)."""

from __future__ import annotations

import pytest

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_factory import build_engine
from collaboration.collaboration_models import (EntityKind, MessageKind,
                                                MemberRole)
from collaboration.comments.comment_engine import CommentEngine
from collaboration.communication.communication_engine import (
    CommunicationEngine)


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "comment_engine",
        CommentEngine(events=engine.events, metrics=engine.metrics,
                      config=engine.config, security=engine.security,
                      registry=engine.registry))
    engine.attach_subsystem(
        "communication_engine",
        CommunicationEngine(events=engine.events, metrics=engine.metrics,
                            config=engine.config,
                            security=engine.security,
                            registry=engine.registry))
    return engine


def _setup(engine):
    ws = engine.create_workspace("NEXUS ERP PROJECT", "SP-01")
    owner = engine.add_member(ws.workspace_id, "Carlos Diretor",
                              role=MemberRole.OWNER,
                              email="carlos@nexus.com.br")
    dev = engine.add_member(ws.workspace_id, "Bruno Backend",
                            role=MemberRole.DEVELOPER,
                            email="bruno@nexus.com.br")
    project = engine.create_project(ws.workspace_id, "Sistema ERP")
    return ws, owner, dev, project


# -------------------------------------------------------------- comments ---

def test_comment_added(engine):
    ws, owner, dev, project = _setup(engine)
    comment = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id,
                                        "Preciso revisar este fluxo")
    assert comment is not None
    assert comment.comment_id.startswith("cmt")
    assert comment.target_id == "task_1"
    assert comment.author_id == dev.member_id


def test_comment_event(engine):
    ws, owner, dev, project = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.COMMENT_ADDED, events.append)
    comment = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id, "Comentário")
    assert events and events[-1]["comment_id"] == comment.comment_id


def test_comment_moderation_blocks(engine):
    ws, owner, dev, project = _setup(engine)
    blocked = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id, "isto é spam puro")
    assert blocked is None
    allowed = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id, "Tudo certo!")
    assert allowed is not None


def test_comment_thread_replies(engine):
    ws, owner, dev, project = _setup(engine)
    parent = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                       dev.member_id, "Pergunta inicial")
    reply = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                      owner.member_id, "Resposta",
                                      parent_id=parent.comment_id)
    replies = engine.comment_engine.replies(parent.comment_id)
    assert [r.comment_id for r in replies] == [reply.comment_id]


def test_comment_mentions(engine):
    ws, owner, dev, project = _setup(engine)
    comment = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id,
                                        "@carlos @agent:planner revise")
    mentions = engine.comment_engine.mentions("@carlos @agent:planner revise")
    assert "carlos" in mentions
    assert "agent" in mentions
    agent = engine.comment_engine.agent_mentions(
        "@agent:planner revise isso")
    assert "planner" in agent


def test_comment_remove(engine):
    ws, owner, dev, project = _setup(engine)
    comment = engine.comment_engine.add(EntityKind.TASK, "task_1",
                                        dev.member_id, "Apagar")
    assert engine.comment_engine.remove(comment.comment_id) is True
    assert engine.comment_engine.for_target("task_1") == []


# --------------------------------------------------------- communication ---

def test_channel_creation(engine):
    ws, _, _, _ = _setup(engine)
    channel = engine.communication_engine.create_channel(
        ws.workspace_id, "geral", topic="Comunicação geral")
    assert channel.channel_id.startswith("chan")
    assert channel.name == "geral"
    assert channel.workspace_id == ws.workspace_id
    assert channel.channel_id in engine.communication_engine.list_channels()


def test_channel_join_leave(engine):
    ws, owner, dev, _ = _setup(engine)
    channel = engine.communication_engine.create_channel(
        ws.workspace_id, "vendas-app")
    engine.communication_engine.join(channel.channel_id, dev.member_id)
    assert dev.member_id in channel.members
    engine.communication_engine.leave(channel.channel_id, dev.member_id)
    assert dev.member_id not in channel.members


def test_send_message_event(engine):
    ws, owner, dev, _ = _setup(engine)
    channel = engine.communication_engine.create_channel(
        ws.workspace_id, "ia-agents")
    events = []
    engine.events.on(CollaborationEventType.MESSAGE_SENT, events.append)
    message = engine.communication_engine.send(channel.channel_id,
                                               dev.member_id,
                                               "Olá equipe")
    assert message is not None
    assert message.kind == MessageKind.CHAT
    assert events and events[-1]["message_id"] == message.message_id


def test_agent_message_in_channel(engine):
    ws, owner, dev, _ = _setup(engine)
    agent = engine.add_agent(ws.workspace_id, "Coder IA")
    channel = engine.communication_engine.create_channel(
        ws.workspace_id, "ia-agents")
    engine.communication_engine.join(channel.channel_id, agent.member_id)
    engine.communication_engine.join(channel.channel_id, dev.member_id)
    message = engine.communication_engine.messages.from_agent(
        channel.channel_id, agent.member_id, "Tarefa concluída")
    assert message.author_id == agent.member_id
    messages = engine.communication_engine.messages_for(channel.channel_id)
    assert any(m.message_id == message.message_id for m in messages)


def test_direct_messages_and_unread(engine):
    ws, owner, dev, _ = _setup(engine)
    engine.communication_engine.send_dm(dev.member_id, owner.member_id,
                                        "Pode aprovar?")
    engine.communication_engine.send_dm(dev.member_id, owner.member_id,
                                        "Só lembrete")
    unread = engine.communication_engine.unread_dms(owner.member_id)
    assert len(unread) == 2
    thread = engine.communication_engine.dm_thread(dev.member_id,
                                                   owner.member_id)
    assert len(thread) == 2


def test_dm_human_agent(engine):
    ws, owner, dev, _ = _setup(engine)
    planner = engine.add_agent(ws.workspace_id, "Planner IA")
    engine.communication_engine.send_dm(planner.member_id, owner.member_id,
                                        "Plano pronto para revisão")
    unread = engine.communication_engine.unread_dms(owner.member_id)
    assert any(m.sender_id == planner.member_id for m in unread)


def test_notifications(engine):
    ws, owner, dev, _ = _setup(engine)
    engine.communication_engine.notify(dev.member_id, "task",
                                       "Nova tarefa atribuída")
    engine.communication_engine.notify(dev.member_id, "review",
                                       "Review solicitado")
    notifications = engine.communication_engine.notifications_for(
        dev.member_id)
    assert len(notifications) == 2
    assert len(engine.communication_engine.unread_notifications(
        dev.member_id)) == 2
    engine.communication_engine.mark_notification_read(
        notifications[0].notification_id)
    assert len(engine.communication_engine.unread_notifications(
        dev.member_id)) == 1


def test_announcements(engine):
    ws, owner, dev, _ = _setup(engine)
    channel = engine.communication_engine.create_channel(
        ws.workspace_id, "geral")
    engine.communication_engine.announce(
        ws.workspace_id, "Release 1.0", "ERP vai ao ar sexta",
        owner.member_id, channel_id=channel.channel_id)
    announcements = engine.communication_engine.announcements_list(
        ws.workspace_id)
    assert len(announcements) == 1
    assert announcements[0].title == "Release 1.0"
    messages = engine.communication_engine.messages_for(channel.channel_id)
    assert any("ANÚNCIO" in m.body for m in messages)


def test_communication_stats(engine):
    ws, owner, dev, _ = _setup(engine)
    engine.communication_engine.create_channel(ws.workspace_id, "geral")
    stats = engine.communication_engine.stats()
    assert stats["channels"] >= 1
