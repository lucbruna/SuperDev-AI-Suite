"""Abstract interfaces for the automation engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ActionExecutor(ABC):
    """Executes a single automation action."""

    @abstractmethod
    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """Executes the action and returns a result dict."""


class Trigger(ABC):
    """A trigger that can fire workflow executions."""

    @abstractmethod
    def evaluate(self, event: dict[str, Any] | None = None) -> bool:
        """Returns True when the trigger condition is met."""


class WorkflowRunner(ABC):
    """Runs workflows end-to-end."""

    @abstractmethod
    def run(self, workflow_id: str, payload: dict[str, Any] | None = None) -> Any:
        """Runs a workflow and returns its execution result."""


class Rule(ABC):
    """A decision rule with a condition and a consequence."""

    @abstractmethod
    def matches(self, fact: dict[str, Any]) -> bool:
        """True when the rule condition matches the given facts."""

    @abstractmethod
    def apply(self, fact: dict[str, Any]) -> Any:
        """Applies the rule consequence."""


class Scheduler(ABC):
    """Schedules and dispatches recurring executions."""

    @abstractmethod
    def run_due(self) -> list[str]:
        """Runs all due scheduled jobs, returning fired schedule ids."""


class Monitor(ABC):
    """Tracks and reports on automation executions."""

    @abstractmethod
    def report(self) -> dict[str, Any]:
        """Returns a monitoring report snapshot."""
