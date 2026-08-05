"""Graph transformations: pruning, external collapsing, package-level views.

These helpers reduce a full file-level graph into shapes that are easier to
reason about (module graphs, layer graphs) or cheaper to ship to the
frontend (pruned / capped graphs).
"""
from __future__ import annotations

from typing import Iterable

from modules.architecture_graph.graph.edge_builder import contains, depends_on
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import package_node


def prune(
    graph: ArchitectureGraph,
    *,
    max_nodes: int = 0,
    keep_kinds: Iterable[str] | None = None,
    drop_kinds: Iterable[str] | None = None,
) -> ArchitectureGraph:
    """Return a copy limited by node count and/or node kinds."""
    keep = set(keep_kinds) if keep_kinds is not None else None
    drop = set(drop_kinds) if drop_kinds is not None else set()

    selected: list[str] = []
    for node in graph.nodes():
        if drop and node.kind in drop:
            continue
        if keep is not None and node.kind not in keep:
            continue
        selected.append(node.id)
        if max_nodes and len(selected) >= max_nodes:
            break
    return graph.subgraph(selected)


def collapse_externals(graph: ArchitectureGraph) -> ArchitectureGraph:
    """Merge external dependency nodes into their top-level package.

    ``external:fastapi`` and ``external:fastapi.security`` collapse into a
    single ``external:fastapi`` node; edges are rewired to the survivor.
    """
    merged = ArchitectureGraph(name=graph.name, project_root=graph.project_root)
    external_by_top: dict[str, str] = {}
    for node in graph.nodes():
        if node.kind != "external":
            merged.upsert_node(node)
            continue
        top = node.name.split(".")[0]
        survivor = f"external:{top}"
        external_by_top.setdefault(node.id, survivor)

    # Create the collapsed external nodes.
    for target in set(external_by_top.values()):
        merged.upsert_node(package_node(target.split(":", 1)[1], ""))

    for edge in graph.edges():
        src = external_by_top.get(edge.source, edge.source)
        dst = external_by_top.get(edge.target, edge.target)
        merged.add_edge(depends_on(src, dst, {"kind": edge.kind}))

    for edge in graph.edges():
        src = external_by_top.get(edge.source, edge.source)
        dst = external_by_top.get(edge.target, edge.target)
        if src != edge.source or dst != edge.target:
            continue
        merged.add_edge(edge)
    return merged


def package_level_graph(graph: ArchitectureGraph) -> ArchitectureGraph:
    """Aggregate the file graph to package/module level.

    For every file node we compute its top-level directory (or module dir)
    and rewire ``imports``/``depends_on`` edges at that granularity. Existing
    package/module nodes are preserved.
    """
    parent: dict[str, str] = {}
    for node in graph.nodes():
        if node.kind == "file":
            rel = (node.path or node.name).replace("\\", "/")
            parts = rel.split("/")
            top = parts[0] if len(parts) > 1 else rel
            parent[node.id] = f"package:{top}"
        elif node.kind in {"module", "package"}:
            parent[node.id] = node.id

    pg = ArchitectureGraph(name=f"{graph.name}:packages", project_root=graph.project_root)
    for node in graph.nodes():
        if node.kind in {"module", "package"}:
            pg.upsert_node(node)
    for file_id, pkg_id in parent.items():
        if pkg_id.startswith("package:"):
            name = pkg_id.split(":", 1)[1]
            if not pg.has_node(pkg_id):
                pg.add_node(package_node(name, ""))
            pg.add_edge(contains(pkg_id, file_id))

    for edge in graph.edges():
        if edge.kind not in {"imports", "depends_on", "uses", "calls"}:
            continue
        src = parent.get(edge.source)
        dst = parent.get(edge.target)
        if src and dst and src != dst:
            pg.add_edge(depends_on(src, dst, {"source": edge.source, "target": edge.target}))
    return pg


def layer_graph(graph: ArchitectureGraph) -> ArchitectureGraph:
    """Aggregate to layer-level dependency edges (frontend->backend->...)."""
    layer_by_id: dict[str, str] = {}
    for node in graph.nodes():
        layer = node.layer or "unknown"
        layer_by_id[node.id] = f"layer:{layer}"

    lg = ArchitectureGraph(name=f"{graph.name}:layers", project_root=graph.project_root)
    for node in graph.nodes():
        lid = layer_by_id[node.id]
        if not lg.has_node(lid):
            lg.add_node(
                package_node(lid.split(":", 1)[1], "").__class__(
                    id=lid,
                    name=lid.split(":", 1)[1],
                    kind="package",
                    layer=node.layer,
                )
            )
    for edge in graph.edges():
        src = layer_by_id.get(edge.source)
        dst = layer_by_id.get(edge.target)
        if src and dst and src != dst:
            lg.add_edge(depends_on(src, dst))
    return lg
