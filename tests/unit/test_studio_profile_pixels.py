"""Pixel-level regression tests for DARKSTUDIO's two visual identities."""
from __future__ import annotations

import numpy as np

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.studio_profiles import apply_studio_profile


def test_studio_profiles_produce_distinct_rendered_pixels() -> None:
    """The selected studio must change actual frames, not only API metadata."""
    canvas = SceneCanvas(width=96, height=54, fps=1, seed=7)
    base_scene = {"text": None, "rects": [], "circles": [], "lines": [], "particles": []}

    whymentary_scene = apply_studio_profile("whymentary", base_scene)
    historical_scene = apply_studio_profile("historical_documentary", base_scene)

    whymentary_frame = canvas.render_scene(whymentary_scene, 0)
    historical_frame = canvas.render_scene(historical_scene, 0)

    assert whymentary_frame.shape == (54, 96, 3)
    assert historical_frame.shape == (54, 96, 3)
    # Whymentary's contract is a clean, ungraded white canvas.
    assert np.all(whymentary_frame == 255)
    # Historical Documentary must render its darker multi-stop environment.
    assert float(historical_frame.mean()) < 100.0
    # Guard against accidental profile collapse to identical pixel output.
    assert not np.array_equal(whymentary_frame, historical_frame)
