"""
Mapping Validation - Validate mappings
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class MappingValidator:
    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}

    def register_schema(self, name: str, schema: Dict[str, Any]) -> None:
        self.schemas[name] = schema

    def validate_mapping(self, source_schema: str, target_schema: str, field_mappings: Dict[str, str]) -> ValidationResult:
        errors = []
        warnings = []
        source = self.schemas.get(source_schema, {})
        target = self.schemas.get(target_schema, {})
        source_fields = set(source.get("fields", []))
        target_fields = set(target.get("fields", []))
        for source_field in field_mappings:
            if source_field not in source_fields:
                warnings.append(f"Source field '{source_field}' not in schema")
        for target_field in field_mappings.values():
            if target_field not in target_fields:
                warnings.append(f"Target field '{target_field}' not in schema")
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_data(self, schema_name: str, data: Dict[str, Any]) -> ValidationResult:
        errors = []
        schema = self.schemas.get(schema_name, {})
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def count(self) -> int:
        return len(self.schemas)
