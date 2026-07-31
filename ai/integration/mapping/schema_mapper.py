"""
Schema Mapper - Schema-level mapping
"""

from dataclasses import dataclass, field


@dataclass
class SchemaField:
    name: str
    field_type: str
    nullable: bool = True
    description: str = ""


@dataclass
class SchemaDefinition:
    name: str
    fields: list[SchemaField] = field(default_factory=list)
    version: str = "1.0"


class SchemaMapper:
    def __init__(self):
        self.schemas: dict[str, SchemaDefinition] = {}
        self.mappings: dict[str, dict[str, str]] = {}

    def register_schema(self, name: str, fields: list[dict[str, str]] = None) -> SchemaDefinition:
        schema_fields = [SchemaField(name=f["name"], field_type=f.get("type", "string")) for f in (fields or [])]
        schema = SchemaDefinition(name=name, fields=schema_fields)
        self.schemas[name] = schema
        return schema

    def create_mapping(self, source_schema: str, target_schema: str, field_mappings: dict[str, str]) -> None:
        key = f"{source_schema}:{target_schema}"
        self.mappings[key] = field_mappings

    def get_mapping(self, source_schema: str, target_schema: str) -> dict[str, str] | None:
        return self.mappings.get(f"{source_schema}:{target_schema}")

    def get_schema(self, name: str) -> SchemaDefinition | None:
        return self.schemas.get(name)

    def list_schemas(self) -> list[SchemaDefinition]:
        return list(self.schemas.values())

    def count(self) -> int:
        return len(self.schemas)
