"""Frame-based visual diagnostics for encoded DARKSTUDIO MP4 files.

Uses FFmpeg for bounded frame sampling and Pillow/NumPy for lightweight
perceptual diagnostics. Metrics are visual-change proxies, not semantic CV.
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, ImageStat


def _probe_duration(path: Path, timeout: int) -> float:
    binary = shutil.which("ffprobe")
    if not binary:
        raise RuntimeError("ffprobe is required for MP4 visual analysis")
    result = subprocess.run(
        [binary, "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=timeout, check=False,
    )
    if result.returncode:
        raise RuntimeError("ffprobe could not read the video")
    try:
        duration = float(json.loads(result.stdout)["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("ffprobe returned an invalid video duration") from exc
    if not math.isfinite(duration) or duration <= 0:
        raise RuntimeError("video duration must be positive")
    return duration


def _dhash(image: Image.Image) -> int:
    pixels = np.asarray(image.convert("L").resize((9, 8), Image.Resampling.LANCZOS))
    bits = pixels[:, 1:] > pixels[:, :-1]
    value = 0
    for bit in bits.flatten():
        value = (value << 1) | int(bit)
    return value


def _hash_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def _frame_descriptor(image: Image.Image) -> dict[str, Any]:
    rgb = image.convert("RGB").resize((160, 90), Image.Resampling.BILINEAR)
    gray = rgb.convert("L")
    arr = np.asarray(rgb, dtype=np.float32)
    gray_arr = np.asarray(gray, dtype=np.float32)
    histograms = []
    for channel in range(3):
        hist, _ = np.histogram(arr[:, :, channel], bins=16, range=(0, 256), density=True)
        histograms.append(hist.astype(np.float32))
    histogram = np.concatenate(histograms)
    histogram /= max(float(np.linalg.norm(histogram)), 1e-9)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_arr = np.asarray(edges, dtype=np.float32)
    edge_density = float(np.mean(edge_arr > 24))
    grid = []
    for row in range(4):
        for col in range(4):
            cell = gray_arr[row * 22:(row + 1) * 22, col * 40:(col + 1) * 40]
            grid.append(float(cell.mean() / 255.0))
    return {
        "hash": _dhash(rgb),
        "histogram": histogram,
        "edge_density": edge_density,
        "grid_luminance": np.asarray(grid, dtype=np.float32),
    }


def analyze_frame_sequence(
    frames: list[Image.Image],
    *,
    sample_times: list[float] | None = None,
    timeline: dict[str, Any] | None = None,
    static_threshold: float = 1.5,
    duplicate_threshold: float = 2.0,
) -> dict[str, Any]:
    """Analyze already-decoded frames; useful for deterministic unit tests."""
    if not frames:
        raise ValueError("at least one decoded frame is required")
    if static_threshold < 0 or duplicate_threshold < 0:
        raise ValueError("visual thresholds cannot be negative")
    if sample_times is None:
        sample_times = [float(index) for index in range(len(frames))]
    if len(sample_times) != len(frames):
        raise ValueError("sample_times must match the number of frames")
    descriptors = [_frame_descriptor(frame) for frame in frames]
    clips = []
    if timeline:
        for track in timeline.get("tracks") or []:
            if track.get("type") == "video":
                clips = track.get("clips") or []
                break

    comparisons = []
    duplicate_pairs = []
    static_pairs = []
    for index in range(1, len(frames)):
        previous = np.asarray(frames[index - 1].convert("RGB").resize((160, 90)), dtype=np.float32)
        current = np.asarray(frames[index].convert("RGB").resize((160, 90)), dtype=np.float32)
        mae = float(np.mean(np.abs(current - previous)))
        hash_distance = _hash_distance(descriptors[index - 1]["hash"], descriptors[index]["hash"])
        histogram_similarity = float(np.dot(descriptors[index - 1]["histogram"], descriptors[index]["histogram"]))
        grid_shift = float(np.mean(np.abs(
            descriptors[index]["grid_luminance"] - descriptors[index - 1]["grid_luminance"]
        )))
        repeated = hash_distance <= 2 and mae <= duplicate_threshold
        static = mae <= static_threshold
        row = {
            "from_sample": index - 1,
            "to_sample": index,
            "from_seconds": round(float(sample_times[index - 1]), 3),
            "to_seconds": round(float(sample_times[index]), 3),
            "mean_pixel_change": round(mae, 3),
            "perceptual_hash_distance": hash_distance,
            "color_histogram_similarity": round(histogram_similarity, 4),
            "composition_grid_change": round(grid_shift, 4),
            "repeated_frame": repeated,
            "low_visual_change": static,
        }
        comparisons.append(row)
        if repeated:
            duplicate_pairs.append(row)
        if static:
            static_pairs.append(row)

    scene_summaries = []
    for clip in clips:
        start = float(clip.get("start_seconds", 0))
        end = float(clip.get("end_seconds", 0))
        selected = [
            comparisons[i] for i in range(len(comparisons))
            if start <= comparisons[i]["to_seconds"] <= end
        ]
        scene_summaries.append({
            "scene_index": int(clip.get("scene_index", len(scene_summaries))),
            "start_seconds": round(start, 3),
            "end_seconds": round(end, 3),
            "sampled_comparisons": len(selected),
            "mean_pixel_change": round(
                sum(item["mean_pixel_change"] for item in selected) / len(selected), 3
            ) if selected else None,
            "repeated_frame_pairs": sum(item["repeated_frame"] for item in selected),
            "low_change_pairs": sum(item["low_visual_change"] for item in selected),
        })

    # A run is reported only when at least two consecutive sampled comparisons
    # remain below the static threshold; a single near-identical pair is noise.
    static_runs = []
    run_start = None
    for index, item in enumerate(comparisons):
        if item["low_visual_change"]:
            if run_start is None:
                run_start = index
        elif run_start is not None:
            if index - run_start >= 2:
                static_runs.append({
                    "start_seconds": comparisons[run_start]["from_seconds"],
                    "end_seconds": comparisons[index - 1]["to_seconds"],
                    "comparison_count": index - run_start,
                })
            run_start = None
    if run_start is not None and len(comparisons) - run_start >= 2:
        static_runs.append({
            "start_seconds": comparisons[run_start]["from_seconds"],
            "end_seconds": comparisons[-1]["to_seconds"],
            "comparison_count": len(comparisons) - run_start,
        })

    warnings = []
    if duplicate_pairs:
        warnings.append({"code": "near_duplicate_sampled_frames", "count": len(duplicate_pairs)})
    if static_runs:
        warnings.append({"code": "sustained_low_visual_change", "count": len(static_runs)})
    if len(frames) < 3:
        warnings.append({"code": "limited_frame_sample", "count": len(frames)})
    return {
        "status": "needs_review" if warnings else "no_obvious_issue",
        "sample_count": len(frames),
        "comparison_count": len(comparisons),
        "duplicate_pair_count": len(duplicate_pairs),
        "low_change_pair_count": len(static_pairs),
        "static_runs": static_runs,
        "scene_summaries": scene_summaries,
        "comparisons": comparisons,
        "warnings": warnings,
        "analysis_method": "ffmpeg_sampled_frames_pillow_numpy",
        "limitations": [
            "A amostragem pode não capturar problemas que ocorram entre os frames selecionados.",
            "Mudança de pixels não distingue movimento de câmera, movimento de objeto ou ruído de compressão.",
            "Não reconhece personagens, rostos, objetos ou semântica; não comprova continuidade de Mia e Leo.",
            "A métrica de composição é uma comparação simples de luminância em grade 4x4, não uma avaliação artística.",
        ],
    }


def analyze_mp4_visuals(
    video_path: str | Path,
    *,
    timeline: dict[str, Any] | None = None,
    max_frames: int = 48,
    timeout: int = 180,
) -> dict[str, Any]:
    """Sample an encoded MP4 at up to max_frames and report visual change."""
    path = Path(video_path)
    if not path.is_file() or path.suffix.lower() != ".mp4":
        raise ValueError("visual analysis requires an existing MP4 file")
    if max_frames < 3 or max_frames > 120:
        raise ValueError("max_frames must be between 3 and 120")
    if timeout < 1:
        raise ValueError("timeout must be positive")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for MP4 visual analysis")
    duration = _probe_duration(path, timeout)
    sample_rate = min(4.0, max_frames / duration)
    with tempfile.TemporaryDirectory(prefix="darkstudio-visual-") as tmp:
        pattern = str(Path(tmp) / "frame-%04d.jpg")
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(path),
             "-vf", f"fps={sample_rate:.8f},scale=160:90:force_original_aspect_ratio=decrease,pad=160:90:(ow-iw)/2:(oh-ih)/2",
             "-frames:v", str(max_frames), "-q:v", "3", pattern],
            capture_output=True, text=True, timeout=timeout, check=False,
        )
        if result.returncode:
            raise RuntimeError("FFmpeg could not extract analysis frames")
        frame_paths = sorted(Path(tmp).glob("frame-*.jpg"))
        frames = [Image.open(item).convert("RGB") for item in frame_paths]
        try:
            times = [index / sample_rate for index in range(len(frames))]
            report = analyze_frame_sequence(frames, sample_times=times, timeline=timeline)
        finally:
            for frame in frames:
                frame.close()
    if not report["sample_count"]:
        raise RuntimeError("FFmpeg did not produce any analysis frames")
    report.update({
        "video_duration_seconds": round(duration, 3),
        "sample_interval_seconds": round(1 / sample_rate, 3),
        "video_file_bytes": path.stat().st_size,
        "max_frames": max_frames,
    })
    return report
