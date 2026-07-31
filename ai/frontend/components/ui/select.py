"""
Select UI Component
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SelectSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


class SelectMode(Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"


@dataclass
class SelectOption:
    label: str
    value: Any
    disabled: bool = False
    group: str | None = None


@dataclass
class SelectProps:
    options: list[SelectOption] = field(default_factory=list)
    size: SelectSize = SelectSize.MD
    mode: SelectMode = SelectMode.SINGLE
    placeholder: str = "Select..."
    value: Any | None = None
    disabled: bool = False
    searchable: bool = False
    clearable: bool = False
    onChange: Callable | None = None


class Select:
    def __init__(self, props: SelectProps | None = None):
        self.props = props or SelectProps()
        self._isOpen = False
        self._searchTerm = ""
        self._selectedValue = self.props.value
        self._selectedMultiple = []

    def open(self):
        self._isOpen = True

    def close(self):
        self._isOpen = False
        self._searchTerm = ""

    def select(self, option):
        if option.disabled:
            return
        if self.props.mode == SelectMode.SINGLE:
            self._selectedValue = option.value
            self.close()
            if self.props.onChange:
                self.props.onChange(option.value)
        else:
            if option.value in self._selectedMultiple:
                self._selectedMultiple.remove(option.value)
            else:
                self._selectedMultiple.append(option.value)
            if self.props.onChange:
                self.props.onChange(self._selectedMultiple)

    def clear(self):
        if self.props.mode == SelectMode.SINGLE:
            self._selectedValue = None
        else:
            self._selectedMultiple.clear()
