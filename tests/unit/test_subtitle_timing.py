"""Subtitle timeline regression tests."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService, cues_for_scene


def test_short_scene_subtitle_cues_never_exceed_scene_duration():
    cues = cues_for_scene(
        "Uma frase longa que precisa ser dividida em várias legendas curtas "
        "para permanecer legível durante a cena.",
        duration=1.2,
        start_offset=4.0,
        max_chars=24,
    )
    assert len(cues) > 1
    assert cues[0].start == pytest.approx(4.0)
    assert cues[-1].end == pytest.approx(5.2)
    assert all(cue.start >= 4.0 and cue.end <= 5.2 for cue in cues)
    assert all(cues[i].end == pytest.approx(cues[i + 1].start) for i in range(len(cues) - 1))


def test_zero_duration_scene_has_no_subtitle_cues():
    assert cues_for_scene("Texto de teste", duration=0.0) == []


def test_srt_service_respects_explicit_scene_start_offsets(tmp_path):
    output = tmp_path / "offsets.srt"
    result = SubtitleStudioService().generate_srt(
        [
            {"text": "Primeira cena.", "duration": 2.0, "start_offset": 0.0},
            {"text": "Segunda cena.", "duration": 1.0, "start_offset": 1.5},
        ],
        output_path=str(output),
    )
    srt = output.read_text(encoding="utf-8")
    assert "00:00:01,500 --> 00:00:02,500" in srt
    assert result["duration"] == pytest.approx(2.5)
