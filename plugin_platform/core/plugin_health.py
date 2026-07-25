from __future__ import annotations

import logging
from typing import Any

from .plugin_configuration import PluginConfig

logger = logging.getLogger(__name__)


async def check_plugin_health(
    name: str,
    config: PluginConfig,
    is_loaded: bool,
    is_enabled: bool,
    resolved_dependencies: list[str],
) -> dict[str, Any]:
    version_ok = True
    try:
        parts = config.version.split(".")
        tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        version_ok = False

    dep_issues = []
    for dep in config.dependencies:
        if dep not in resolved_dependencies:
            dep_issues.append(dep)

    health = {
        "name": name,
        "loaded": is_loaded,
        "enabled": is_enabled,
        "version_match": version_ok,
        "version": config.version,
        "dependency_issues": dep_issues,
        "healthy": is_loaded and is_enabled and version_ok and len(dep_issues) == 0,
    }
    logger.info("Health check for %s: %s", name, health)
    return health