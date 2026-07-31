"""
Notification UI Component
"""
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPosition(Enum):
    TOP_RIGHT = "top-right"
    TOP_LEFT = "top-left"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM_LEFT = "bottom-left"


@dataclass
class NotificationProps:
    type: NotificationType = NotificationType.INFO
    title: str = ""
    message: str = ""
    duration: int = 5000
    position: NotificationPosition = NotificationPosition.TOP_RIGHT
    dismissible: bool = True
    onClose: Optional[Callable] = None


class Notification:
    def __init__(self, props: Optional[NotificationProps] = None):
        self.props = props or NotificationProps()
        self._visible = True
        self._createdAt = datetime.now()
        
    @property
    def age(self):
        return (datetime.now() - self._createdAt).total_seconds()
        
    @property
    def progress(self):
        if self.props.duration <= 0:
            return 100
        return min(100, (self.age / self.props.duration) * 100)
        
    def dismiss(self):
        self._visible = False
        if self.props.onClose:
            self.props.onClose()
            
    def get_icon(self):
        icons = {
            NotificationType.INFO: "info",
            NotificationType.SUCCESS: "check-circle",
            NotificationType.WARNING: "alert-triangle",
            NotificationType.ERROR: "x-circle",
        }
        return icons.get(self.props.type, "info")
