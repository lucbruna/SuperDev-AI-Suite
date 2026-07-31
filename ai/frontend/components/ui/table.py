"""
Table UI Component
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"


class TableSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


@dataclass
class TableColumn:
    key: str
    label: str
    sortable: bool = True
    width: str | None = None
    align: str = "left"


@dataclass
class TableProps:
    columns: list[TableColumn] = field(default_factory=list)
    data: list[dict[str, Any]] = field(default_factory=list)
    size: TableSize = TableSize.MD
    striped: bool = True
    hoverable: bool = True
    loading: bool = False
    pagination: bool = True
    pageSize: int = 10
    currentPage: int = 1


class Table:
    def __init__(self, props: TableProps | None = None):
        self.props = props or TableProps()
        self._currentPage = self.props.currentPage
        self._pageSize = self.props.pageSize

    @property
    def paginated_data(self):
        data = self.props.data
        if not self.props.pagination:
            return data
        start = (self._currentPage - 1) * self._pageSize
        end = start + self._pageSize
        return data[start:end]

    @property
    def total_pages(self):
        return max(1, (len(self.props.data) + self._pageSize - 1) // self._pageSize)
