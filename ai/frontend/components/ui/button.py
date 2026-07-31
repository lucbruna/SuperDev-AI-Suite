"""
Button UI Component
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class ButtonVariant(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    GHOST = "ghost"
    LINK = "link"


class ButtonSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


@dataclass
class ButtonProps:
    variant: ButtonVariant = ButtonVariant.PRIMARY
    size: ButtonSize = ButtonSize.MD
    disabled: bool = False
    loading: bool = False
    icon: str | None = None
    icon_position: str = "left"
    full_width: bool = False
    type: str = "button"
    onClick: Callable | None = None


class Button:
    def __init__(self, props: ButtonProps | None = None):
        self.props = props or ButtonProps()
        self.clicked = False

    def click(self):
        if not self.props.disabled and not self.props.loading:
            self.clicked = True
            if self.props.onClick:
                self.props.onClick()

    def get_class_name(self):
        classes = ["btn", "btn-" + self.props.variant.value, "btn-" + self.props.size.value]
        if self.props.full_width:
            classes.append("btn-block")
        if self.props.loading:
            classes.append("btn-loading")
        return " ".join(classes)

    def is_disabled(self):
        return self.props.disabled or self.props.loading
