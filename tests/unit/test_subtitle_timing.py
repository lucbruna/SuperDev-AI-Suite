"""Subtitle timeline regression tests."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.services.subtitle_studio import cues_for_scene


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
