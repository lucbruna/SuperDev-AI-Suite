"""Adapters subsystem for Integration Hub & API Ecosystem Engine."""

from .adapter_engine import AdapterEngine
from .adapter_manager import AdapterManager
from .protocol_adapter import ProtocolAdapter
from .format_adapter import FormatAdapter
from .legacy_adapter import LegacyAdapter

__all__ = [
    'AdapterEngine',
    'AdapterManager',
    'ProtocolAdapter',
    'FormatAdapter',
    'LegacyAdapter',
]
