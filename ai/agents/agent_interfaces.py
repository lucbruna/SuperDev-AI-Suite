from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class AgentInterface(ABC):
    """Abstract interface all agents implement."""

    @abstractmethod
    def get_id(self) -> str: ...

    @abstractmethod
    def get_type(self) -> str: ...

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]: ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]: ...


class AgentStorageInterface(ABC):
    """Interface for agent storage backends."""

    @abstractmethod
    def save(self, agent_id: str, data: Dict[str, Any]) -> None: ...

    @abstractmethod
    def load(self, agent_id: str) -> Dict[str, Any] | None: ...

    @abstractmethod
    def delete(self, agent_id: str) -> bool: ...


class AgentCommunicationInterface(ABC):
    """Interface for agent communication."""

    @abstractmethod
    def send(self, sender: str, recipient: str, message: Dict[str, Any]) -> bool: ...

    @abstractmethod
    def receive(self, agent_id: str) -> List[Dict[str, Any]]: ...


class AgentCoordinationInterface(ABC):
    """Interface for agent coordination."""

    @abstractmethod
    def assign_task(self, agent_id: str, task: Dict[str, Any]) -> bool: ...

    @abstractmethod
    def get_status(self, agent_id: str) -> str: ...
