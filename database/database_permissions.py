from __future__ import annotations

import re
from enum import Enum
from typing import Any

from .database_logger import DatabaseLogger
from .database_models import QueryResult


class DatabaseAction(str, Enum):
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    EXECUTE = "execute"
    ALL = "*"


class DatabasePermissions:
    """Per-query permission and scope checking for database operations."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._permissions: dict[str, set[str]] = {}
        self._table_grants: dict[str, dict[str, set[str]]] = {}
        self._logger = logger or DatabaseLogger("database.permissions")

    def grant(self, role: str, action: DatabaseAction | str, table: str | None = None) -> None:
        action_str = action.value if isinstance(action, DatabaseAction) else action
        if table:
            self._table_grants.setdefault(role, {}).setdefault(table, set()).add(action_str)
        else:
            self._permissions.setdefault(role, set()).add(action_str)
        self._logger.info(f"Granted {action_str} on {table or '*' } to '{role}'")

    def revoke(self, role: str, action: DatabaseAction | str, table: str | None = None) -> None:
        action_str = action.value if isinstance(action, DatabaseAction) else action
        if table:
            grants = self._table_grants.get(role, {}).get(table, set())
            grants.discard(action_str)
        else:
            perms = self._permissions.get(role, set())
            perms.discard(action_str)

    def check(self, role: str, action: DatabaseAction | str, table: str | None = None) -> bool:
        action_str = action.value if isinstance(action, DatabaseAction) else action
        if role in self._permissions:
            if "*" in self._permissions[role]:
                return True
            if action_str in self._permissions[role]:
                return True
        if table and role in self._table_grants:
            table_perms = self._table_grants[role].get(table, set())
            if "*" in table_perms or action_str in table_perms:
                return True
        return False

    def check_query(self, role: str, query: str) -> bool:
        action = self._infer_action(query)
        table = self._infer_table(query)
        if not action:
            return True
        return self.check(role, action, table)

    def _infer_action(self, query: str) -> str | None:
        normalized = query.strip().upper()
        for action in ("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "EXECUTE"):
            if normalized.startswith(action):
                return action.lower()
        return None

    def _infer_table(self, query: str) -> str | None:
        patterns = [
            r"(?:FROM|INTO|UPDATE|TABLE|FROM)\s+`?(\w+)`?",
            r"(?:FROM|INTO|UPDATE|TABLE|FROM)\s+(?:`?\w+`?\.)?`?(\w+)`?",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def list_roles(self) -> list[str]:
        return list(set(list(self._permissions.keys()) + list(self._table_grants.keys())))
