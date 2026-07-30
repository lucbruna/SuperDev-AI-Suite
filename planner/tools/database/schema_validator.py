from __future__ import annotations

from typing import Any


class SchemaValidator:
    """Validate database schema definitions."""

    @staticmethod
    def validate_column(col: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "name" not in col:
            errors.append("Column missing 'name'")
        if "type" not in col:
            errors.append("Column missing 'type'")
        return errors

    @staticmethod
    def validate_table(name: str, columns: list[dict[str, Any]]) -> dict[str, Any]:
        errors: list[str] = []
        if not name:
            errors.append("Table name is empty")
        if not columns:
            errors.append("Table has no columns")
        else:
            for col in columns:
                errors.extend(SchemaValidator.validate_column(col))
        return {"valid": len(errors) == 0, "errors": errors, "table": name}

    @staticmethod
    def validate_schema(schema: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
        all_errors: dict[str, list[str]] = {}
        for table_name, columns in schema.items():
            result = SchemaValidator.validate_table(table_name, columns)
            if not result["valid"]:
                all_errors[table_name] = result["errors"]
        return {"valid": len(all_errors) == 0, "errors": all_errors}
