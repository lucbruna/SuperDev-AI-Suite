"""
Dropdown UI Component
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DropdownSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


@dataclass
class DropdownItem:
    label: str
    value: Any
    icon: str | None = None
    disabled: bool = False
    divider: bool = False


@dataclass
class DropdownProps:
    trigger: str = "click"
    size: DropdownSize = DropdownSize.MD
    items: list[DropdownItem] = field(default_factory=list)
    disabled: bool = False
    placeholder: str = "Select..."
    value: Any | None = None
    onChange: Callable | None = None


class Dropdown:
    def __init__(self, props: DropdownProps | None = None):
        self.props = props or DropdownProps()
        self._isOpen = False
        self._selectedValue = self.props.value

    def open(self):
        self._isOpen = True

    def close(self):
        self._isOpen = False

    def toggle(self):
        if self._isOpen:
            self.close()
        else:
            self.open()

    def select(self, item):
        if item.disabled or item.divider:
            return
        self._selectedValue = item.value
        self.close()
        if self.props.onChange:
            self.props.onChange(item.value)

    def get_selected_label(self):
        for item in self.props.items:
            if item.value == self._selectedValue:
                return item.label
        return self.props.placeholder
