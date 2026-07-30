from __future__ import annotations

import logging
import uuid
from typing import Any


class Board:
    """Represents a project board (Kanban-style)."""

    def __init__(self, name: str, project_id: str) -> None:
        self.id = str(uuid.uuid4())
        self.name = name
        self.project_id = project_id
        self.columns: list[str] = ["todo", "in_progress", "done"]
        self.cards: list[dict[str, Any]] = []


class BoardManager:
    """Manages project boards."""

    def __init__(self) -> None:
        self._boards: dict[str, Board] = {}
        self._log = logging.getLogger("superdev.project.boards")

    def create(self, name: str, project_id: str) -> Board:
        board = Board(name=name, project_id=project_id)
        self._boards[board.id] = board
        self._log.info("Created board %s", board.id)
        return board

    def get(self, board_id: str) -> Board | None:
        return self._boards.get(board_id)

    def add_card(self, board_id: str, card: dict[str, Any]) -> None:
        board = self._boards.get(board_id)
        if board:
            board.cards.append(card)
