"""Abstract interfaces for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class WorkspaceProvider(ABC):
    """Manages collaborative workspaces."""

    @abstractmethod
    def create(self, workspace: Any) -> dict[str, Any]:
        """Creates a workspace and returns its summary."""


class TeamProvider(ABC):
    """Manages teams and their structure."""

    @abstractmethod
    def create_team(self, team: Any) -> dict[str, Any]:
        """Creates a team and returns its summary."""


class ProjectProvider(ABC):
    """Manages collaborative projects."""

    @abstractmethod
    def create_project(self, project: Any) -> dict[str, Any]:
        """Creates a project and returns its summary."""


class TaskProvider(ABC):
    """Manages tasks and their lifecycle."""

    @abstractmethod
    def create_task(self, task: Any) -> dict[str, Any]:
        """Creates a task and returns its summary."""


class CommentHandler(ABC):
    """Handles comments and discussions."""

    @abstractmethod
    def add(self, comment: Any) -> dict[str, Any]:
        """Registers a comment and returns its summary."""


class Reviewer(ABC):
    """Reviews code, documents or processes."""

    @abstractmethod
    def review(self, target_id: str, author_id: str,
               **kwargs: Any) -> dict[str, Any]:
        """Runs a review over a target and returns findings."""


class ApprovalFlow(ABC):
    """Runs approval workflows."""

    @abstractmethod
    def start(self, approval: Any) -> dict[str, Any]:
        """Starts an approval flow."""

    @abstractmethod
    def decide(self, approval_id: str, approved: bool,
               decider: str, reason: str = "") -> dict[str, Any]:
        """Advances an approval with a decision."""


class MessageSink(ABC):
    """Delivers messages to channels."""

    @abstractmethod
    def send(self, message: Any) -> dict[str, Any]:
        """Sends a message and returns its summary."""


class KnowledgeSink(ABC):
    """Persists collaborative knowledge documents."""

    @abstractmethod
    def save(self, document: Any) -> dict[str, Any]:
        """Saves a document and returns its summary."""


class AgentCollaborator(ABC):
    """An AI agent that participates as a team member."""

    @abstractmethod
    def participate(self, task: Any) -> dict[str, Any]:
        """Executes a collaborative step and returns the outcome."""
