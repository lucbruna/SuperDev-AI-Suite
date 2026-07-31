"""
Modal UI Component
"""
from typing import Optional, Callable, Any
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
    onClose: Optional[Callable] = None
    onConfirm: Optional[Callable] = None


class Modal:
    def __init__(self, props: Optional[ModalProps] = None):
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
