"""AI Platform — public API layer over the core AI engine.

Safe imports — gracefully handles missing provider implementations.
"""
from __future__ import annotations

import importlib
import logging

logger = logging.getLogger(__name__)

# Safe re-export of core AI modules
_AI_MODULES = [
    "ai_config",
    "ai_constants",
    "ai_context",
    "ai_engine",
    "ai_exceptions",
    "ai_factory",
    "ai_interfaces",
    "ai_logger",
    "ai_manager",
    "ai_models",
    "ai_registry",
    "ai_types",
    "ai_utils",
]

for _mod_name in _AI_MODULES:
    try:
        module = importlib.import_module(f"ai.{_mod_name}")
        globals()[_mod_name] = module
    except (ImportError, ModuleNotFoundError) as e:
        logger.debug("AI module not available: ai.%s — %s", _mod_name, e)
