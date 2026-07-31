"""Tests for the orchestration subsystem (Volume 20, Fase 3)."""

from __future__ import annotations

from automation.automation_events import AutomationEventType, AutomationEvents
from automation.orchestration.orchestration_agent import OrchestrationAgent
from automation.orchestration.orchestration_coordinator import OrchestrationCoordinator
from automation.orchestration.orchestration_dispatcher import OrchestrationDispatcher
from automation.orchestration.orchestration_engine import OrchestrationEngine
from automation.orchestration.orchestration_models import (OrchestrationPlan,
                                                           OrchestrationTask,
                                                           TaskStatus)
from automation.orchestration.orchestration_monitor import OrchestrationMonitor
from automation.orchestration.orchestration_planner import OrchestrationPlanner


class TestOrchestrationPlanner:
    def test_default_pipeline_structure(self) -> None:
        plan = OrchestrationPlanner().plan("adicionar autenticacao")
        assert plan.goal == "adicionar autenticacao"
        assert len(plan.tasks) == 5
        kinds = [t.kind for t in plan.tasks]
        assert kinds == ["plan", "implement", "test", "security_review", "deploy"]
        # dependencies: t2 <- t1; t3,t4 <- t2; t5 <- t3,t4
        assert plan.task("t5").depends_on == ["t3", "t4"]
        assert plan.task("t2").depends_on == ["t1"]
        assert plan.task("t1").depends_on == []

    def test_custom_plan(self) -> None:
        tasks = [OrchestrationTask("a", "Analisar", "analista", "plan")]
        plan = OrchestrationPlanner().custom("meta", tasks, plan_id="plan-x")
        assert plan.plan_id == "plan-x"
        assert plan.task("a") is not None
        assert plan.by_agent("analista") == [tasks[0]]


class TestOrchestrationAgent:
    def test_capabilities(self) -> None:
        agent = OrchestrationAgent("dev", "Developer", ["implement"])
        assert agent.can_handle("implement") is True
        assert agent.can_handle("deploy") is False

    def test_execute_with_handler(self) -> None:
        agent = OrchestrationAgent("dev", "Developer", ["implement"],
                                   handler=lambda t: {"code": t.task_id})
        task = OrchestrationTask("t2", "Codigo", "dev", "implement")
        assert agent.execute(task) == {"code": "t2"}

    def test_execute_without_handler_raises(self) -> None:
        agent = OrchestrationAgent("ghost", "Fantasma", ["implement"])
        task = OrchestrationTask("t9", "X", "ghost", "implement")
        try:
            agent.execute(task)
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass


class TestOrchestrationDispatcher:
    def _agents(self) -> list[OrchestrationAgent]:
        def make(agent_id: str, kind: str) -> OrchestrationAgent:
            return OrchestrationAgent(
                agent_id, agent_id, [kind],
                handler=lambda t, k=kind: {f"{k}_done": True})
        return [make("planner", "plan"),
                make("developer", "implement"),
                make("tester", "test"),
                make("security", "security_review"),
                make("devops", "deploy")]

    def test_dispatch_respects_dependencies(self) -> None:
        plan = OrchestrationPlanner().plan("Nova solicitação: login")
        order: list[str] = []
        dispatcher = OrchestrationDispatcher()

        # wrap handlers to record order
        agents = self._agents()
        for agent in agents:
            original = agent.handler
            agent.handler = lambda t, orig=original: (
                order.append(t.task_id) or orig(t))
        dispatcher.dispatch(plan, agents)

        assert order == ["t1", "t2", "t3", "t4", "t5"]
        assert plan.status == TaskStatus.COMPLETED
        assert all(t.status == TaskStatus.COMPLETED for t in plan.tasks)
        assert plan.task("t5").result == {"deploy_done": True}

    def test_failure_skips_dependents(self) -> None:
        agents = self._agents()
        for agent in agents:
            if agent.agent_id == "developer":
                agent.handler = lambda t: (_ for _ in ()).throw(
                    RuntimeError("build quebrou"))
        plan = OrchestrationPlanner().plan("meta")
        OrchestrationDispatcher().dispatch(plan, agents)
        assert plan.status == TaskStatus.FAILED
        assert plan.task("t2").status == TaskStatus.FAILED
        assert plan.task("t3").status == TaskStatus.SKIPPED
        assert plan.task("t4").status == TaskStatus.SKIPPED
        assert plan.task("t5").status == TaskStatus.SKIPPED

    def test_missing_agent_fails_task(self) -> None:
        plan = OrchestrationPlanner().plan("meta")
        dispatcher = OrchestrationDispatcher()
        # only the planner agent is registered -> downstream agents missing
        dispatcher.dispatch(plan, [self._agents()[0]])
        assert plan.status == TaskStatus.FAILED
        assert plan.task("t2").error is not None

    def test_monitor_tracks_progress(self) -> None:
        monitor = OrchestrationMonitor()
        dispatcher = OrchestrationDispatcher(monitor)
        plan = OrchestrationPlanner().plan("meta")
        dispatcher.dispatch(plan, self._agents())
        progress = monitor.progress(plan)
        assert progress["total"] == 5
        assert progress["completed"] == 5
        assert progress["percent"] == 100.0
        assert monitor.status("t5") == TaskStatus.COMPLETED


