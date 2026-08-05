"""SQLite persistence backend for the Architecture Graph (default).

Uses the stdlib ``sqlite3`` module. A fresh connection is opened per
operation so the backend is safe to use from FastAPI's thread pool and from
background scheduler tasks. The graph is stored in two tables and replaced
atomically inside a transaction on save.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    GraphEdge,
    GraphNode,
)
from modules.architecture_graph.storage.base import GraphStorage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS graph_meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT '',
    path TEXT NOT NULL DEFAULT '',
    size INTEGER NOT NULL DEFAULT 0,
    layer TEXT NOT NULL DEFAULT '',
    meta TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    kind TEXT NOT NULL,
    meta TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (source, target, kind)
);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target);
"""


class SQLiteGraphStorage(GraphStorage):
    backend_name = "sqlite"

    def __init__(self, db_path: str) -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    # -------------------------------------------------------------- GraphStorage
    def save(self, graph: ArchitectureGraph) -> None:
        data = graph.to_dict()
        with self._connect() as conn:
            conn.execute("DELETE FROM nodes")
            conn.execute("DELETE FROM edges")
            conn.execute("DELETE FROM graph_meta")
            conn.executemany(
                "INSERT OR REPLACE INTO nodes "
                "(id, name, kind, language, path, size, layer, meta) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    (
                        n["id"],
                        n["name"],
                        n["kind"],
                        n["language"],
                        n["path"],
                        n["size"],
                        n["layer"],
                        json.dumps(n.get("meta") or {}, ensure_ascii=False),
                    )
                    for n in data["nodes"]
                ],
            )
            conn.executemany(
                "INSERT OR REPLACE INTO edges (source, target, kind, meta) "
                "VALUES (?, ?, ?, ?)",
                [
                    (
                        e["source"],
                        e["target"],
                        e["kind"],
                        json.dumps(e.get("meta") or {}, ensure_ascii=False),
                    )
                    for e in data["edges"]
                ],
            )
            conn.executemany(
                "INSERT OR REPLACE INTO graph_meta (key, value) VALUES (?, ?)",
                [
                    ("name", data["name"]),
                    ("project_root", data["project_root"]),
                    ("built_at", data["built_at"]),
                    ("version", str(data["version"])),
                ],
            )

    def load(self) -> ArchitectureGraph | None:
        with self._connect() as conn:
            meta = dict(conn.execute("SELECT key, value FROM graph_meta"))
            nodes = conn.execute("SELECT * FROM nodes").fetchall()
            edges = conn.execute("SELECT * FROM edges").fetchall()
        if not nodes:
            return None
        graph = ArchitectureGraph(
            name=meta.get("name", "superdev"),
            project_root=meta.get("project_root", ""),
        )
        graph.built_at = meta.get("built_at", "")
        try:
            graph.version = int(meta.get("version", "1"))
        except ValueError:
            graph.version = 1
        for row in nodes:
            graph._nodes[row["id"]] = GraphNode(
                id=row["id"],
                name=row["name"],
                kind=row["kind"],
                language=row["language"],
                path=row["path"],
                size=row["size"],
                layer=row["layer"],
                meta=json.loads(row["meta"] or "{}"),
            )
        for row in edges:
            graph._edges.append(
                GraphEdge(
                    source=row["source"],
                    target=row["target"],
                    kind=row["kind"],
                    meta=json.loads(row["meta"] or "{}"),
                )
            )
        for node_id in graph._nodes:
            graph._out[node_id] = {
                e.target for e in graph._edges if e.source == node_id
            }
            graph._in[node_id] = {
                e.source for e in graph._edges if e.target == node_id
            }
        return graph

    def exists(self) -> bool:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS c FROM nodes").fetchone()
        return bool(row and row["c"] > 0)

    def clear(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM nodes")
            conn.execute("DELETE FROM edges")
            conn.execute("DELETE FROM graph_meta")


class MemoryGraphStorage(GraphStorage):
    """In-process storage used when no persistent backend is available."""

    backend_name = "memory"

    def __init__(self) -> None:
        self._graph: ArchitectureGraph | None = None

    def save(self, graph: ArchitectureGraph) -> None:
        self._graph = graph

    def load(self) -> ArchitectureGraph | None:
        return self._graph

    def exists(self) -> bool:
        return self._graph is not None

    def clear(self) -> None:
        self._graph = None
