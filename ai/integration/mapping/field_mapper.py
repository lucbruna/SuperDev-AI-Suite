"""
Field Mapper - Field-level transformations
"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class FieldTransform:
    source_field: str
    target_field: str
    transform_fn: Any = None
    transform_name: str = ""


class FieldMapper:
    def __init__(self):
        self.transforms: dict[str, list[FieldTransform]] = {}
        self.functions: dict[str, Callable] = {}

    def register_function(self, name: str, fn: Callable) -> None:
        self.functions[name] = fn

    def add_transform(self, mapping_name: str, source: str, target: str, transform_name: str = "") -> FieldTransform:
        transform = FieldTransform(source_field=source, target_field=target, transform_name=transform_name)
        self.transforms.setdefault(mapping_name, []).append(transform)
        return transform

    def apply(self, mapping_name: str, data: dict[str, Any]) -> dict[str, Any]:
        transforms = self.transforms.get(mapping_name, [])
        result = {}
        for t in transforms:
            value = data.get(t.source_field)
            if t.transform_name and t.transform_name in self.functions:
                value = self.functions[t.transform_name](value)
            result[t.target_field] = value
        return result

    def get_transforms(self, mapping_name: str) -> list[FieldTransform]:
        return self.transforms.get(mapping_name, [])

    def count(self) -> int:
        return sum(len(v) for v in self.transforms.values())
