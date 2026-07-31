"""Interfaces for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agent_orchestration.orchestrator_models import (AgentMessage, AgentProfile,
                                                     AgentTask,
                                                     EvaluationReport, Lesson)


class PlannerStrategy(ABC):
    @abstractmethod
    def plan(self, request: str) -> list[AgentTask]: ...


class TaskExecutor(ABC):
    @abstractmethod
    def execute(self, task: AgentTask) -> dict[str, Any]: ...


class CommunicationBus(ABC):
    @abstractmethod
    def send(self, message: AgentMessage) -> bool: ...


class AgentMemoryStore(ABC):
    @abstractmethod
    def remember(self, agent_id: str, content: str) -> bool: ...


class DecisionEngine(ABC):
    @abstractmethod
    def decide(self, task: AgentTask) -> dict[str, Any]: ...


class Evaluator(ABC):
    @abstractmethod
    def evaluate(self, agent: AgentProfile) -> EvaluationReport: ...


class TaskScheduler(ABC):
    @abstractmethod
    def enqueue(self, task: AgentTask) -> bool: ...


class LearningStore(ABC):
    @abstractmethod
    def record(self, lesson: Lesson) -> bool: ...
