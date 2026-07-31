"""Agent lifecycle management subsystem."""
from __future__ import annotations

from .activation import ActivationManager
from .health import HealthMonitor
from .lifecycle_engine import LifecycleEngine
from .shutdown import ShutdownManager
from .startup import StartupManager
from .suspension import SuspensionManager
from .versioning import VersionManager

__all__ = [
    "LifecycleEngine",
    "StartupManager",
    "ShutdownManager",
    "ActivationManager",
    "SuspensionManager",
    "VersionManager",
    "HealthMonitor",
]
