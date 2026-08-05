"""Lip Sync Engine — drives mouth shapes from audio/text.

Produces:
* a per-frame **viseme timeline** (JSON) consumable by animators.
* an optional **mouth animation MP4** rendered with PIL so the output is a
  real video file, not just metadata.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_lip_sync.phoneme_mapper import map_text_to_phonemes
from modules.ai_video_studio.ai_lip_sync.viseme_mapper import map_phoneme
from modules.ai_video_studio.ai_lip_sync.facial_sync import build_facial_timeline

logger = logging.getLogger(__name__)

_LIP = None


def get_lip_sync_engine() -> LipSyncEngine:
    global _LIP
    if _LIP is None:
        _LIP = LipSyncEngine()
    return _LIP


class LipSyncEngine:
    """Generates lip-sync data and a real mouth-animation video."""

    def generate(
        self,
        text: str,
        *,
        audio_path: str | None = None,
        duration: float | None = None,
        fps: int = 24,
        render_video: bool = True,
        output_dir: str | None = None,
    ) -> dict[str, Any]:
        """Return ``{timeline, duration, frames, ...}`` (+ optional MP4)."""
        if audio_path:
            from modules.ai_video_studio.media import dsp

            audio, sr = dsp.read_audio(audio_path)
            duration = len(audio) / sr
        duration = duration or max(1.0, len(text) / 15.0)

        phonemes = map_text_to_phonemes(text, duration=duration)
        frame_count = max(1, int(duration * fps))

        # Per-frame visemes (hold each viseme until the next one starts).
        frames: list[dict[str, Any]] = []
        for f in range(frame_count):
            t = f / fps
            current = {"frame": f, "time": round(t, 3)}
            for entry in phonemes:
                if entry["start"] <= t < entry["end"]:
                    current.update(map_phoneme(entry["phoneme"]))
                    current["phoneme"] = entry["phoneme"]
                    break
            current.setdefault("viseme", "closed")
            current.setdefault("open", 0.0)
            current.setdefault("round", 0.0)
            current.setdefault("wide", 0.0)
            current.setdefault("tense", 0.0)
            frames.append(current)

        facial = build_facial_timeline(frames)
        result: dict[str, Any] = {
            "duration": round(duration, 3),
            "fps": fps,
            "frames": frame_count,
            "phonemes": len(phonemes),
            "timeline": frames,
            "facial": facial,
        }

        out_dir = Path(output_dir or get_subsystem_dir("lip_sync"))
        if render_video:
            out = unique_filename(out_dir, "lip_sync", "mp4")
            self._render_mouth_video(frames, out, fps=fps, width=320, height=240)
            result["output_path"] = str(out)
            result["output_bytes"] = out.stat().st_size

        # Also persist the timeline JSON for animators.
        json_path = unique_filename(out_dir, "lip_sync_timeline", "json")
        json_path.write_text(json.dumps({"duration": result["duration"], "fps": fps, "frames": facial},
                                        indent=2), encoding="utf-8")
        result["timeline_path"] = str(json_path)
        return result

    # ── Mouth animation renderer ──────────────────────────────────
    @staticmethod
    def _render_mouth_video(frames: list[dict[str, Any]], out_path: Path, *,
                            fps: int, width: int, height: int) -> None:
        from PIL import Image, ImageDraw

        from modules.ai_video_studio.media.video import frames_to_video

        rendered: list[np.ndarray] = []
        for frame in frames:
            img = Image.new("RGB", (width, height), (24, 26, 38))
            draw = ImageDraw.Draw(img)
            # Face.
            face_x, face_y, face_w, face_h = width // 2 - 70, 40, 140, 170
            draw.ellipse([face_x, face_y, face_x + face_w, face_y + face_h], fill=(120, 96, 80))
            # Eyes.
            eye_l = 100
            eye_r = 200
            eye_y = 100
            blink = frame.get("_blink", 0.0)
            if blink < 0.5:
                draw.ellipse([eye_l - 14, eye_y - 14, eye_l + 14, eye_y + 14], fill=(30, 30, 34))
                draw.ellipse([eye_r - 14, eye_y - 14, eye_r + 14, eye_y + 14], fill=(30, 30, 34))
            else:
                draw.line([eye_l - 14, eye_y, eye_l + 14, eye_y], fill=(30, 30, 34), width=3)
                draw.line([eye_r - 14, eye_y, eye_r + 14, eye_y], fill=(30, 30, 34), width=3)
            # Mouth.
            open_amt = frame.get("open", 0.0)
            wide = frame.get("wide", 0.0)
            round_ = frame.get("round", 0.0)
            mouth_y = 185
            mw = 30 + wide * 30
            mh = 4 + open_amt * 26
            if round_ > 0.5:
                draw.ellipse([width // 2 - mw, mouth_y - mh, width // 2 + mw, mouth_y + mh],
                             fill=(60, 24, 30), outline=(20, 20, 24))
            else:
                draw.rounded_rectangle(
                    [width // 2 - mw, mouth_y - mh, width // 2 + mw, mouth_y + mh],
                    radius=mh, fill=(60, 24, 30), outline=(20, 20, 24),
                )
            rendered.append(np.asarray(img, dtype=np.uint8))

        frames_to_video(rendered, out_path, fps=fps)
