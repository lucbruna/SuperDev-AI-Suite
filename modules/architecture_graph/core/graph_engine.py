"""Graph engine: orchestrates scanning, parsing and graph construction.

Pipeline: filesystem scan -> per-file parsing -> file nodes -> dependency
edges -> semantic relations -> package/module aggregation nodes -> topology
assignment. The result is a fully wired :class:`ArchitectureGraph`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.architecture_graph.config.graph_config import GraphConfig
from modules.architecture_graph.core.dependency_engine import DependencyEngine
from modules.architecture_graph.core.relation_engine import apply_relations
from modules.architecture_graph.graph.edge_builder import contains, depends_on
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import (
    config_node,
    file_node,
    module_node,
    package_node,
)
from modules.architecture_graph.scanner import (
    docker_scanner,
    filesystem_scanner,
    javascript_scanner,
    json_scanner,
    python_scanner,
    typescript_scanner,
    workflow_scanner,
)
from modules.architecture_graph.scanner.plugin_scanner import scan as scan_plugins

_PY_PARSER = {"python": python_scanner}
_TS_PARSER = {"typescript": typescript_scanner, "javascript": javascript_scanner}
_JSON_PARSER = {"json": json_scanner}
_YAML_PARSER = {"yaml": docker_scanner, "docker": docker_scanner}

_SPECIAL_FILES = {
    "package.json": ("config", "package.json"),
    "pyproject.toml": ("config", "pyproject.toml"),
    "docker-compose.yml": ("config", "docker-compose.yml"),
    "docker-compose.yaml": ("config", "docker-compose.yaml"),
    "alembic.ini": ("config", "alembic.ini"),
}


class GraphEngine:
    """Builds an :class:`ArchitectureGraph` from a repository scan."""

    def __init__(self, config: GraphConfig) -> None:
        self.config = config
        self.parsed_files: dict[str, dict[str, Any]] = {}
        self.plugins: list[dict[str, Any]] = []
        self.workflows: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []

    # --------------------------------------------------------------- scanning
    def scan(self) -> list[filesystem_scanner.FileInfo]:
        return filesystem_scanner.scan_files(self.config)

    def parse(self, files: list[filesystem_scanner.FileInfo]) -> None:
        root = Path(self.config.project_root)
        for info in files:
            try:
                raw = (root / info.rel_path).read_text(
                    encoding="utf-8", errors="ignore"
                )
            except OSError:
                continue
            parser = self._parser_for(info.rel_path, info.language)
            if parser is None:
                continue
            try:
                self.parsed_files[info.rel_path] = parser.scan(raw, info.rel_path)
            except Exception as exc:  # defensive: never kill the build
                self.errors.append(
                    {"path": info.rel_path, "error": f"{type(exc).__name__}: {exc}"}
                )

    def _parser_for(self, rel_path: str, language: str) -> Any:
        name = rel_path.rsplit("/", 1)[-1]
        if name in _SPECIAL_FILES:
            kind, _ = _SPECIAL_FILES[name]
            return _JSON_PARSER.get("json") if kind == "config" and name.endswith(".json") else _YAML_PARSER.get("yaml")
        if language in _PY_PARSER:
            return _PY_PARSER[language]
        if language in _TS_PARSER:
            return _TS_PARSER[language]
        if language in _JSON_PARSER:
            return _JSON_PARSER[language]
        if language in _YAML_PARSER:
            return _YAML_PARSER[language]
        if language == "markdown":
            from modules.architecture_graph.scanner import markdown_scanner

            return markdown_scanner
        return None

    # ------------------------------------------------------------- building
    def build(self) -> ArchitectureGraph:
        files = self.scan()
        self.parse(files)
        graph = ArchitectureGraph(
            name=self.config.name, project_root=self.config.project_root
        )

        known = {info.rel_path for info in files}
        dep_engine = DependencyEngine(self.config.project_root, known)

        # 1) File + package + module nodes.
        for info in files:
            graph.add_node(
                file_node(info.rel_path, language=info.language, size=info.size)
            )
            self._add_package_nodes(graph, info.rel_path)
            self._add_module_nodes(graph, info.rel_path)

        # 2) Config nodes for special files.
        for rel_path in self.parsed_files:
            name = rel_path.rsplit("/", 1)[-1]
            if name in _SPECIAL_FILES:
                _, canonical = _SPECIAL_FILES[name]
                cid = f"config:{canonical}"
                if not graph.has_node(cid):
                    graph.add_node(config_node(canonical, rel_path))
                graph.add_edge(contains(cid, f"file:{rel_path}"))

        # 3) Dependency edges (imports).
        dep_engine.add_dependencies_for_batch(graph, self.parsed_files)

        # 4) Semantic relations + platform entity discovery.
        self.plugins = scan_plugins(self.config.project_root)
        self.workflows = workflow_scanner.scan(self.config.project_root)
        apply_relations(graph, self.parsed_files, plugins=self.plugins, workflows=self.workflows)

        # 5) Package/module dependency aggregation.
        self._aggregate_relations(graph)

        # 6) Topology layers.
        from modules.architecture_graph.core.topology_engine import assign_layers

        assign_layers(graph)
        return graph

    # -------------------------------------------------------------- helpers
    def _add_package_nodes(self, graph: ArchitectureGraph, rel_path: str) -> None:
        parts = rel_path.split("/")
        if len(parts) < 2:
            return
        pkg_id = f"package:{parts[0]}"
        if not graph.has_node(pkg_id):
            graph.add_node(package_node(parts[0], parts[0] + "/"))
        graph.add_edge(contains(pkg_id, f"file:{rel_path}"))

    def _add_module_nodes(self, graph: ArchitectureGraph, rel_path: str) -> None:
        parts = rel_path.split("/")
        if len(parts) >= 3 and parts[0] == "modules":
            mod_id = f"module:{parts[1]}"
            if not graph.has_node(mod_id):
                graph.add_node(module_node(parts[1], f"modules/{parts[1]}/"))
            graph.add_edge(contains(mod_id, f"file:{rel_path}"))

    def _aggregate_relations(self, graph: ArchitectureGraph) -> None:
        """Module/package level edges derived from file-level edges."""
        parent: dict[str, str] = {}
        for node in graph.nodes():
            if node.kind == "file":
                parts = (node.path or node.name).split("/")
                parent[node.id] = f"package:{parts[0]}" if parts else node.id
            elif node.kind == "module":
                parent[node.id] = node.id
            elif node.kind == "package":
                parent[node.id] = node.id

        for edge in graph.edges():
            if edge.kind not in {"imports", "uses", "calls", "depends_on"}:
                continue
            src = parent.get(edge.source)
            dst = parent.get(edge.target)
            if src and dst and src != dst:
                graph.add_edge(depends_on(src, dst))
