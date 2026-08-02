"""Rust package — cargo toolchain facade (Vol 12, Fase 21)."""
from __future__ import annotations

from modules.aios.rust.cargo import CargoCommands
from modules.aios.rust.clippy import Clippy
from modules.aios.rust.rust_client import (
    CargoClient,
    RustUnavailableError,
    require_rust_action,
)
from modules.aios.rust.rust_runtime import RustRuntime, get_rust_runtime

__all__ = [
    "CargoClient",
    "CargoCommands",
    "Clippy",
    "RustRuntime",
    "RustUnavailableError",
    "get_rust_runtime",
    "require_rust_action",
]
