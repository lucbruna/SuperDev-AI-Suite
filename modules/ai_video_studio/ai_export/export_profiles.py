"""Export profiles — container/codec/bitrate definitions for each target."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ExportProfile:
    """A concrete encoder configuration for an export target."""

    name: str
    container: str
    video_codec: str
    audio_codec: str
    video_bitrate: str
    audio_bitrate: str = "192k"
    fps: int = 30
    max_resolution: tuple[int, int] | None = None  # (W, H) cap, None = unlimited
    pixel_format: str = "yuv420p"
    extra_args: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)


MP4_H264 = ExportProfile(
    name="mp4_h264",
    container="mp4",
    video_codec="libx264",
    audio_codec="aac",
    video_bitrate="8M",
    extra_args=("-preset", "medium", "-crf", "18"),
    meta={"quality": "high", "faststart": True},
)

MP4_H265 = ExportProfile(
    name="mp4_h265",
    container="mp4",
    video_codec="libx265",
    audio_codec="aac",
    video_bitrate="5M",
    extra_args=("-preset", "medium", "-crf", "20"),
    meta={"quality": "high", "hdr_capable": True},
)

MOV_PRORES = ExportProfile(
    name="mov_prores",
    container="mov",
    video_codec="prores_ks",
    audio_codec="pcm_s16le",
    video_bitrate="200M",
    pixel_format="yuv422p10le",
    extra_args=("-profile:v", "3"),
    meta={"quality": "master", "editing": True},
)

MKV_H264 = ExportProfile(
    name="mkv_h264",
    container="matroska",
    video_codec="libx264",
    audio_codec="aac",
    video_bitrate="8M",
    extra_args=("-preset", "medium", "-crf", "18"),
)

AVI_DV = ExportProfile(
    name="avi_dv",
    container="avi",
    video_codec="dvvideo",
    audio_codec="pcm_s16le",
    video_bitrate="25M",
    fps=25,
    meta={"legacy": True},
)

WEBM_VP9 = ExportProfile(
    name="webm_vp9",
    container="webm",
    video_codec="libvpx-vp9",
    audio_codec="libopus",
    video_bitrate="6M",
    extra_args=("-crf", "32", "-b:v", "0"),
    meta={"web": True},
)

GIF = ExportProfile(
    name="gif",
    container="gif",
    video_codec="gif",
    audio_codec="none",
    video_bitrate="0",
    fps=15,
    meta={"lossy": True, "no_audio": True},
)

IMAGE_SEQUENCE = ExportProfile(
    name="image_sequence",
    container="image2",
    video_codec="png",
    audio_codec="none",
    video_bitrate="0",
    meta={"lossless": True, "no_audio": True},
)

PROFILES: dict[str, ExportProfile] = {
    p.name: p
    for p in (
        MP4_H264,
        MP4_H265,
        MOV_PRORES,
        MKV_H264,
        AVI_DV,
        WEBM_VP9,
        GIF,
        IMAGE_SEQUENCE,
    )
}


def get_profile(name: str) -> ExportProfile:
    """Look up an export profile by name, with alias handling."""
    alias = {
        "mp4": "mp4_h264",
        "mov": "mov_prores",
        "mkv": "mkv_h264",
        "avi": "avi_dv",
        "webm": "webm_vp9",
        "image2": "image_sequence",
    }
    key = alias.get(name, name)
    if key not in PROFILES:
        raise KeyError(f"unknown export profile {name!r}; available: {sorted(PROFILES)}")
    return PROFILES[key]
