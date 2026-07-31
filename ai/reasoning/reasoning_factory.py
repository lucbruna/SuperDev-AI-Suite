from __future__ import annotations

from .reasoning_engine import ReasoningEngine
from .reasoning_manager import ReasoningManager
from .reasoning_memory import ReasoningMemory
from .reasoning_service import ReasoningService


class ReasoningFactory:
    """Factory for creating reasoning engine instances."""

    @staticmethod
    def create_default_engine() -> ReasoningEngine:
        return ReasoningEngine(memory=ReasoningMemory())

    @staticmethod
    def create_default_manager() -> ReasoningManager:
        return ReasoningManager(engine=ReasoningFactory.create_default_engine())

    @staticmethod
    def create_default_service() -> ReasoningService:
        return ReasoningService(engine=ReasoningFactory.create_default_engine())

    @staticmethod
    def create_with_memory(memory: ReasoningMemory) -> ReasoningEngine:
        return ReasoningEngine(memory=memory)
