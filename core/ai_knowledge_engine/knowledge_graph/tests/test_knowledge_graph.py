from __future__ import annotations

import pytest

from core.ai_knowledge_engine.knowledge_graph.graph_engine import GraphEngine, EngineConfig, EngineState
from core.ai_knowledge_engine.knowledge_graph.entity_manager import EntityManager
from core.ai_knowledge_engine.knowledge_graph.relationship_builder import RelationshipBuilder, RelationshipType
from core.ai_knowledge_engine.knowledge_graph.knowledge_mapper import KnowledgeMapper


@pytest.fixture
def entity_manager() -> EntityManager:
    return EntityManager()


@pytest.fixture
def relationship_builder() -> RelationshipBuilder:
    return RelationshipBuilder()


@pytest.fixture
def knowledge_mapper() -> KnowledgeMapper:
    return KnowledgeMapper()


@pytest.fixture
async def engine() -> GraphEngine:
    eng = GraphEngine()
    await eng.initialize()
    yield eng
    await eng.stop()


@pytest.mark.asyncio
async def test_engine_initialize_and_stop(engine: GraphEngine) -> None:
    assert engine.state == EngineState.READY


@pytest.mark.asyncio
async def test_add_node(engine: GraphEngine) -> None:
    node = await engine.add_node("n1", "Person", {"name": "Alice"})
    assert node.id == "n1"
    assert node.label == "Person"
    assert node.properties == {"name": "Alice"}


@pytest.mark.asyncio
async def test_add_edge(engine: GraphEngine) -> None:
    await engine.add_node("n1", "Service", {})
    await engine.add_node("n2", "Database", {})
    edge = await engine.add_edge("n1", "n2", RelationshipType.DEPENDS_ON)
    assert edge.source_id == "n1"
    assert edge.target_id == "n2"
    assert edge.relationship_type == RelationshipType.DEPENDS_ON


@pytest.mark.asyncio
async def test_add_edge_missing_node(engine: GraphEngine) -> None:
    await engine.add_node("existing", "Node", {})
    with pytest.raises(ValueError, match="Node not found"):
        await engine.add_edge("existing", "missing", RelationshipType.RELATES_TO)


@pytest.mark.asyncio
async def test_query(engine: GraphEngine) -> None:
    await engine.add_node("a", "A", {})
    await engine.add_node("b", "B", {})
    await engine.add_node("c", "C", {})
    await engine.add_edge("a", "b", RelationshipType.CONTAINS)
    await engine.add_edge("b", "c", RelationshipType.CONTAINS)

    result = await engine.query("a", depth=2)
    assert result["node"]["id"] == "a"
    assert len(result["neighbors"]) == 2


@pytest.mark.asyncio
async def test_traverse(engine: GraphEngine) -> None:
    await engine.add_node("root", "Root", {})
    await engine.add_node("child1", "Child", {})
    await engine.add_node("child2", "Child", {})
    await engine.add_edge("root", "child1", RelationshipType.CONTAINS)
    await engine.add_edge("root", "child2", RelationshipType.CONTAINS)

    path = await engine.traverse("root")
    assert len(path) == 3


@pytest.mark.asyncio
async def test_get_subgraph(engine: GraphEngine) -> None:
    await engine.add_node("n1", "X", {})
    await engine.add_node("n2", "Y", {})
    await engine.add_node("n3", "Z", {})
    await engine.add_edge("n1", "n2", RelationshipType.RELATES_TO)
    await engine.add_edge("n2", "n3", RelationshipType.RELATES_TO)

    subgraph = await engine.get_subgraph(["n1", "n2"])
    assert len(subgraph["nodes"]) == 2
    assert len(subgraph["edges"]) == 1


@pytest.mark.asyncio
async def test_entity_manager_create_and_get(entity_manager: EntityManager) -> None:
    await entity_manager.create_entity("e1", "Concept", {"description": "test"})
    entity = await entity_manager.get_entity("e1")
    assert entity is not None
    assert entity["label"] == "Concept"


@pytest.mark.asyncio
async def test_entity_manager_update(entity_manager: EntityManager) -> None:
    await entity_manager.create_entity("e2", "Concept", {"value": 1})
    updated = await entity_manager.update_entity("e2", {"value": 2, "new_key": "yes"})
    assert updated["properties"]["value"] == 2
    assert updated["properties"]["new_key"] == "yes"


