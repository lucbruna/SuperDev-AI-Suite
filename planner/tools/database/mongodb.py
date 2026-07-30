from __future__ import annotations

from typing import Any


class MongoDB:
    """MongoDB database adapter."""

    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        self.connection_string = connection_string
        self._client: Any = None
        self._db: Any = None

    def connect(self, database: str = "default") -> None:
        # In production: pymongo.MongoClient(self.connection_string)
        self._db_name = database

    def disconnect(self) -> None:
        self._client = None
        self._db = None

    def find(self, collection: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return []

    def insert_one(self, collection: str, document: dict[str, Any]) -> str:
        return "mock_id"

    def insert_many(self, collection: str, documents: list[dict[str, Any]]) -> list[str]:
        return ["mock_id"] * len(documents)

    def update_one(self, collection: str, query: dict[str, Any], update: dict[str, Any]) -> int:
        return 1

    def delete_one(self, collection: str, query: dict[str, Any]) -> int:
        return 1

    def aggregate(self, collection: str, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []
