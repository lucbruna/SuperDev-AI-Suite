"""Marketing suite endpoints — branding, marketing campaigns and thumbnails.

Exposes the Volume 5 distribution engines (AI Branding, AI Marketing, AI
Thumbnail) over three routers registered under ``/branding``, ``/marketing``
and ``/thumbnails``. Handlers are sync because they run real file + PIL work;
FastAPI executes them in a worker threadpool.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from modules.ai_video_studio.ai_branding.brand_kit import build_brand_kit
from modules.ai_video_studio.ai_branding.seo_engine import generate_seo_metadata
from modules.ai_video_studio.ai_branding.brand_assets import (
    generate_logo_placeholder,
    generate_palette_swatches,
)
from modules.ai_video_studio.ai_marketing.caption_generator import generate_caption
from modules.ai_video_studio.ai_marketing.hashtag_engine import generate_hashtags
from modules.ai_video_studio.ai_marketing.marketing_engine import get_marketing_engine
from modules.ai_video_studio.ai_marketing.poster_engine import generate_poster
from modules.ai_video_studio.ai_thumbnail.thumbnail_engine import get_thumbnail_engine
from modules.ai_video_studio.ai_thumbnail.thumbnail_templates import THUMBNAIL_TEMPLATES

branding_router = APIRouter()
marketing_router = APIRouter()
thumbnails_router = APIRouter()


# ── Branding ────────────────────────────────────────────────────────


class BrandKitRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Brand name")
    colors: list[str] = Field(..., min_length=2, description="Brand palette (#RRGGBB)")
    tagline: str = ""
    tone: str = "professional"
    fonts: list[str] | None = None


class SeoRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Video title")
    topic: str | None = None
    keywords: list[str] | None = None
    platforms: list[str] | None = None
    language: str = "pt"


class SwatchesRequest(BaseModel):
    colors: list[str] = Field(..., min_length=1, description="Brand palette (#RRGGBB)")
    name: str = "palette"
    width: int = Field(640, ge=16, le=4096)
    height: int = Field(80, ge=16, le=4096)


class LogoRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Brand name")
    color: str = "#FFFFFF"
    background: str = "#1F2937"
    width: int = Field(256, ge=16, le=1024)
    height: int = Field(256, ge=16, le=1024)


@branding_router.post("/brand-kit")
def create_brand_kit(body: BrandKitRequest):
    return build_brand_kit(
        body.name, colors=body.colors, tagline=body.tagline,
        tone=body.tone, fonts=body.fonts,
    )


@branding_router.post("/seo")
def create_seo_metadata(body: SeoRequest):
    return generate_seo_metadata(
        body.title, topic=body.topic, keywords=body.keywords,
        platforms=body.platforms, language=body.language,
    )


@branding_router.post("/assets/swatches")
def create_palette_swatches(body: SwatchesRequest):
    return generate_palette_swatches(body.colors, name=body.name, size=(body.width, body.height))


@branding_router.post("/assets/logo")
def create_logo_placeholder(body: LogoRequest):
    return generate_logo_placeholder(
        body.name, color=body.color, background=body.background,
        size=(body.width, body.height),
    )


# ── Marketing ───────────────────────────────────────────────────────


class CampaignRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Video title")
    topic: str | None = None
    keywords: list[str] | None = None
    platforms: list[str] | None = None
    cta: str | None = None
    brand_name: str | None = None
    language: str = "pt"


class CaptionRequest(BaseModel):
    title: str = Field(..., min_length=1)
    platform: str = "instagram"
    topic: str | None = None
    keywords: list[str] | None = None
    hook: str | None = None
    cta: str | None = None
    language: str = "pt"


class HashtagsRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    platform: str = "all"
    count: int = Field(10, ge=1, le=30)
    language: str = "pt"


class PosterRequest(BaseModel):
    title: str = Field(..., min_length=1)
    subtitle: str | None = None
    cta: str | None = None
    colors: tuple[str, str] = ("#111827", "#F59E0B")
    width: int = Field(1080, ge=320, le=4096)
    height: int = Field(1080, ge=320, le=4096)


@marketing_router.post("/campaign")
def create_campaign(body: CampaignRequest):
    return get_marketing_engine().create_campaign(
        body.title, topic=body.topic, keywords=body.keywords,
        platforms=body.platforms, cta=body.cta, brand_name=body.brand_name,
        language=body.language,
    )


@marketing_router.post("/captions")
def create_caption(body: CaptionRequest):
    return generate_caption(
        body.title, platform=body.platform, topic=body.topic,
        keywords=body.keywords, hook=body.hook, cta=body.cta, language=body.language,
    )


@marketing_router.post("/hashtags")
def suggest_hashtags(body: HashtagsRequest):
    return {
        "topic": body.topic,
        "platform": body.platform,
        "hashtags": generate_hashtags(body.topic, platform=body.platform, count=body.count),
    }


@marketing_router.post("/poster")
def create_poster(body: PosterRequest):
    return generate_poster(
        body.title, subtitle=body.subtitle, cta=body.cta,
        colors=body.colors, size=(body.width, body.height),
    )


# ── Thumbnails ──────────────────────────────────────────────────────


class ThumbnailRequest(BaseModel):
    title: str = Field(..., min_length=1)
    template: str = "bold_title"
    width: int = Field(1280, ge=320, le=4096)
    height: int = Field(720, ge=180, le=4096)
    subtitle: str | None = None
    output_path: str | None = None


@thumbnails_router.post("/generate")
def generate_thumbnail(body: ThumbnailRequest):
    return get_thumbnail_engine().generate(
        body.title, template=body.template, size=(body.width, body.height),
        subtitle=body.subtitle, output_path=body.output_path,
    )


@thumbnails_router.get("/templates")
def list_thumbnail_templates():
    return {"templates": THUMBNAIL_TEMPLATES}
