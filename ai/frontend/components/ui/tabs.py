"""
Tabs UI Component
"""
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class TabsSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


class TabsVariant(Enum):
    DEFAULT = "default"
    BOXED = "boxed"
    PILLS = "pills"
    UNDERLINE = "underline"


@dataclass
class Tab:
    key: str
    label: str
    icon: str | None = None
    disabled: bool = False
    badge: str | None = None


@dataclass
class TabsProps:
    tabs: list[Tab] = field(default_factory=list)
    activeKey: str | None = None
    size: TabsSize = TabsSize.MD
    variant: TabsVariant = TabsVariant.DEFAULT
    animated: bool = True
    onChange: Callable | None = None


class Tabs:
    def __init__(self, props: TabsProps | None = None):
        self.props = props or TabsProps()
        self._activeKey = self.props.activeKey or (self.props.tabs[0].key if self.props.tabs else "")

    def set_active(self, key):
        for tab in self.props.tabs:
            if tab.key == key and not tab.disabled:
                self._activeKey = key
                if self.props.onChange:
                    self.props.onChange(key)
                return

    def next(self):
        keys = [t.key for t in self.props.tabs if not t.disabled]
        idx = keys.index(self._activeKey) if self._activeKey in keys else -1
        if idx < len(keys) - 1:
            self.set_active(keys[idx + 1])
