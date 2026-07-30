from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import Model


class Relationship:
    """Describes a relationship between two models.

    Usage::

        class Author(Model):
            books = Relationship(Book, foreign_key="author_id", rel_type="has_many")
    """

    def __init__(
        self,
        model_class: type[Model],
        foreign_key: str,
        rel_type: str = "has_many",
        local_key: str = "id",
        through: str | None = None,
    ) -> None:
        self.model_class: type[Model] = model_class
        self.foreign_key: str = foreign_key
        self.rel_type: str = rel_type  # has_many, has_one, many_to_many
        self.local_key: str = local_key
        self.through: str | None = through
        self.name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name


__all__ = [
    "Relationship",
]
