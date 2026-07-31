"""
Card UI Component
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class CardVariant(Enum):
    DEFAULT = "default"
    ELEVATED = "elevated"
    OUTLINED = "outlined"
    FILLED = "filled"


@dataclass
class CardProps:
    title: str | None = None
    subtitle: str | None = None
    variant: CardVariant = CardVariant.DEFAULT
    padding: bool = True
    hoverable: bool = False
    bordered: bool = False
    loading: bool = False
    onClick: Callable | None = None
    className: str | None = None


class Card:
    def __init__(self, props: CardProps | None = None):
        self.props = props or CardProps()

    def handle_click(self):
        if self.props.onClick:
            self.props.onClick()

    def get_class_name(self):
        classes = ["card", "card-" + self.props.variant.value]
        if self.props.hoverable:
            classes.append("card-hoverable")
        if self.props.bordered:
            classes.append("card-bordered")
        if self.props.loading:
            classes.append("card-loading")
        if self.props.className:
            classes.append(self.props.className)
        return " ".join(classes)
