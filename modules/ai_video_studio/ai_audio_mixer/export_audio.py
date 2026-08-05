"""Export Audio — writes mixes to WAV/MP3/FLAC/OGG files."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp


def export(samples: np.ndarray, path: str | Path, *, format: str = "wav",
           bitrate: str = "192k", metadata: dict[str, Any] | None = None,
           sample_rate: int = dsp.SAMPLE_RATE) -> dict[str, Any]:
    """Write ``samples`` to ``path`` (extension + format select the codec)."""
    out = Path(path)
    fmt = format.lower().lstrip(".")
    if fmt not in {"wav", "mp3", "flac", "ogg", "m4a"}:
        fmt = "wav"
    dsp.write_audio(out, samples, sample_rate=sample_rate, bitrate=bitrate)
    return {"output_path": str(out), "bytes": out.stat().st_size,
            "format": fmt, "sample_rate": sample_rate,
            "duration": round(len(samples) / sample_rate, 3)}


def embed_metadata(path: str | Path, metadata: dict[str, Any]) -> dict[str, Any]:
    """Write ID3-ish tags via ffmpeg (safe no-op without ffmpeg)."""
    out = Path(path)
    if not out.exists() or not metadata:
        return {"tags": 0}
    tags: list[str] = []
    mapping = {"title": "title", "artist": "artist", "album": "album",
               "genre": "genre", "comment": "comment"}
    for key, value in metadata.items():
        if key in mapping and value:
            tags += ["-metadata", f"{mapping[key]}={value}"]
    if not tags:
        return {"tags": 0}
    tmp = out.with_suffix(".tagged" + out.suffix)
    cmd = ["ffmpeg", "-y", "-i", str(out), *tags, "-codec", "copy", str(tmp)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode == 0 and tmp.exists():
        tmp.replace(out)
        return {"tags": len(tags) // 2}
    return {"tags": 0}
