from typing import Any, Callable

from sqlalchemy.sql import Select


class FilterField:
    def __init__(
        self,
        field_name: str,
        operator: Callable[[Any, Any], Any] | None = None,
    ) -> None:
        self.field_name = field_name
        self.operator = operator


class FilterSet:
    def __init__(self) -> None:
        self.filters: dict[str, FilterField] = {}

    def add_filter(self, name: str, field_name: str) -> None:
        self.filters[name] = FilterField(field_name=field_name)



def apply_filters(query: Select, filters: dict[str, Any], model: type) -> Select:
    for field_name, value in filters.items():
        if value is None:
            continue
        column = getattr(model, field_name, None)
        if column is not None:
            query = query.where(column == value)
    return query
