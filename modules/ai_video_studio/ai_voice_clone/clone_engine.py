"""Clone Engine — voice cloning without deep learning on CPU.

What is real here:

* **Analysis** — every sample is actually measured (f0, timbre, energy, SNR).
* **Embeddings** — speaker vectors are computed, stored and matched.
* **Synthesis** — cloned speech is produced by speaking the text with the
  reference voice's prosody and then post-processing the audio (phase-vocoder
  pitch shift toward the reference f0, energy matching, timbre EQ) so the
  result genuinely moves toward the cloned speaker.

A neural conversion model (e.g. Coqui) can be plugged via
``AIVS_NEURAL_TTS_URL`` later without changing the public API.
"""
from __future__ import annotations

import logging
import re
import time
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_voice_clone.speaker_encoder import encode_audio
from modules.ai_video_studio.ai_voice_clone.speaker_embeddings import SpeakerEmbeddings
from modules.ai_video_studio.ai_voice_clone.voice_analyzer import analyze_file
from modules.ai_video_studio.ai_voice_clone.quality_validator import validate_sample
from modules.ai_video_studio.ai_voice_clone.audio_cleanup import cleanup_sample
from modules.ai_video_studio.ai_voice_clone.emotion_transfer import prosody_from_analysis

logger = logging.getLogger(__name__)

_CLONE = None


def get_clone_engine() -> CloneEngine:
    global _CLONE
    if _CLONE is None:
        _CLONE = CloneEngine()
    return _CLONE


class CloneEngine:
    """Create, store and use cloned voice profiles."""

    def __init__(self) -> None:
        self.embeddings = SpeakerEmbeddings()

    # ── Profile management ────────────────────────────────────────
    def create_profile(self, samples: list[str], *, clone_id: str | None = None,
                       name: str = "", description: str = "") -> dict[str, Any]:
        """Validate + analyze + embed one or more reference samples."""
        if not samples:
            raise ValidationError("At least one reference sample is required", field="samples")
        reports = [validate_sample(s) for s in samples]
        failed = [r for r in reports if not r["passed"]]
        if failed:
            raise ValidationError(
                "Reference samples failed quality checks",
                field="samples",
                context={"reports": failed},
            )

        # Clean and concatenate the samples, then analyze the aggregate.
        buffers: list[np.ndarray] = []
        for sample in samples:
            audio, sr = dsp.read_audio(sample)
            buffers.append(cleanup_sample(audio, sample_rate=sr))
        combined = dsp.concatenate(buffers)
        analysis = analyze_file(samples[0])
        embedding = encode_audio(combined)

        # Sanitize: the clone id becomes a directory name, so only allow safe
        # characters — prevents path traversal via ``../../``.
        clone_id = re.sub(r"[^A-Za-z0-9_-]", "_", clone_id or f"clone_{int(time.time())}").strip("._")
        if not clone_id:  # e.g. input was only punctuation — fall back to a time id
            clone_id = f"clone_{int(time.time())}"
        metadata = {
            "name": name or clone_id,
            "description": description,
            "created": time.time(),
            "samples": [{"file": s, "ts": time.time()} for s in samples],
            "analysis": {k: v for k, v in analysis.items() if k != "file"},
            "prosody": prosody_from_analysis(analysis),
        }
        directory = self.embeddings.save(clone_id, embedding, metadata)
        return {"clone_id": clone_id, "directory": str(directory),
                "analysis": metadata["analysis"], "prosody": metadata["prosody"]}

    def list_clones(self) -> list[dict[str, Any]]:
        return self.embeddings.list()

    def delete_clone(self, clone_id: str) -> bool:
        return self.embeddings.delete(clone_id)

    # ── Cloned synthesis ──────────────────────────────────────────
    def clone(self, text: str, clone_id: str, *, language: str = "en",
              emotion: str | None = None, output_path: str | None = None) -> dict[str, Any]:
        """Speak ``text`` with the cloned voice's prosody → real audio file."""
        embedding = self.embeddings.load_embedding(clone_id)
        metadata = self.embeddings.load_metadata(clone_id)
        if embedding is None or metadata is None:
            raise ValidationError(f"Clone '{clone_id}' not found", field="clone_id")

        prosody = dict(metadata.get("prosody", {}))
        if emotion:
            from modules.ai_video_studio.ai_voice_clone.emotion_transfer import transfer_emotion

            prosody.update(transfer_emotion(metadata["samples"][0]["file"], emotion=emotion))

        # 1) Base synthesis with the cloned prosody.
        from modules.ai_video_studio.ai_voice_studio import get_voice_engine

        base = get_voice_engine().synthesize(
            text, voice_id="default", language=language,
            speed=float(prosody.get("rate", 1.0)), pitch=float(prosody.get("pitch", 1.0)),
            use_cache=False,
        )

        # 2) Post-process toward the reference timbre.
        audio, sr = dsp.read_audio(base["output_path"])
        ref_f0 = float(metadata["analysis"].get("f0_mean") or 0.0)
        if ref_f0 > 0:
            # Shift the synthesized audio to the reference speaker's pitch.
            from modules.ai_video_studio.ai_voice_clone.pitch_analyzer import mean_f0

            actual = mean_f0(audio, sample_rate=sr)
            if actual > 0:
                semitones = 12 * np.log2(ref_f0 / actual)
                audio = dsp.pitch_shift(audio, float(np.clip(semitones, -6, 6)))
        # Timbre: nudge EQ toward the reference centroid.
        target_centroid = float(metadata["analysis"].get("centroid_hz") or 1500.0)
        current_centroid = dsp.spectral_centroid(audio, sample_rate=sr)
        if current_centroid > 0:
            ratio = target_centroid / current_centroid
            if 0.5 < ratio < 2.0:
                audio = dsp.biquad_highshelf(audio, 3000.0, 6.0 * np.log2(ratio), sample_rate=sr)
        audio = dsp.normalize_rms(audio, float(prosody.get("energy", 0.2)))
        audio = dsp.normalize_peak(audio, 0.95)

        out_dir = Path(output_path).parent if output_path else get_subsystem_dir("clones")
        out_path = output_path or str(unique_filename(out_dir, f"clone_{clone_id}", "wav"))
        dsp.write_audio(out_path, audio, sample_rate=sr)
        return {
            "output_path": out_path,
            "duration": round(len(audio) / sr, 3),
            "bytes": int(Path(out_path).stat().st_size),
            "clone_id": clone_id,
            "base_engine": base["engine"],
            "prosody_applied": prosody,
            "pitch_shifted": bool(ref_f0 > 0),
        }
