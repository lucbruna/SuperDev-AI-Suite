"""Tests for projects/ and tasks/ subsystems (Volume 26, Fase 4)."""

from __future__ import annotations

import pytest

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_factory import build_engine
from collaboration.collaboration_models import (MemberKind, MemberRole,
                                                ProjectStatus, TaskPriority,
                                                TaskStatus)
from collaboration.projects.project_engine import ProjectEngine
from collaboration.tasks.task_engine import TaskEngine


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "project_engine",
        ProjectEngine(events=engine.events, metrics=engine.metrics,
                      config=engine.config, security=engine.security,
                      registry=engine.registry))
    engine.attach_subsystem(
        "task_engine",
        TaskEngine(events=engine.events, metrics=engine.metrics,
                   config=engine.config, security=engine.security,
                   registry=engine.registry))
    return engine


def _setup(engine):
    ws = engine.create_workspace("NEXUS ERP PROJECT", "SP-01")
    owner = engine.add_member(ws.workspace_id, "Carlos Diretor",
                              role=MemberRole.OWNER,
                              email="carlos@nexus.com.br")
    project = engine.project_engine.create(
        ws.workspace_id, "Sistema Supermercado ERP",
        owner_id=owner.member_id,
        description="ERP para supermercado")
    return ws, owner, project


# -------------------------------------------------------------- projects ---

def test_project_creation_with_phases(engine):
    ws, _, project = _setup(engine)
    assert project.project_id.startswith("prj")
    assert project.status == ProjectStatus.PLANNING
    assert project.progress == 0.0
    structure = engine.project_engine.structure(project.project_id)
    names = [p["name"] for p in structure["phases"]]
    assert names == ["Planejamento", "Desenvolvimento", "Testes", "Deploy"]
    assert project.project_id in engine.list_projects()


def test_project_created_event(engine):
    ws, _, _ = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.PROJECT_CREATED, events.append)
    project = engine.project_engine.create(ws.workspace_id, "App Vendas",
                                           "SP-01")
    assert events and events[-1]["project_id"] == project.project_id


def test_project_progress_updates_metric_and_event(engine):
    ws, _, project = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.PROJECT_UPDATED, events.append)
    updated = engine.project_engine.update_progress(project.project_id, 74.0)
    assert updated.progress == 74.0
    gauge = engine.metrics.snapshot()["gauges"].get(
        f"collab.progress.{project.project_id}")
    assert gauge == 74.0
    assert events and events[-1]["progress"] == 74.0


def test_project_update_status(engine):
    ws, _, project = _setup(engine)
    updated = engine.project_engine.update_status(project.project_id,
                                                  ProjectStatus.ACTIVE)
    assert updated.status == ProjectStatus.ACTIVE
    assert engine.project_engine.get(project.project_id).status \
        == ProjectStatus.ACTIVE


def test_project_by_workspace(engine):
    ws, _, project = _setup(engine)
    ws2 = engine.create_workspace("OUTRO", "SP-02")
    engine.project_engine.create(ws2.workspace_id, "Outro Projeto")
    projects = engine.project_engine.by_workspace(ws.workspace_id)
    assert len(projects) == 1
    assert projects[0].name == "Sistema Supermercado ERP"


def test_project_modules(engine):
    ws, _, project = _setup(engine)
    structure = engine.project_engine.structure(project.project_id)
    dev_phase = next(p for p in structure["phases"]
                     if p["name"] == "Desenvolvimento")
    module_id = engine.project_engine.add_module(project.project_id, "Vendas",
                                                 phase_id=dev_phase["phase_id"])
    structure = engine.project_engine.structure(project.project_id)
    modules = structure["modules"]
    assert any(m["module_id"] == module_id and m["name"] == "Vendas"
               for m in modules)


def test_project_settings_update(engine):
    ws, _, project = _setup(engine)
    settings = engine.project_engine.update_settings(project.project_id,
                                                     allow_agents=False)
    assert settings["settings"]["allow_agents"] is False
    assert settings["settings"]["require_approval"] is True


def test_project_metrics(engine):
    ws, _, project = _setup(engine)
    metrics = engine.project_engine.metrics_for(project.project_id)
    assert metrics.progress(40.0, 100.0) == 40.0
    dist = metrics.distribution(10, 7, 2, 1)
    assert dist["pct_done"] == 70.0
    assert metrics.risk(blocked=1, overdue=1, total=10) in \
        ("low", "medium", "high")


def test_project_activity(engine):
    ws, _, project = _setup(engine)
    engine.project_engine.record_activity(project.project_id,
                                          "project.milestone",
                                          ws.workspace_id)
    entries = engine.project_engine.activity(project.project_id)
    assert any(e["action"] == "project.milestone" for e in entries)


def test_project_remove(engine):
    ws, _, project = _setup(engine)
    project_id = project.project_id
    assert engine.project_engine.remove(project_id) is True
    assert engine.project_engine.get(project_id) is None


# ---------------------------------------------------------------- tasks ----

def test_task_creation(engine):
    ws, _, project = _setup(engine)
    task = engine.task_engine.create(
        project.project_id, ws.workspace_id, "Criar aplicativo de vendas",
        priority=TaskPriority.HIGH)
    assert task.task_id.startswith("task")
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.HIGH
    assert engine.task_engine.get(task.task_id) is task
    assert task.task_id in engine.list_tasks()


def test_task_created_event(engine):
    ws, _, project = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.TASK_CREATED, events.append)
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Tarefa Nova")
    assert events and events[-1]["task_id"] == task.task_id


def test_task_assign_to_agent(engine):
    ws, _, project = _setup(engine)
    agent = engine.add_agent(ws.workspace_id, "Coder IA",
                             skills=["python"])
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Implementar API")
    events = []
    engine.events.on(CollaborationEventType.TASK_ASSIGNED, events.append)
    assignee_id = engine.task_engine.assign(task.task_id, agent)
    assert assignee_id == agent.member_id
    assert engine.task_engine.get(task.task_id).assignee_id \
        == agent.member_id
    assert events and events[-1]["assignee_id"] == agent.member_id


def test_task_status_transition(engine):
    ws, _, project = _setup(engine)
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Tarefa Fluxo")
    engine.task_engine.update_status(task.task_id, TaskStatus.IN_PROGRESS)
    engine.task_engine.update_status(task.task_id, TaskStatus.IN_REVIEW)
    engine.task_engine.update_status(task.task_id, TaskStatus.DONE)
    assert engine.task_engine.get(task.task_id).status == TaskStatus.DONE


def test_task_invalid_transition_ignored(engine):
    ws, _, project = _setup(engine)
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Tarefa Salto")
    options = engine.task_engine.status_options(TaskStatus.TODO)
    assert "done" in options
    engine.task_engine.update_status(task.task_id, TaskStatus.DONE)
    engine.task_engine.update_status(task.task_id, TaskStatus.IN_REVIEW)
    assert engine.task_engine.get(task.task_id).status == TaskStatus.DONE


def test_task_completed_event(engine):
    ws, _, project = _setup(engine)
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Tarefa Pronta")
    events = []
    engine.events.on(CollaborationEventType.TASK_COMPLETED, events.append)
    engine.task_engine.update_status(task.task_id, TaskStatus.IN_PROGRESS)
    engine.task_engine.update_status(task.task_id, TaskStatus.DONE)
    assert events and events[-1]["task_id"] == task.task_id


def test_task_dependencies(engine):
    ws, _, project = _setup(engine)
    setup = engine.task_engine.create(project.project_id, ws.workspace_id,
                                      "Setup ambiente")
    impl = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Implementar")
    engine.task_engine.add_dependency(impl.task_id, setup.task_id)
    assert engine.task_engine.blockers(impl.task_id) == [setup.task_id]
    assert engine.task_engine.ready(impl.task_id) is False
    engine.task_engine.update_status(setup.task_id, TaskStatus.IN_PROGRESS)
    engine.task_engine.update_status(setup.task_id, TaskStatus.DONE)
    assert engine.task_engine.ready(impl.task_id) is True


def test_task_scheduler_least_loaded(engine):
    ws, _, project = _setup(engine)
    a = engine.add_agent(ws.workspace_id, "Agent A", skills=["qa"])
    b = engine.add_agent(ws.workspace_id, "Agent B", skills=["qa"])
    t1 = engine.task_engine.create(project.project_id, ws.workspace_id, "T1")
    t2 = engine.task_engine.create(project.project_id, ws.workspace_id, "T2")
    engine.task_engine.assign(t1.task_id, a)
    scheduler = engine.task_engine.scheduler()
    assert scheduler.load_of(a.member_id) > 0
    picked = scheduler.least_loaded([a, b], required_skill="qa")
    assert picked.member_id == b.member_id
    engine.task_engine.assign(t2.task_id, b)


def test_task_by_project_and_order(engine):
    ws, _, project = _setup(engine)
    engine.task_engine.create(project.project_id, ws.workspace_id, "Primeira")
    engine.task_engine.create(project.project_id, ws.workspace_id, "Segunda")
    tasks = engine.task_engine.by_project(project.project_id)
    assert len(tasks) == 2
    ordered = engine.task_engine.ordered()
    assert [t.title for t in ordered] == ["Primeira", "Segunda"]


def test_task_priority_sort(engine):
    ws, _, project = _setup(engine)
    engine.task_engine.create(project.project_id, ws.workspace_id, "Baixa",
                              priority=TaskPriority.LOW)
    engine.task_engine.create(project.project_id, ws.workspace_id, "Urgente",
                              priority=TaskPriority.URGENT)
    from collaboration.tasks.task_priorities import prioritize
    tasks = engine.task_engine.by_project(project.project_id)
    ordered = prioritize(tasks)
    assert ordered[0].title == "Urgente"


def test_task_remove(engine):
    ws, _, project = _setup(engine)
    task = engine.task_engine.create(project.project_id, ws.workspace_id,
                                     "Descartável")
    task_id = task.task_id
    assert engine.task_engine.remove(task_id) is True
    assert engine.task_engine.get(task_id) is None
