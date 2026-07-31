"""JSON persistence helpers for the DevOps engine state.

Both ``DeploymentEngine`` and ``DevOpsEngine`` accept a ``store_path`` and
persist their in-memory state to JSON files in that directory. Writes are
atomic (temp file + rename) and loads degrade gracefully to the provided
default when the file is missing or corrupt.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("superdev.devops.store")


def load_json(path: Path, default: Any) -> Any:
    """Load JSON from disk, returning ``default`` when missing or corrupt."""
    try:
        if not path.exists():
            return default
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:  # pragma: no cover - defensive
        logger.warning("failed to load %s: %s", path, exc)
        return default


def save_json(path: Path, data: Any) -> None:
    """Atomically write JSON to disk (temp file + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.replace(path)
