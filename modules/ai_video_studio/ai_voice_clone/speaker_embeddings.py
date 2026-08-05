"""Speaker Embeddings — persistent storage of voice embeddings.

Each clone profile lives under ``modules/downloads/voice_clones/<id>/`` with
``embedding.npy`` (the vector) and ``profile.json`` (analysis + metadata).
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir

logger = logging.getLogger(__name__)

# Safe clone-id charset: ids become directory names, so anything else is
# rejected up front — prevents path traversal (``../``, absolute paths,
# Windows ``\\``) in every read/write/delete path, not just create.
_CLONE_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def safe_clone_id(clone_id: str) -> str:
    """Validate a clone id, raising ``ValidationError`` when it is unsafe.

    Central chokepoint: all profile reads/writes/deletes resolve through this
    so a malicious id can never escape the voice_clones root.
    """
    if not clone_id or not _CLONE_ID_RE.match(clone_id) or clone_id in {".", ".."}:
        raise ValidationError(
            "Clone id may only contain letters, digits, '_' and '-'",
            field="clone_id",
        )
    return clone_id


class SpeakerEmbeddings:
    """Reads/writes clone profiles and embeddings on disk."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or get_subsystem_dir("clones")

    def profile_dir(self, clone_id: str) -> Path:
        path = self.root / safe_clone_id(clone_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, clone_id: str, embedding: np.ndarray, metadata: dict[str, Any]) -> Path:
        directory = self.profile_dir(clone_id)
        np.save(directory / "embedding.npy", np.asarray(embedding, dtype=np.float32))
        with open(directory / "profile.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        return directory

    def load_embedding(self, clone_id: str) -> np.ndarray | None:
        path = self.root / safe_clone_id(clone_id) / "embedding.npy"
        if not path.exists():
            return None
        try:
            return np.load(path)
        except Exception as e:  # noqa: BLE001
            logger.warning("embedding load failed for %s: %s", clone_id, e)
            return None

    def load_metadata(self, clone_id: str) -> dict[str, Any] | None:
        path = self.root / safe_clone_id(clone_id) / "profile.json"
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:  # noqa: BLE001
            logger.warning("profile load failed for %s: %s", clone_id, e)
            return None

    def list(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for directory in sorted(self.root.iterdir()):
            if not directory.is_dir():
                continue
            meta = self.load_metadata(directory.name) or {}
            out.append({"id": directory.name, **meta})
        return out

    def delete(self, clone_id: str) -> bool:
        import shutil

        path = self.root / safe_clone_id(clone_id)
        if path.is_dir():
            shutil.rmtree(path)
            return True
        return False
