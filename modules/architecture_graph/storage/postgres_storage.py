"""PostgreSQL persistence backend for the Architecture Graph.

Activates only when the user configures ``SUPERDEV_GRAPH_POSTGRES_URL`` and
selects ``storage_backend=postgres``. Uses SQLAlchemy (a core dependency of
the platform backend) with a synchronous engine; the schema mirrors the
SQLite backend so switching backends is transparent.
"""
from __future__ import annotations

import json
from typing import Any

from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    GraphEdge,
    GraphNode,
)
from modules.architecture_graph.storage.base import GraphStorage

_TABLES = """
CREATE TABLE IF NOT EXISTS graph_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, kind TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT '', path TEXT NOT NULL DEFAULT '',
    size INTEGER NOT NULL DEFAULT 0, layer TEXT NOT NULL DEFAULT '',
    meta TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS edges (
    source TEXT NOT NULL, target TEXT NOT NULL, kind TEXT NOT NULL,
    meta TEXT NOT NULL DEFAULT '{}', PRIMARY KEY (source, target, kind)
);
"""


class PostgresGraphStorage(GraphStorage):
    backend_name = "postgres"

    def __init__(self, url: str = "") -> None:
        if not url:
            from modules.architecture_graph.config.graph_settings import get_settings

            url = get_settings().config.postgres_url
        if not url:
            raise ValueError(
                "PostgresGraphStorage requires SUPERDEV_GRAPH_POSTGRES_URL"
            )
        self.url = url
        self._engine = self._make_engine(url)

    @staticmethod
    def _make_engine(url: str) -> Any:
        try:
            from sqlalchemy import create_engine
        except ImportError as exc:  # pragma: no cover
            raise ImportError("sqlalchemy is required for the postgres backend") from exc
        return create_engine(url, pool_pre_ping=True)

    def _init_schema(self) -> None:
        with self._engine.begin() as conn:
            conn.exec_driver_sql(_TABLES)

    # -------------------------------------------------------------- GraphStorage
    def save(self, graph: ArchitectureGraph) -> None:
        data = graph.to_dict()
        with self._engine.begin() as conn:
            conn.exec_driver_sql("DELETE FROM nodes")
            conn.exec_driver_sql("DELETE FROM edges")
            conn.exec_driver_sql("DELETE FROM graph_meta")
            conn.exec_driver_sql(
                "INSERT INTO graph_meta (key, value) VALUES (%s, %s)",
                [("name", data["name"]), ("project_root", data["project_root"]),
                 ("built_at", data["built_at"]), ("version", str(data["version"]))],
            )
            conn.exec_driver_sql(
                "INSERT INTO nodes (id, name, kind, language, path, size, layer, meta) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                [
                    (n["id"], n["name"], n["kind"], n["language"], n["path"],
                     n["size"], n["layer"], json.dumps(n.get("meta") or {}))
                    for n in data["nodes"]
                ],
            )
            conn.exec_driver_sql(
                "INSERT INTO edges (source, target, kind, meta) VALUES (%s, %s, %s, %s)",
                [
                    (e["source"], e["target"], e["kind"],
                     json.dumps(e.get("meta") or {}))
                    for e in data["edges"]
                ],
            )

    def load(self) -> ArchitectureGraph | None:
        with self._engine.connect() as conn:
            meta = dict(conn.exec_driver_sql("SELECT key, value FROM graph_meta").all())
            rows = conn.exec_driver_sql(
                "SELECT * FROM nodes"
            ).mappings().all()
            edge_rows = conn.exec_driver_sql(
                "SELECT * FROM edges"
            ).mappings().all()
        if not rows:
            return None
        graph = ArchitectureGraph(
            name=meta.get("name", "superdev"),
            project_root=meta.get("project_root", ""),
        )
        graph.built_at = meta.get("built_at", "")
        for row in rows:
            graph._nodes[row["id"]] = GraphNode(
                id=row["id"], name=row["name"], kind=row["kind"],
                language=row["language"], path=row["path"], size=row["size"],
                layer=row["layer"], meta=json.loads(row["meta"] or "{}"),
            )
        for row in edge_rows:
            graph._edges.append(
                GraphEdge(
                    source=row["source"], target=row["target"], kind=row["kind"],
                    meta=json.loads(row["meta"] or "{}"),
                )
            )
        for node_id in graph._nodes:
            graph._out[node_id] = {e.target for e in graph._edges if e.source == node_id}
            graph._in[node_id] = {e.source for e in graph._edges if e.target == node_id}
        return graph

    def exists(self) -> bool:
        with self._engine.connect() as conn:
            row = conn.exec_driver_sql("SELECT COUNT(*) AS c FROM nodes").one()
        return bool(row and row[0] > 0)

    def clear(self) -> None:
        with self._engine.begin() as conn:
            conn.exec_driver_sql("DELETE FROM nodes")
            conn.exec_driver_sql("DELETE FROM edges")
            conn.exec_driver_sql("DELETE FROM graph_meta")
