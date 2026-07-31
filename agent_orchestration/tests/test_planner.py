"""Tests for the planner/ subpackage (Volume 31, Fase 2)."""

from __future__ import annotations

import pytest

from agent_orchestration.agents import AgentFactory
from agent_orchestration.orchestrator_events import (OrchestratorEventType,
                                                     OrchestratorEvents)
from agent_orchestration.orchestrator_models import TaskStatus
from agent_orchestration.planner import (DependencyMapper, PlannerEngine,
                                         ResourcePlanner, StrategyBuilder,
                                         TaskAnalyzer, TaskBreaker)


class TestTaskAnalyzer:
    def test_complexity(self):
        analyzer = TaskAnalyzer()
        assert analyzer.analyze("oi")["complexity"] == "low"
        assert analyzer.analyze("criar um sistema com quatro itens")[
            "complexity"] == "medium"
        assert analyzer.analyze(
            "criar um sistema completo de gestão empresarial com módulos de "
            "estoque compras vendas financeiro e relatórios")[
            "complexity"] == "high"

    def test_requirements_dedup(self):
        analyzer = TaskAnalyzer()
        requirements = analyzer.requirements(
            "criar sistema financeiro financeiro app")
        assert requirements.count("financeiro") == 1
        assert "sistema" in requirements

    def test_extract_domain(self):
        analyzer = TaskAnalyzer()
        assert analyzer.extract_domain("Criar um ERP para supermercado") == "erp"
        assert analyzer.extract_domain("site institucional") == "site"
        assert analyzer.extract_domain("qualquer coisa") == "general"


class TestTaskBreaker:
    def test_break_down_standard(self):
        breaker = TaskBreaker()
        tasks = breaker.break_down("criar erp", plan_id="plan-1")
        assert len(tasks) == 7
        assert tasks[0].title == "Analisar requisitos"
        assert tasks[-1].title == "Publicar"
        assert all(task.plan_id == "plan-1" for task in tasks)
        assert all(task.status == TaskStatus.PENDING for task in tasks)

    def test_custom(self):
        breaker = TaskBreaker()
        tasks = breaker.custom(["A", "B"])
        assert [task.title for task in tasks] == ["A", "B"]

    def test_single(self):
        breaker = TaskBreaker()
        task = breaker.single("Só uma etapa")
        assert task.title == "Só uma etapa"
        assert task.task_id.startswith("task-")


class TestDependencyMapper:
    def test_link_sequential(self):
        mapper = DependencyMapper()
        breaker = TaskBreaker()
        tasks = mapper.link_sequential(breaker.custom(["A", "B", "C"]))
        assert tasks[1].dependencies == [tasks[0].task_id]
        assert tasks[2].dependencies == [tasks[1].task_id]
        assert tasks[0].dependencies == []

    def test_add_dependency_no_duplicate(self):
        mapper = DependencyMapper()
        breaker = TaskBreaker()
        a, b = breaker.custom(["A", "B"])
        mapper.add_dependency(a, b)
        mapper.add_dependency(a, b)
        assert a.dependencies == [b.task_id]

    def test_cycle_detection(self):
        mapper = DependencyMapper()
        breaker = TaskBreaker()
        a, b = breaker.custom(["A", "B"])
        mapper.add_dependency(a, b)
        mapper.add_dependency(b, a)
        assert mapper.has_cycle([a, b])
        assert mapper.order([a, b]) == []

    def test_topological_order(self):
        mapper = DependencyMapper()
        breaker = TaskBreaker()
        tasks = mapper.link_sequential(breaker.custom(["A", "B", "C"]))
        order = mapper.order(tasks)
        assert order == [tasks[0].task_id, tasks[1].task_id, tasks[2].task_id]


class TestStrategyBuilder:
    def test_parallel_when_independent(self):
        builder = StrategyBuilder()
        breaker = TaskBreaker()
        tasks = breaker.custom(["A", "B"])
        assert builder.build(tasks) == "parallel"

    def test_sequential_when_linked(self):
        builder = StrategyBuilder()
        mapper = DependencyMapper()
        breaker = TaskBreaker()
        tasks = mapper.link_sequential(breaker.custom(["A", "B", "C"]))
        assert builder.build(tasks) == "sequential"

    def test_estimate_duration(self):
        builder = StrategyBuilder()
        breaker = TaskBreaker()
        tasks = breaker.custom(["A", "B"])
        assert builder.estimate_duration(tasks, unit=1.0) == 1.5
        linked = DependencyMapper().link_sequential(tasks)
        assert builder.estimate_duration(linked, unit=1.0) == 2.0


class TestResourcePlanner:
    def test_assigns_by_capability(self):
        planner = ResourcePlanner()
        factory = AgentFactory()
        agents = factory.create_team(["data", "coding"])
        breaker = TaskBreaker()
        tasks = breaker.custom(["Criar banco de dados", "Desenvolver API"])
        planner.assign(tasks, agents)
        data_agent = next(a for a in agents if a.has_capability("data"))
        code_agent = next(a for a in agents if a.has_capability("code"))
        assert tasks[0].agent_id == data_agent.agent_id
        assert tasks[1].agent_id == code_agent.agent_id

    def test_fallback_to_first_agent(self):
        planner = ResourcePlanner()
        factory = AgentFactory()
        agents = [factory.create("testing")]
        breaker = TaskBreaker()
        tasks = breaker.custom(["Criar banco de dados"])
        planner.assign(tasks, agents)
        assert tasks[0].agent_id == agents[0].agent_id

    def test_plan_assignment_mapping(self):
        planner = ResourcePlanner()
        factory = AgentFactory()
        agents = factory.create_coding_team()
        breaker = TaskBreaker()
        tasks = breaker.custom(["Testar", "Publicar"])
        assignment = planner.plan_assignment(tasks, agents)
        assert set(assignment) == {task.task_id for task in tasks}
        assert all(assignment[task.task_id] for task in tasks)


class TestPlannerEngine:
    def test_plan_registers_and_links(self):
        engine = PlannerEngine()
        tasks = engine.plan("criar erp para supermercado")
        assert len(tasks) == 7
        assert engine.stats()["tasks"] == 7
        assert engine.get_task(tasks[0].task_id) is tasks[0]
        assert engine.topological() == [task.task_id for task in tasks]

    def test_plan_publishes_events(self):
        events = OrchestratorEvents()
        engine = PlannerEngine(events=events)
        fired = []
        events.on(OrchestratorEventType.TASK_PLANNED,
                  lambda payload: fired.append(payload))
        tasks = engine.plan("criar api")
        assert len(fired) == len(tasks)

    def test_plan_assigns_agents(self):
        engine = PlannerEngine()
        factory = AgentFactory()
        agents = factory.create_coding_team()
        tasks = engine.plan("criar sistema financeiro", agents=agents)
        assert all(task.agent_id for task in tasks)
        assert engine.stats()["plans"] == 1
