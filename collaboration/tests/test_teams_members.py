"""Tests for teams/ and members/ subsystems (Volume 26, Fase 3)."""

from __future__ import annotations

import pytest

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_factory import build_engine
from collaboration.collaboration_models import (MemberKind, MemberRole,
                                                MemberStatus, TeamKind)
from collaboration.members.member_engine import MemberEngine
from collaboration.teams.team_engine import TeamEngine
from collaboration.teams.team_roles import TeamRoles
from collaboration.teams.team_structure import TeamStructure


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "team_engine",
        TeamEngine(events=engine.events, metrics=engine.metrics,
                   config=engine.config, context=engine.context,
                   security=engine.security, registry=engine.registry))
    engine.attach_subsystem(
        "member_engine",
        MemberEngine(events=engine.events, metrics=engine.metrics,
                     config=engine.config, security=engine.security,
                     registry=engine.registry))
    return engine


def _setup(engine):
    ws = engine.create_workspace("NEXUS ERP PROJECT", "SP-01")
    owner = engine.add_member(ws.workspace_id, "Carlos Diretor",
                              role=MemberRole.OWNER,
                              email="carlos@nexus.com.br")
    tech = engine.add_member(ws.workspace_id, "Ana Tech Lead",
                             role=MemberRole.ADMIN,
                             email="ana@nexus.com.br")
    return ws, owner, tech


# ---------------------------------------------------------------- teams ---

def test_team_creation_publishes_event(engine):
    ws, _, _ = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.TEAM_CREATED, events.append)
    team = engine.team_engine.create(ws.workspace_id, "Desenvolvimento",
                                     TeamKind.DEVELOPMENT,
                                     lead_id="member_lead")
    assert team.team_id.startswith("team")
    assert team.kind == TeamKind.DEVELOPMENT
    assert team.lead_id == "member_lead"
    assert engine.team_engine.get(team.team_id) is team
    assert team.team_id in engine.list_teams()
    assert events and events[-1]["team_id"] == team.team_id


def test_team_kinds_roles(engine):
    roles = TeamRoles()
    assert roles.has_role(TeamKind.SECURITY, MemberRole.SECURITY)
    assert not roles.has_role(TeamKind.MANAGEMENT, MemberRole.DEVELOPER)
    assert MemberRole.OWNER in roles.roles_for(TeamKind.MANAGEMENT)


def test_team_structure_summary(engine):
    ws, _, _ = _setup(engine)
    team = engine.team_engine.create(ws.workspace_id, "Qualidade",
                                     TeamKind.QUALITY)
    summary = engine.team_engine.summary(team.team_id)
    assert summary["kind"] == "quality"
    assert "roles" in summary and summary["roles"]


def test_team_settings_update(engine):
    ws, _, _ = _setup(engine)
    team = engine.team_engine.create(ws.workspace_id, "Ops",
                                     TeamKind.OPERATIONS)
    settings = engine.team_engine.update_settings(team.team_id,
                                                  allow_agents=False,
                                                  max_members=20)
    assert settings["settings"]["allow_agents"] is False
    assert settings["settings"]["max_members"] == 20


def test_team_activity_records(engine):
    ws, _, _ = _setup(engine)
    team = engine.team_engine.create(ws.workspace_id, "Dev",
                                     TeamKind.DEVELOPMENT)
    engine.team_engine.record_activity(team.team_id, "team.lead_changed",
                                       ws.workspace_id)
    entries = engine.team_engine.activity(team.team_id)
    assert any(e["action"] == "team.lead_changed" for e in entries)


def test_team_remove(engine):
    ws, _, _ = _setup(engine)
    team = engine.team_engine.create(ws.workspace_id, "Temp",
                                     TeamKind.DEVELOPMENT)
    team_id = team.team_id
    assert engine.team_engine.remove(team_id) is True
    assert engine.team_engine.get(team_id) is None
    assert team_id not in engine.list_teams()


def test_team_by_kind(engine):
    ws, _, _ = _setup(engine)
    engine.team_engine.create(ws.workspace_id, "Seg",
                              TeamKind.SECURITY)
    security_teams = engine.team_engine.by_kind(TeamKind.SECURITY)
    assert all(t.kind == TeamKind.SECURITY for t in security_teams)


def test_team_increments_metric(engine):
    ws, _, _ = _setup(engine)
    before = engine.metrics.snapshot()["counters"].get("collab.teams", 0)
    engine.team_engine.create(ws.workspace_id, "Agents",
                              TeamKind.AGENTS)
    after = engine.metrics.snapshot()["counters"].get("collab.teams", 0)
    assert after == before + 1


# -------------------------------------------------------------- members ---

def test_member_add_human(engine):
    ws, _, _ = _setup(engine)
    member = engine.add_member(ws.workspace_id, "Bruno Backend",
                               role=MemberRole.DEVELOPER,
                               email="bruno@nexus.com.br",
                               skills=["python", "api"])
    assert member.member_id.startswith("mem")
    assert member.kind == MemberKind.HUMAN
    assert member.status == MemberStatus.ACTIVE
    assert member.skills == ["python", "api"]
    assert engine.get_member(member.member_id) is member
    assert member.member_id in engine.list_members()


