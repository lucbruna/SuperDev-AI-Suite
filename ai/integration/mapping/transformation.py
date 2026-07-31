"""
Transformation - Data transformations
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class TransformType(Enum):
    UPPER = "upper"
    LOWER = "lower"
    TRIM = "trim"
    CAST = "cast"
    DEFAULT = "default"
    CONCAT = "concat"
    SPLIT = "split"
    REGEX = "regex"
    CUSTOM = "custom"


@dataclass
class TransformDef:
    name: str
    transform_type: TransformType
    params: Dict[str, Any] = field(default_factory=dict)


class TransformationEngine:
    def __init__(self):
        self.transforms: Dict[str, TransformDef] = {}
        self.functions: Dict[str, Callable] = {}

    def register_transform(self, name: str, transform_type: TransformType, params: Dict[str, Any] = None) -> TransformDef:
        t = TransformDef(name=name, transform_type=transform_type, params=params or {})
        self.transforms[name] = t
        return t

    def apply(self, transform_name: str, value: Any) -> Any:
        t = self.transforms.get(transform_name)
        if not t:
            return value
        if t.transform_type == TransformType.UPPER:
            return str(value).upper() if value else value
        elif t.transform_type == TransformType.LOWER:
            return str(value).lower() if value else value
        elif t.transform_type == TransformType.TRIM:
            return str(value).strip() if value else value
        elif t.transform_type == TransformType.CAST:
            cast_type = t.params.get("type", "str")
            return {"str": str, "int": int, "float": float}.get(cast_type, str)(value) if value else value
        elif t.transform_type == TransformType.DEFAULT:
            return value if value is not None else t.params.get("value")
        elif t.transform_type == TransformType.CONCAT:
            parts = t.params.get("parts", [])
            return "".join(str(value) if p == "$value" else p for p in parts)
        return value

    def get_transform(self, name: str) -> Optional[TransformDef]:
        return self.transforms.get(name)

    def list_transforms(self) -> List[TransformDef]:
        return list(self.transforms.values())

    def count(self) -> int:
        return len(self.transforms)
