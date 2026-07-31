"""Knowledge Graph models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    PRODUCT = "product"
    EVENT = "event"
    CONCEPT = "concept"
    DATASET = "dataset"


class RelationType(Enum):
    WORKS_FOR = "works_for"
    PRODUCES = "produces"
    CONSUMES = "consumes"
    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    CAUSED_BY = "caused_by"


@dataclass
class Entity:
    entity_id: str
    name: str = ""
    entity_type: EntityType = EntityType.CONCEPT
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Relation:
    relation_id: str
    source_id: str = ""
    target_id: str = ""
    relation_type: RelationType = RelationType.RELATES_TO
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgePath:
    path_id: str
    entities: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    score: float = 0.0


@dataclass
class GraphQuery:
    query_id: str
    entity_type: EntityType | None = None
    relation_type: RelationType | None = None
    max_depth: int = 3
    limit: int = 100
