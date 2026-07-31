from __future__ import annotations

from .desktop_engine import DesktopEngine
from .windows import WindowsAdapter
from .linux import LinuxAdapter
from .macos import MacOSAdapter
from .terminal import DesktopTerminal
from .filesystem import DesktopFilesystem


def create_default_desktop_engine() -> DesktopEngine:
    engine = DesktopEngine()
    engine.register_platform("windows", {"adapter": "windows", "name": "Windows"})
    engine.register_platform("linux", {"adapter": "linux", "name": "Linux"})
    engine.register_platform("macos", {"adapter": "macos", "name": "macOS"})
    return engine


__all__ = [
    "DesktopEngine",
    "WindowsAdapter",
    "LinuxAdapter",
    "MacOSAdapter",
    "DesktopTerminal",
    "DesktopFilesystem",
    "create_default_desktop_engine",
]
