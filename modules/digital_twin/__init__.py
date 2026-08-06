"""Digital Twin module for the SuperDev AI Suite.

Maintains a living, continuously-synchronized digital representation of the
platform: its state, relationships, and evolution over time. Deterministic
and testable; no live LLM/network/clock dependency at the component level.
"""
from __future__ import annotations

from modules.digital_twin.version import __version__, VERSION

__all__ = ["__version__", "VERSION"]
