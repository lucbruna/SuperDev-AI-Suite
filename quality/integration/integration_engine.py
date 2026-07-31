from __future__ import annotations

from typing import Any

from ..quality_models import TestCase, TestKind, TestSuite


class IntegrationEngine:
    """Integration testing — API, database, service, workflow, agent, deployment."""

    CATEGORIES = ["api", "database", "service", "workflow", "agent", "deployment"]

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.integration
        self._suites: dict[str, TestSuite] = {}
        self._connectors: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def create_suite(self, name: str, category: str = "api", target: str = "") -> TestSuite:
        if category not in self.CATEGORIES:
            raise ValueError(f"Unknown integration category: {category}")
        suite = TestSuite(name=name, kind=TestKind.INTEGRATION, target=target)
        suite.metadata = {"category": category}
        self._suites[suite.suite_id] = suite
        self.engine.registry.register_suite(suite)
        return suite

    def add_api_test(self, suite_id: str, endpoint: str, expected_status: int = 200) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(TestCase(
            name=f"api_{endpoint.replace('/', '_')}",
            kind=TestKind.INTEGRATION,
            source=endpoint,
            assertions=[f"status == {expected_status}"],
        ))
        return True

    def add_database_test(self, suite_id: str, query: str, expected_rows: int = 1) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(TestCase(
            name=f"db_{query.split()[0].lower() if query else 'query'}",
            kind=TestKind.INTEGRATION,
            source=query,
            assertions=[f"rows == {expected_rows}"],
        ))
        return True

    def add_workflow_test(self, suite_id: str, workflow: str, expected_steps: int = 1) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(TestCase(
            name=f"wf_{workflow}",
            kind=TestKind.INTEGRATION,
            source=workflow,
            assertions=[f"steps == {expected_steps}"],
        ))
        return True

    def add_agent_test(self, suite_id: str, agent: str, expected_status: str = "completed") -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(TestCase(
            name=f"agent_{agent}",
            kind=TestKind.INTEGRATION,
            source=agent,
            assertions=[f"status == '{expected_status}'"],
        ))
        return True

    def add_deployment_test(self, suite_id: str, environment: str, expected_healthy: bool = True) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(TestCase(
            name=f"deploy_{environment}",
            kind=TestKind.INTEGRATION,
            source=environment,
            assertions=[f"healthy == {expected_healthy}"],
        ))
        return True

    # -- connectors ----------------------------------------------------------

    def register_connector(self, name: str, connector: Any) -> None:
        self._connectors[name] = connector

    def get_connector(self, name: str) -> Any:
        return self._connectors.get(name)

    def list_suites(self) -> list[TestSuite]:
        return list(self._suites.values())

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "suites": len(self._suites),
            "connectors": len(self._connectors),
        }


__all__ = ["IntegrationEngine"]
