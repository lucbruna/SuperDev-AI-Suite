from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Generator

from .database_tool import DatabaseTool


class Transaction:
    """Manage database transactions."""

    def __init__(self, adapter: DatabaseTool):
        self._adapter = adapter
        self._depth = 0

    def begin(self) -> None:
        self._adapter.execute("BEGIN")
        self._depth += 1

    def commit(self) -> None:
        if self._depth > 0:
            self._adapter.execute("COMMIT")
            self._depth -= 1

    def rollback(self) -> None:
        if self._depth > 0:
            self._adapter.execute("ROLLBACK")
            self._depth -= 1

    def savepoint(self, name: str) -> None:
        self._adapter.execute(f"SAVEPOINT {name}")

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        self.begin()
        try:
            yield
            self.commit()
        except Exception:
            self.rollback()
            raise