@pytest.mark.asyncio
async def test_entity_manager_delete(entity_manager: EntityManager) -> None:
    await entity_manager.create_entity("e3", "Temp", {})
    assert await entity_manager.delete_entity("e3") is True
    assert await entity_manager.get_entity("e3") is None


@pytest.mark.asyncio
async def test_entity_manager_list_by_label(entity_manager: EntityManager) -> None:
    await entity_manager.create_entity("a1", "Animal", {})
    await entity_manager.create_entity("a2", "Animal", {})
    await entity_manager.create_entity("v1", "Vegetable", {})
    animals = await entity_manager.list_entities("Animal")
    assert len(animals) == 2


@pytest.mark.asyncio
async def test_relationship_builder_create(relationship_builder: RelationshipBuilder) -> None:
    rel = await relationship_builder.create_relationship("src", "tgt", RelationshipType.REQUIRES)
    assert rel["type"] == "requires"
    assert rel["source_id"] == "src"
    assert rel["target_id"] == "tgt"


@pytest.mark.asyncio
async def test_relationship_builder_infer(relationship_builder: RelationshipBuilder) -> None:
    inferred = await relationship_builder.infer_relationship("source_code", "compiled_binary")
    assert len(inferred) >= 1
    assert inferred[0]["inferred_type"] == "produces"


@pytest.mark.asyncio
async def test_relationship_builder_batch(relationship_builder: RelationshipBuilder) -> None:
    batch = [
        {"source_id": "a", "target_id": "b", "type": "depends_on"},
        {"source_id": "b", "target_id": "c", "type": "contains"},
    ]
    results = await relationship_builder.batch_create(batch)
    assert len(results) == 2
    assert results[0]["type"] == "depends_on"


@pytest.mark.asyncio
async def test_relationship_builder_find_path(relationship_builder: RelationshipBuilder) -> None:
    await relationship_builder.create_relationship("x", "y", RelationshipType.DEPENDS_ON)
    await relationship_builder.create_relationship("y", "z", RelationshipType.DEPENDS_ON)
    paths = await relationship_builder.get_relationship_path("x", "z")
    assert len(paths) >= 1
    assert len(paths[0]) == 2


@pytest.mark.asyncio
async def test_knowledge_mapper_create_map(knowledge_mapper: KnowledgeMapper) -> None:
    nodes = [{"id": "n1", "label": "A"}, {"id": "n2", "label": "B"}]
    edges = [{"source": "n1", "target": "n2", "type": "relates_to"}]
    km = await knowledge_mapper.create_map("map1", nodes, edges)
    assert km["node_count"] == 2
    assert km["edge_count"] == 1


@pytest.mark.asyncio
async def test_knowledge_mapper_connected_components(knowledge_mapper: KnowledgeMapper) -> None:
    adj = {
        "a": ["b"],
        "b": ["a"],
        "c": ["d"],
        "d": ["c"],
    }
    components = await knowledge_mapper.get_connected_components(adj)
    assert len(components) == 2


@pytest.mark.asyncio
async def test_knowledge_mapper_analyze_density(knowledge_mapper: KnowledgeMapper) -> None:
    adj = {
        "a": ["b", "c"],
        "b": ["a", "c"],
        "c": ["a", "b"],
    }
    analysis = await knowledge_mapper.analyze_density(adj)
    assert analysis["node_count"] == 3
    assert analysis["edge_count"] == 6
    assert analysis["is_dense"] is True


@pytest.mark.asyncio
async def test_knowledge_mapper_summary(knowledge_mapper: KnowledgeMapper) -> None:
    nodes = [{"id": "n1", "label": "Service"}, {"id": "n2", "label": "Database"}]
    edges = [{"source": "n1", "target": "n2", "type": "depends_on"}]
    await knowledge_mapper.create_map("summary_map", nodes, edges)
    summary = await knowledge_mapper.get_knowledge_map_summary("summary_map")
    assert summary["node_count"] == 2
    assert "Service" in summary["node_labels"]


@pytest.mark.asyncio
async def test_engine_metrics(engine: GraphEngine) -> None:
    await engine.add_node("m1", "Node1", {})
    await engine.add_node("m2", "Node2", {})
    await engine.add_node("m3", "Node3", {})
    await engine.add_edge("m1", "m2", RelationshipType.CONTAINS)
    await engine.add_edge("m2", "m3", RelationshipType.CONTAINS)
    await engine.query("m1", depth=2)
    assert engine.metrics.total_nodes == 3
    assert engine.metrics.total_edges == 2
    assert engine.metrics.queries_executed == 1