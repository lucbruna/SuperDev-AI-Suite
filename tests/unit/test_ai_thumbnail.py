"""Unit tests for the AI Thumbnail Studio (templates, text helpers, engine)."""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.ai_video_studio.ai_branding.brand_kit import contrast_ratio
from modules.ai_video_studio.ai_thumbnail.thumbnail_engine import get_thumbnail_engine
from modules.ai_video_studio.ai_thumbnail.thumbnail_templates import get_template, list_templates
from modules.ai_video_studio.ai_thumbnail.thumbnail_text import ensure_contrast, split_lines, wrap_text
from modules.ai_video_studio.core.exceptions import ValidationError


def test_wrap_text_breaks_long_text() -> None:
    lines = wrap_text("um dois tres quatro cinco", 10)
    assert all(len(line) <= 10 for line in lines)
    assert len(lines) > 1


def test_split_lines_truncates_with_ellipsis() -> None:
    lines = split_lines("a b c d e f g h i j k l m n o p q r s t u", max_lines=3, max_chars=8)
    assert len(lines) == 3
    assert lines[-1].endswith("…")


def test_unknown_template_raises() -> None:
    with pytest.raises(ValidationError):
        get_template("nonexistent")


def test_list_templates() -> None:
    names = list_templates()
    assert "bold_title" in names
    assert len(names) >= 3


def test_ensure_contrast_keeps_ok_color() -> None:
    assert ensure_contrast("#FFFFFF", "#111827") == "#ffffff"


def test_ensure_contrast_reaches_ratio() -> None:
    result = ensure_contrast("#F59E0B", "#F59E0B", min_ratio=4.5)
    assert contrast_ratio(result, "#F59E0B") >= 4.5


def test_generate_thumbnail_png() -> None:
    result = get_thumbnail_engine().generate("Titulo Incrivel do Video", template="bold_title")
    out = Path(result["output_path"])
    assert out.exists() and out.suffix == ".png"
    assert result["width"] == 1280
    assert result["height"] == 720


def test_generate_thumbnail_custom_size() -> None:
    result = get_thumbnail_engine().generate("Mini", template="split_frame", size=(960, 540))
    assert result["width"] == 960
    assert result["height"] == 540


def test_generate_thumbnail_rejects_small_size() -> None:
    with pytest.raises(ValidationError):
        get_thumbnail_engine().generate("Mini", size=(100, 100))


def test_generate_thumbnail_rejects_empty_title() -> None:
    with pytest.raises(ValidationError):
        get_thumbnail_engine().generate("   ")