def test_member_add_agent(engine):
    ws, _, _ = _setup(engine)
    agent = engine.add_agent(ws.workspace_id, "Planner IA",
                             skills=["planejamento"])
    assert agent.kind == MemberKind.AGENT
    assert agent.role == MemberRole.DEVELOPER
    agents = engine.member_engine.agents_in(ws.workspace_id)
    assert any(a.member_id == agent.member_id for a in agents)


def test_member_joined_event(engine):
    ws, _, _ = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.MEMBER_JOINED, events.append)
    member = engine.add_member(ws.workspace_id, "Julia QA",
                               role=MemberRole.REVIEWER,
                               email="julia@nexus.com.br")
    assert events and events[-1]["member_id"] == member.member_id
    assert events[-1]["kind"] == "human"


def test_member_remove(engine):
    ws, _, _ = _setup(engine)
    member = engine.add_member(ws.workspace_id, "Temp Dev",
                               role=MemberRole.DEVELOPER)
    member_id = member.member_id
    assert engine.remove_member(member_id) is True
    assert engine.get_member(member_id) is None


def test_member_status_change(engine):
    ws, _, _ = _setup(engine)
    member = engine.add_member(ws.workspace_id, "Busy Dev",
                               role=MemberRole.DEVELOPER)
    updated = engine.member_engine.set_status(member.member_id,
                                              MemberStatus.INVITED)
    assert updated.status == MemberStatus.INVITED
    assert engine.get_member(member.member_id).status == MemberStatus.INVITED


def test_member_by_workspace(engine):
    ws, _, _ = _setup(engine)
    ws2 = engine.create_workspace("OUTRO", "SP-02")
    engine.add_member(ws.workspace_id, "Dev A", role=MemberRole.DEVELOPER)
    engine.add_member(ws2.workspace_id, "Dev B", role=MemberRole.DEVELOPER)
    ws_members = engine.member_engine.by_workspace(ws.workspace_id)
    names = {m.name for m in ws_members}
    assert "Dev A" in names
    assert "Dev B" not in names


def test_invitation_flow(engine):
    ws, _, _ = _setup(engine)
    invite = engine.member_engine.invite(ws.workspace_id,
                                         "novo@nexus.com.br",
                                         role=MemberRole.DEVELOPER)
    assert invite.status == "pending"
    member = engine.member_engine.accept_invite(invite.invitation_id,
                                                "Novo Membro")
    assert member is not None
    assert member.email == "novo@nexus.com.br"
    assert invite.status == "accepted"


def test_invitation_decline(engine):
    ws, _, _ = _setup(engine)
    invite = engine.member_engine.invite(ws.workspace_id,
                                         "recusa@nexus.com.br")
    assert engine.member_engine.invitations.decline(
        invite.invitation_id) is invite
    assert invite.status == "declined"
    pending = engine.member_engine.invitations.pending_for(
        "recusa@nexus.com.br")
    assert pending == []


def test_member_profile_and_availability(engine):
    ws, _, _ = _setup(engine)
    member = engine.member_engine.add(ws.workspace_id, "Perfil Dev",
                                      role=MemberRole.DEVELOPER)
    profile = engine.member_engine.profiles.update(
        member.member_id, bio="Backend sênior")
    assert profile is not None and profile.bio == "Backend sênior"
    assert engine.member_engine.set_available(member.member_id,
                                              "busy") is True
    assert member.member_id not in engine.member_engine.available_members()
    assert engine.member_engine.set_available(member.member_id) is True
    assert member.member_id in engine.member_engine.available_members()


def test_member_permissions_matrix(engine):
    perms = engine.member_engine.permissions
    assert perms.can_manage(MemberRole.OWNER)
    assert perms.can_manage(MemberRole.ADMIN)
    assert not perms.can_manage(MemberRole.DEVELOPER)
    assert perms.can_review(MemberRole.REVIEWER)
    assert not perms.can_review(MemberRole.DEVELOPER)


def test_member_activity_log(engine):
    ws, _, _ = _setup(engine)
    member = engine.add_member(ws.workspace_id, "Ativo Dev",
                               role=MemberRole.DEVELOPER)
    engine.member_engine.record_activity(member.member_id, "task.completed",
                                         target="task_123")
    entries = engine.member_engine.activity(member.member_id)
    assert any(e["action"] == "task.completed"
               and e["target"] == "task_123" for e in entries)


def test_agents_as_ia_collaborators(engine):
    ws, _, _ = _setup(engine)
    planner = engine.add_agent(ws.workspace_id, "Planner",
                               skills=["roadmap"])
    coder = engine.add_agent(ws.workspace_id, "Coder",
                             skills=["python"])
    tester = engine.add_agent(ws.workspace_id, "Tester",
                              skills=["qa"])
    agents = engine.member_engine.agents_in(ws.workspace_id)
    ids = {a.member_id for a in agents}
    assert {planner.member_id, coder.member_id, tester.member_id} <= ids
    assert all(a.kind == MemberKind.AGENT for a in agents)
