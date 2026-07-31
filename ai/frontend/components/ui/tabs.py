"""
Tabs UI Component
"""
from typing import Optional, Any, Callable, List
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
    icon: Optional[str] = None
    disabled: bool = False
    badge: Optional[str] = None


@dataclass
class TabsProps:
    tabs: List[Tab] = field(default_factory=list)
    activeKey: Optional[str] = None
    size: TabsSize = TabsSize.MD
    variant: TabsVariant = TabsVariant.DEFAULT
    animated: bool = True
    onChange: Optional[Callable] = None


class Tabs:
    def __init__(self, props: Optional[TabsProps] = None):
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
