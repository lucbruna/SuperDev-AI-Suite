from __future__ import annotations

from typing import Any

from .planning_board import PlanningBoard
from .shared_context import SharedContext
from .shared_memory import SharedMemory


class CollaborationEngine:
    """Central collaboration orchestrator."""

    def __init__(self) -> None:
        self._shared_context = SharedContext()
        self._shared_memory = SharedMemory()
        self._planning_board = PlanningBoard()

    @property
    def shared_context(self) -> SharedContext:
        return self._shared_context

    @property
    def shared_memory(self) -> SharedMemory:
        return self._shared_memory

    @property
    def planning_board(self) -> PlanningBoard:
        return self._planning_board

    def get_status(self) -> dict[str, Any]:
        return {
            "context_keys": self._shared_context.key_count,
            "memory_keys": self._shared_memory.key_count,
            "board_items": self._planning_board.item_count,
        }
