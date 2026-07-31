"""
Modal UI Component
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class ModalSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


@dataclass
class ModalProps:
    title: str = ""
    size: ModalSize = ModalSize.MD
    isOpen: bool = False
    closeOnOverlay: bool = True
    closeOnEsc: bool = True
    showClose: bool = True
    onClose: Callable | None = None
    onConfirm: Callable | None = None


class Modal:
    def __init__(self, props: ModalProps | None = None):
        self.props = props or ModalProps()
        self._isOpen = self.props.isOpen

    def open(self):
        self._isOpen = True

    def close(self):
        self._isOpen = False
        if self.props.onClose:
            self.props.onClose()

    def toggle(self):
        if self._isOpen:
            self.close()
        else:
            self.open()

    def confirm(self):
        if self.props.onConfirm:
            self.props.onConfirm()
        self.close()
