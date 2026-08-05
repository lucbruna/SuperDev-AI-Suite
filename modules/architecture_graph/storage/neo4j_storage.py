"""Neo4j persistence backend for the Architecture Graph.

Best-effort adapter: requires the ``neo4j`` Python driver and a reachable
server (SUPERDEV_GRAPH_NEO4J_URI / _USER / _PASSWORD). Missing driver or
unreachable server raises a descriptive error at construction time so the
caller can fall back to SQLite.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    GraphEdge,
    GraphNode,
)
from modules.architecture_graph.storage.base import GraphStorage


class Neo4jGraphStorage(GraphStorage):
    backend_name = "neo4j"

    def __init__(self, uri: str = "", user: str = "", password: str = "") -> None:
        if not uri:
            from modules.architecture_graph.config.graph_settings import get_settings

            cfg = get_settings().config
            uri, user, password = cfg.neo4j_uri, cfg.neo4j_user, cfg.neo4j_password
        if not uri:
            raise ValueError("Neo4jGraphStorage requires SUPERDEV_GRAPH_NEO4J_URI")
        self.uri, self.user, self.password = uri, user or "neo4j", password or ""
        self._driver = self._make_driver()

    @staticmethod
    def _make_driver() -> Any:
        try:
            from neo4j import GraphDatabase  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "the 'neo4j' driver is required for the neo4j backend "
                "(pip install neo4j)"
            ) from exc
        return GraphDatabase.driver

    # -------------------------------------------------------------- GraphStorage
    def save(self, graph: ArchitectureGraph) -> None:
        data = graph.to_dict()
        with self._driver(
            self.uri, auth=(self.user, self.password)
        ) as driver:
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                session.run(
                    "CREATE (g:Graph {name: $name, project_root: $root, built_at: $at})",
                    name=data["name"], root=data["project_root"], at=data["built_at"],
                )
                for n in data["nodes"]:
                    session.run(
                        "CREATE (n:Node {id: $id, name: $name, kind: $kind, "
                        "language: $lang, path: $path, size: $size, layer: $layer, "
                        "meta: $meta})",
                        id=n["id"], name=n["name"], kind=n["kind"], lang=n["language"],
                        path=n["path"], size=n["size"], layer=n["layer"],
                        meta=str(n.get("meta") or {}),
                    )
                for e in data["edges"]:
                    session.run(
                        "MATCH (a:Node {id: $src}), (b:Node {id: $dst}) "
                        "CREATE (a)-[r:EDGE {kind: $kind, meta: $meta}]->(b)",
                        src=e["source"], dst=e["target"], kind=e["kind"],
                        meta=str(e.get("meta") or {}),
                    )

    def load(self) -> ArchitectureGraph | None:
        with self._driver(self.uri, auth=(self.user, self.password)) as driver:
            with driver.session() as session:
                graph_info = session.run("MATCH (g:Graph) RETURN g").single()
                nodes = session.run("MATCH (n:Node) RETURN n").data()
                rels = session.run(
                    "MATCH (a:Node)-[r:EDGE]->(b:Node) "
                    "RETURN a.id AS src, b.id AS dst, r.kind AS kind, r.meta AS meta"
                ).data()
        if not nodes:
            return None
        name = "superdev"
        root = ""
        built_at = ""
        if graph_info is not None:
            g = graph_info["g"]
            name = g.get("name", name)
            root = g.get("project_root", root)
            built_at = g.get("built_at", built_at)
        graph = ArchitectureGraph(name=name, project_root=root)
        graph.built_at = built_at
        for n in nodes:
            props = n["n"]
            graph._nodes[props["id"]] = GraphNode(
                id=props["id"], name=props.get("name", ""), kind=props.get("kind", "file"),
                language=props.get("language", ""), path=props.get("path", ""),
                size=int(props.get("size", 0) or 0), layer=props.get("layer", ""),
            )
        for r in rels:
            graph._edges.append(
                GraphEdge(source=r["src"], target=r["dst"], kind=r.get("kind", "depends_on"))
            )
        for node_id in graph._nodes:
            graph._out[node_id] = {e.target for e in graph._edges if e.source == node_id}
            graph._in[node_id] = {e.source for e in graph._edges if e.target == node_id}
        return graph

    def exists(self) -> bool:
        with self._driver(self.uri, auth=(self.user, self.password)) as driver:
            with driver.session() as session:
                row = session.run("MATCH (n:Node) RETURN count(n) AS c").single()
        return bool(row and row["c"] > 0)

    def clear(self) -> None:
        with self._driver(self.uri, auth=(self.user, self.password)) as driver:
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
