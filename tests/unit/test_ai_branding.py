"""Unit tests for the AI Branding Studio (brand kits, SEO, brand assets)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from modules.ai_video_studio.ai_branding.brand_kit import (
    build_brand_kit,
    contrast_ratio,
    validate_hex,
)
from modules.ai_video_studio.ai_branding.seo_engine import generate_seo_metadata
from modules.ai_video_studio.ai_branding.brand_assets import (
    generate_logo_placeholder,
    generate_palette_swatches,
)
from modules.ai_video_studio.core.exceptions import ValidationError


def test_validate_hex_normalizes() -> None:
    assert validate_hex("#FFFFFF") == "#ffffff"
    with pytest.raises(ValidationError):
        validate_hex("white")
    with pytest.raises(ValidationError):
        validate_hex("#GGGGGG")


def test_contrast_ratio_bounds() -> None:
    assert contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0, abs=0.05)
    assert contrast_ratio("#FFFFFF", "#FFFFFF") == pytest.approx(1.0)


def test_build_brand_kit_writes_json() -> None:
    result = build_brand_kit("Aurora", colors=["#111827", "#F59E0B", "#FFFFFF"])
    out = Path(result["output_path"])
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["name"] == "Aurora"
    assert "#f59e0b" in data["colors"]
    assert "#f59e0b_on_#111827" in data["contrast"]
    assert result["output_bytes"] > 0


def test_build_brand_kit_requires_two_colors() -> None:
    with pytest.raises(ValidationError):
        build_brand_kit("X", colors=["#111111"])


def test_build_brand_kit_rejects_bad_tone() -> None:
    with pytest.raises(ValidationError):
        build_brand_kit("X", colors=["#111111", "#222222"], tone="loud")


def test_seo_metadata_respects_platform_limits() -> None:
    result = generate_seo_metadata(
        "Tutorial Completo de Edição de Vídeo Profissional",
        topic="edição de vídeo",
        keywords=["edição", "vídeo", "tutorial"],
        platforms=["youtube", "x"],
    )
    assert len(result["platforms"]["youtube"]["title"]) <= 100
    assert len(result["platforms"]["x"]["title"]) <= 60
    assert result["platforms"]["youtube"]["tags"] == []
    assert result["platforms"]["x"]["tags"]
    out = Path(result["output_path"])
    assert out.exists()


def test_seo_metadata_rejects_unknown_platform() -> None:
    with pytest.raises(ValidationError):
        generate_seo_metadata("T", platforms=["myspace"])


def test_seo_metadata_rejects_bad_language() -> None:
    with pytest.raises(ValidationError):
        generate_seo_metadata("T", language="zz")


def test_palette_swatches_png() -> None:
    result = generate_palette_swatches(["#111827", "#F59E0B"], name="teste")
    out = Path(result["output_path"])
    assert out.exists() and out.suffix == ".png"
    assert result["width"] == 640


def test_logo_placeholder_png() -> None:
    result = generate_logo_placeholder("Aurora")
    out = Path(result["output_path"])
    assert out.exists() and out.suffix == ".png"
    assert result["letter"] == "A"
