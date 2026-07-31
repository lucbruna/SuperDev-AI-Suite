"""
Tooltip UI Component
"""
from typing import Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum


class TooltipPlacement(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class TooltipTrigger(Enum):
    HOVER = "hover"
    CLICK = "click"
    FOCUS = "focus"


@dataclass
class TooltipProps:
    content: str = ""
    placement: TooltipPlacement = TooltipPlacement.TOP
    trigger: TooltipTrigger = TooltipTrigger.HOVER
    delay: int = 200
    arrow: bool = True
    disabled: bool = False
    maxWidth: int = 300
    children: Optional[Any] = None
    onShow: Optional[Callable] = None
    onHide: Optional[Callable] = None


class Tooltip:
    def __init__(self, props: Optional[TooltipProps] = None):
        self.props = props or TooltipProps()
        self._visible = False
        
    def show(self):
        if not self.props.disabled:
            self._visible = True
            if self.props.onShow:
                self.props.onShow()
                
    def hide(self):
        self._visible = False
        if self.props.onHide:
            self.props.onHide()
            
    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()
