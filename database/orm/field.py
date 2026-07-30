from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class FieldMetadata:
    """Metadata for a model field."""

    name: str = ""
    data_type: str = "text"
    primary_key: bool = False
    nullable: bool = True
    unique: bool = False
    default: Any = None
    max_length: int | None = None
    foreign_key: str | None = None
    index: bool = False


class Field:
    """Descriptor that captures field metadata from model class definitions.

    Usage::

        class User(Model):
            id = Field(data_type="integer", primary_key=True)
            name = Field(data_type="text", nullable=False)
    """

    def __init__(
        self,
        data_type: str = "text",
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        default: Any = None,
        max_length: int | None = None,
        foreign_key: str | None = None,
        index: bool = False,
    ) -> None:
        self.metadata = FieldMetadata(
            data_type=data_type,
            primary_key=primary_key,
            nullable=nullable,
            unique=unique,
            default=default,
            max_length=max_length,
            foreign_key=foreign_key,
            index=index,
        )

    def __set_name__(self, owner: type, name: str) -> None:
        self.metadata.name = name

    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return obj._values.get(self.metadata.name)

    def __set__(self, obj: Any, value: Any) -> None:
        obj._values[self.metadata.name] = value


__all__ = [
    "FieldMetadata",
    "Field",
]
