from __future__ import annotations

from typing import Any, ClassVar

from .field import Field, FieldMetadata


class ModelMeta(type):
    """Metaclass that collects ``Field`` descriptors into ``_fields``."""

    def __new__(
        mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]
    ) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        fields: dict[str, FieldMetadata] = {}
        for base in reversed(bases):
            if hasattr(base, "_fields"):
                fields.update(base._fields)  # type: ignore[attr-defined]
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value.metadata
        cls._fields = fields  # type: ignore[attr-defined]
        cls._table = namespace.get("__table__", name.lower())  # type: ignore[attr-defined]
        return cls


class Model(metaclass=ModelMeta):
    """Base class for all ORM models.

    Subclasses declare fields using :class:`Field` descriptors::

        class Product(Model):
            __table__ = "products"

            id = Field(data_type="integer", primary_key=True)
            name = Field(data_type="text", nullable=False)
            price = Field(data_type="float", nullable=False)
    """

    _fields: ClassVar[dict[str, FieldMetadata]]
    _table: ClassVar[str]

    def __init__(self, **kwargs: Any) -> None:
        self._values: dict[str, Any] = {}
        for name, fmeta in self._fields.items():
            self._values[name] = kwargs.get(name, self._coerce_default(fmeta))

    @staticmethod
    def _coerce_default(fmeta: FieldMetadata) -> Any:
        if fmeta.default is not None:
            return fmeta.default() if callable(fmeta.default) else fmeta.default
        return None

    def __repr__(self) -> str:
        parts = ", ".join(f"{k}={v!r}" for k, v in self._values.items())
        return f"<{self.__class__.__name__}({parts})>"

    # -- query helpers --------------------------------------------------------

    def pk_value(self) -> Any:
        for name, fmeta in self._fields.items():
            if fmeta.primary_key:
                return self._values.get(name)
        return None

    def pk_name(self) -> str | None:
        for name, fmeta in self._fields.items():
            if fmeta.primary_key:
                return name
        return None

    def to_dict(self) -> dict[str, Any]:
        return dict(self._values)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Model:
        return cls(**data)

    @classmethod
    def fields(cls) -> dict[str, FieldMetadata]:
        return cls._fields

    @classmethod
    def _get_pk_name(cls) -> str | None:
        for name, fmeta in cls._fields.items():
            if fmeta.primary_key:
                return name
        return None

    @classmethod
    def table_name(cls) -> str:
        return cls._table


__all__ = [
    "ModelMeta",
    "Model",
]
