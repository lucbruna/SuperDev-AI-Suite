"""Voice Matcher — finds the closest cloned voice for a sample."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_voice_clone.speaker_encoder import encode_file
from modules.ai_video_studio.ai_voice_clone.speaker_embeddings import SpeakerEmbeddings
from modules.ai_video_studio.ai_voice_clone.voice_similarity import cosine_similarity, match_threshold


class VoiceMatcher:
    """Matches an unknown sample to the nearest stored clone."""

    def __init__(self, embeddings: SpeakerEmbeddings | None = None) -> None:
        self.embeddings = embeddings or SpeakerEmbeddings()

    def match(self, sample_path: str, *, top_k: int = 3) -> list[dict[str, Any]]:
        query = encode_file(sample_path)
        scored: list[dict[str, Any]] = []
        for clone in self.embeddings.list():
            stored = self.embeddings.load_embedding(clone["id"])
            if stored is None:
                continue
            score = cosine_similarity(query, stored)
            scored.append({"clone_id": clone["id"], "similarity": round(score * 100, 1), **clone})
        scored.sort(key=lambda d: d["similarity"], reverse=True)
        return scored[:top_k]

    def best_match(self, sample_path: str) -> dict[str, Any] | None:
        results = self.match(sample_path, top_k=1)
        if not results:
            return None
        best = results[0]
        same_speaker = best["similarity"] / 100.0 >= match_threshold()
        return {**best, "same_speaker": same_speaker}
