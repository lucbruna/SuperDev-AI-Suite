"""Unit tests for the AI Marketing Studio (captions, hashtags, campaigns, posters)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from modules.ai_video_studio.ai_marketing.caption_generator import generate_caption
from modules.ai_video_studio.ai_marketing.hashtag_engine import generate_hashtags
from modules.ai_video_studio.ai_marketing.marketing_engine import get_marketing_engine
from modules.ai_video_studio.ai_marketing.poster_engine import generate_poster
from modules.ai_video_studio.core.exceptions import ValidationError


def test_caption_x_within_limit() -> None:
    result = generate_caption(
        "Vídeo demo", platform="x", topic="edição", keywords=["vídeo", "tutorial"]
    )
    assert result["platform"] == "x"
    assert len(result["caption"]) <= result["character_limit"]


def test_caption_unknown_platform_raises() -> None:
    with pytest.raises(ValidationError):
        generate_caption("Vídeo demo", platform="myspace")


def test_caption_instagram_has_hashtags() -> None:
    result = generate_caption("Vídeo demo", platform="instagram", keywords=["edição"])
    assert "#" in result["caption"]


def test_hashtags_deduplicated_and_prefixed() -> None:
    tags = generate_hashtags("edição de vídeo tutorial", count=8)
    assert len(tags) == 8
    assert all(tag.startswith("#") for tag in tags)
    assert len(set(tags)) == len(tags)


def test_hashtags_reject_bad_platform() -> None:
    with pytest.raises(ValidationError):
        generate_hashtags("topic", platform="nope")


def test_create_campaign_writes_json() -> None:
    result = get_marketing_engine().create_campaign(
        "Vídeo demo", topic="edição", keywords=["vídeo"]
    )
    assert set(result["captions"]) == {"youtube", "instagram", "tiktok", "x", "linkedin"}
    assert result["hashtags"]
    out = Path(result["output_path"])
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["title"] == "Vídeo demo"
    assert len(data["content_ideas"]) >= 3


def test_create_campaign_restricted_platforms() -> None:
    result = get_marketing_engine().create_campaign("Vídeo demo", platforms=["instagram", "x"])
    assert set(result["captions"]) == {"instagram", "x"}


def test_poster_png() -> None:
    result = generate_poster("Vídeo Demo", subtitle="Assista agora", cta="Saiba mais")
    out = Path(result["output_path"])
    assert out.exists() and out.suffix == ".png"
    assert result["width"] == 1080
    assert result["height"] == 1080