class TestOrchestrationCoordinator:
    def test_register_and_dispatch(self) -> None:
        coordinator = OrchestrationCoordinator()

        def developer_handler(task: OrchestrationTask) -> dict[str, object]:
            return {"code": task.params.get("feature", "default")}

        coordinator.register_agent(
            OrchestrationAgent("developer", "Developer", ["implement"],
                               developer_handler))
        coordinator.register_agent(
            OrchestrationAgent("planner", "Planner", ["plan"],
                               lambda t: {"tasks": 3}))
        coordinator.register_agent(
            OrchestrationAgent("tester", "Tester", ["test"],
                               lambda t: {"passed": 12}))
        coordinator.register_agent(
            OrchestrationAgent("security", "Security", ["security_review"],
                               lambda t: {"secure": True}))
        coordinator.register_agent(
            OrchestrationAgent("devops", "DevOps", ["deploy"],
                               lambda t: {"published": "v1.2.0"}))

        plan = coordinator.plan("adicionar autenticacao", ["planner", "developer",
                                                          "tester", "security",
                                                          "devops"])
        coordinator.dispatch(plan.plan_id)
        progress = coordinator.progress(plan.plan_id)
        assert progress["percent"] == 100.0
        results = coordinator.results(plan.plan_id)
        assert results["t5"] == {"published": "v1.2.0"}
        assert coordinator.results(plan.plan_id)["t4"] == {"secure": True}


class TestOrchestrationEngine:
    def test_full_dev_workflow(self) -> None:
        """Nova solicitação -> Planner cria tarefas -> Developer cria código ->
        Testing valida -> Security verifica -> DevOps publica."""
        engine = OrchestrationEngine()
        engine.register_agent(
            "planner", "Planner Agent", ["plan"],
            handler=lambda t: {"tasks": ["criar endpoint", "criar testes"]})
        engine.register_agent(
            "developer", "Developer Agent", ["implement"],
            handler=lambda t: {"code": "src/auth.py criado"})
        engine.register_agent(
            "tester", "Testing Agent", ["test"],
            handler=lambda t: {"tests": 14, "all_passed": True})
        engine.register_agent(
            "security", "Security Agent", ["security_review"],
            handler=lambda t: {"vulnerabilities": 0})
        engine.register_agent(
            "devops", "DevOps Agent", ["deploy"],
            handler=lambda t: {"url": "https://app.superdev.dev"})

        plan = engine.execute_goal("Nova solicitação: autenticação por token")
        assert plan.status == TaskStatus.COMPLETED
        assert engine.progress(plan.plan_id)["percent"] == 100.0
        assert engine.task_result(plan.plan_id, "t2")["code"] == "src/auth.py criado"
        assert engine.task_result(plan.plan_id, "t3")["tests"] == 14
        assert engine.task_result(plan.plan_id, "t5")["url"] == "https://app.superdev.dev"

    def test_dispatch_with_events(self) -> None:
        events = AutomationEvents()
        completed: list[str] = []
        monitor = OrchestrationMonitor()
        dispatcher = OrchestrationDispatcher(monitor, events)
        events.on(AutomationEventType.TASK_COMPLETED,
                  lambda d: completed.append(d["task_id"]))
        plan = OrchestrationPlanner().plan("meta")
        dispatcher.dispatch(plan, [
            OrchestrationAgent("planner", "Planner", ["plan"],
                               handler=lambda t: {}),
            OrchestrationAgent("developer", "Developer", ["implement"],
                               handler=lambda t: {}),
            OrchestrationAgent("tester", "Tester", ["test"],
                               handler=lambda t: {}),
            OrchestrationAgent("security", "Security", ["security_review"],
                               handler=lambda t: {}),
            OrchestrationAgent("devops", "DevOps", ["deploy"],
                               handler=lambda t: {}),
        ])
        assert plan.status == TaskStatus.COMPLETED
        assert completed == ["t1", "t2", "t3", "t4", "t5"]
