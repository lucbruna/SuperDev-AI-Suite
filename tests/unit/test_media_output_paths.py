"""Unit tests for media output paths and path safety helpers.

Covers the canonical downloads layout, collision-free unique filenames, and
the ``safe_clone_id`` whitelist that blocks path traversal.
"""
from __future__ import annotations

import pytest

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import (
    DOWNLOADS_DIR,
    get_downloads_dir,
    get_subsystem_dir,
    media_path,
    unique_filename,
)
from modules.ai_video_studio.ai_voice_clone.speaker_embeddings import SpeakerEmbeddings, safe_clone_id


def test_downloads_dir_under_project(tmp_path) -> None:
    assert get_downloads_dir().exists()
    # The canonical root is <project>/modules/downloads
    assert str(DOWNLOADS_DIR).replace("\\", "/").endswith("modules/downloads")


def test_subsystem_dirs_created() -> None:
    for kind in ("voice", "music", "effects", "mix", "clones", "subtitles", "dubbing"):
        d = get_subsystem_dir(kind)
        assert d.exists()
        assert d.is_dir()


def test_media_path_nesting() -> None:
    p = media_path("voice", "demo.wav")
    assert p.name == "demo.wav"
    assert p.parent == get_subsystem_dir("voice")


def test_unique_filename_no_collision(tmp_path) -> None:
    first = unique_filename(tmp_path, "clip", "wav")
    first.touch()  # occupy the name so the next call must increment
    second = unique_filename(tmp_path, "clip", "wav")
    assert first != second
    assert first.suffix == ".wav"
    assert second.name.startswith("clip_")
    assert second.name.endswith(".wav")


def test_unique_filename_increments_after_creation(tmp_path) -> None:
    a = unique_filename(tmp_path, "clip", "wav")
    a.touch()
    b = unique_filename(tmp_path, "clip", "wav")
    assert b != a


# ── safe_clone_id — path traversal guard ─────────────────────────────


@pytest.mark.parametrize(
    "bad",
    ["../evil", "..%2fevil", "a/b", "a\\b", "C:\\evil", "..", ".", "", "a..b/../x"],
)
def test_safe_clone_id_rejects_traversal(bad: str) -> None:
    with pytest.raises(ValidationError):
        safe_clone_id(bad)


@pytest.mark.parametrize("good", ["clone_123", "Ana-2_x", "voiceref", "a-b_c9"])
def test_safe_clone_id_accepts_valid(good: str) -> None:
    assert safe_clone_id(good) == good


def test_speaker_embeddings_rejects_bad_id(tmp_path) -> None:
    se = SpeakerEmbeddings(root=tmp_path)
    with pytest.raises(ValidationError):
        se.profile_dir("../escape")


def test_speaker_embeddings_roundtrip(tmp_path) -> None:

    import numpy as np

    se = SpeakerEmbeddings(root=tmp_path)
    directory = se.save("voice_a", np.zeros(8, dtype=np.float32), {"name": "A"})
    assert directory == tmp_path / "voice_a"
    emb = se.load_embedding("voice_a")
    assert emb is not None and emb.shape == (8,)
    meta = se.load_metadata("voice_a")
    assert meta["name"] == "A"
    assert len(se.list()) == 1
    assert se.delete("voice_a") is True
    assert se.delete("voice_a") is False
