from __future__ import annotations

from .mobile_engine import MobileEngine
from .android import AndroidAdapter
from .ios import iOSAdapter
from .notifications import MobileNotifications
from .offline import OfflineCache
from .synchronization import SynchronizationEngine


def create_default_mobile_engine() -> MobileEngine:
    engine = MobileEngine()
    engine.register_platform("android", {"adapter": "android", "name": "Android"})
    engine.register_platform("ios", {"adapter": "ios", "name": "iOS"})
    return engine


__all__ = [
    "MobileEngine",
    "AndroidAdapter",
    "iOSAdapter",
    "MobileNotifications",
    "OfflineCache",
    "SynchronizationEngine",
    "create_default_mobile_engine",
]
