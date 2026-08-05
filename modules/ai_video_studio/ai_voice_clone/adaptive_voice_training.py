"""Adaptive Voice Training — refines a clone as more samples arrive.

Each new reference sample updates the stored embedding (running average) and
expands the metadata so the clone improves with exposure — a lightweight,
real "training" loop that requires no GPU.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np

from modules.ai_video_studio.ai_voice_clone.speaker_encoder import encode_file
from modules.ai_video_studio.ai_voice_clone.speaker_embeddings import SpeakerEmbeddings

logger = logging.getLogger(__name__)


class AdaptiveVoiceTraining:
    """Incremental embedding refinement per clone."""

    def __init__(self, embeddings: SpeakerEmbeddings | None = None) -> None:
        self.embeddings = embeddings or SpeakerEmbeddings()

    def add_sample(self, clone_id: str, sample_path: str, *, label: str = "") -> dict[str, Any]:
        vector = encode_file(sample_path)
        metadata = self.embeddings.load_metadata(clone_id) or {"samples": [], "created": time.time()}
        stored = self.embeddings.load_embedding(clone_id)

        if stored is None:
            updated = vector
        else:
            count = len(metadata.get("samples", []))
            weight = 1.0 / (count + 1)
            updated = stored * (1 - weight) + vector * weight

        metadata.setdefault("samples", []).append(
            {"file": sample_path, "ts": time.time(), "label": label}
        )
        metadata["updated"] = time.time()
        metadata["sample_count"] = len(metadata["samples"])
        metadata["embedding_mean"] = [round(float(v), 4) for v in updated.tolist()]

        directory = self.embeddings.save(clone_id, updated, metadata)
        return {"clone_id": clone_id, "sample_count": len(metadata["samples"]),
                "directory": str(directory)}

    def consolidate(self, clone_id: str) -> dict[str, Any]:
        """Recompute the embedding from all stored samples (mean)."""
        metadata = self.embeddings.load_metadata(clone_id) or {}
        samples = metadata.get("samples", [])
        if not samples:
            return {"clone_id": clone_id, "consolidated": False}
        vectors = [encode_file(s["file"]) for s in samples]
        mean = np.mean(vectors, axis=0).astype(np.float32)
        self.embeddings.save(clone_id, mean, {**metadata, "consolidated_at": time.time()})
        return {"clone_id": clone_id, "consolidated": True, "samples": len(samples)}
