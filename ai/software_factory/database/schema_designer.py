"""Schema designer for creating database schemas."""

from typing import Any

from .models import Column, ColumnType, DatabaseSchema, ForeignKey, Index, Table


class SchemaDesigner:
    """Designs and creates database schemas."""

    def __init__(self):
        self._schemas: dict[str, DatabaseSchema] = {}

    def create_schema(self, name: str, description: str = "") -> DatabaseSchema:
        schema = DatabaseSchema(name=name, description=description)
        self._schemas[schema.schema_id] = schema
        return schema

    def create_table(self, schema: DatabaseSchema, name: str, columns: list[dict[str, Any]]) -> Table:
        table = Table(name=name)
        for col_def in columns:
            col_type_str = col_def.get("type", "varchar")
            try:
                col_type = ColumnType(col_type_str)
            except ValueError:
                col_type = ColumnType.VARCHAR
            col = Column(
                name=col_def.get("name", ""),
                column_type=col_type,
                nullable=col_def.get("nullable", True),
                primary_key=col_def.get("primary_key", False),
                unique=col_def.get("unique", False),
                max_length=col_def.get("max_length"),
            )
            table.add_column(col)
        schema.add_table(table)
        return table

    def add_index(self, table: Table, name: str, columns: list[str], unique: bool = False) -> Index:
        idx = Index(name=name, columns=columns, unique=unique, table_name=table.name)
        table.indexes.append(idx)
        return idx

    def add_foreign_key(
        self, table: Table, name: str, columns: list[str], ref_table: str, ref_columns: list[str]
    ) -> ForeignKey:
        fk = ForeignKey(
            name=name,
            columns=columns,
            reference_table=ref_table,
            reference_columns=ref_columns,
        )
        table.foreign_keys.append(fk)
        return fk

    def get_schema(self, schema_id: str) -> DatabaseSchema | None:
        return self._schemas.get(schema_id)

    def list_schemas(self) -> list[DatabaseSchema]:
        return list(self._schemas.values())

    def generate_ddl(self, schema: DatabaseSchema) -> str:
        """Generate DDL statements for a schema."""
        lines = []
        for table in schema.tables:
            col_defs = []
            for col in table.columns:
                parts = [f"    {col.name} {col.column_type.value}"]
                if col.primary_key:
                    parts.append("PRIMARY KEY")
                if col.auto_increment:
                    parts.append("AUTO_INCREMENT")
                if not col.nullable:
                    parts.append("NOT NULL")
                if col.unique:
                    parts.append("UNIQUE")
                col_defs.append(" ".join(parts))
            lines.append(f"CREATE TABLE {table.name} (")
            lines.append(",\n".join(col_defs))
            lines.append(");")
        return "\n".join(lines)
