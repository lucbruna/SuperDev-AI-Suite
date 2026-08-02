"""Video Studio settings using Pydantic BaseSettings.

All settings are loaded from environment variables with VIDEO_STUDIO_ prefix.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


def _default_db_url() -> str:
    """Resolve the database URL from the backend config when available."""
    try:
        from backend.config import config

        return config.database.url
    except Exception:
        return "postgresql+asyncpg://superdev:superdev@localhost:5432/superdev"


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = Field(
        default_factory=_default_db_url,
        alias="VIDEO_STUDIO_DB_URL",
    )
    pool_size: int = Field(default=20, alias="VIDEO_STUDIO_DB_POOL_SIZE")
    max_overflow: int = Field(default=40, alias="VIDEO_STUDIO_DB_MAX_OVERFLOW")
    echo: bool = Field(default=False, alias="VIDEO_STUDIO_DB_ECHO")

    model_config = {"env_prefix": "", "extra": "ignore"}


class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(
        default="redis://localhost:6379/0",
        alias="VIDEO_STUDIO_REDIS_URL",
    )
    max_connections: int = Field(default=50, alias="VIDEO_STUDIO_REDIS_POOL")

    model_config = {"env_prefix": "", "extra": "ignore"}


class StorageSettings(BaseSettings):
    """File storage configuration."""
    local_path: Path = Field(
        default=Path("storage/video_studio"),
        alias="VIDEO_STUDIO_STORAGE_PATH",
    )
    max_upload_size_mb: int = Field(default=5000, alias="VIDEO_STUDIO_MAX_UPLOAD_MB")
    temp_path: Path = Field(
        default=Path("storage/video_studio/temp"),
        alias="VIDEO_STUDIO_TEMP_PATH",
    )
    export_path: Path = Field(
        default=Path("storage/video_studio/exports"),
        alias="VIDEO_STUDIO_EXPORT_PATH",
    )
    asset_path: Path = Field(
        default=Path("storage/video_studio/assets"),
        alias="VIDEO_STUDIO_ASSET_PATH",
    )

    model_config = {"env_prefix": "", "extra": "ignore"}

    def ensure_dirs(self) -> None:
        """Create all storage directories if they don't exist."""
        for p in [self.local_path, self.temp_path, self.export_path, self.asset_path]:
            p.mkdir(parents=True, exist_ok=True)


class RenderSettings(BaseSettings):
    """Render engine configuration."""
    ffmpeg_path: str = Field(default="ffmpeg", alias="VIDEO_STUDIO_FFMPEG")
    ffprobe_path: str = Field(default="ffprobe", alias="VIDEO_STUDIO_FFPROBE")
    max_concurrent_renders: int = Field(default=4, alias="VIDEO_STUDIO_MAX_RENDERS")
    gpu_enabled: bool = Field(default=False, alias="VIDEO_STUDIO_GPU_ENABLED")
    gpu_device: str = Field(default="0", alias="VIDEO_STUDIO_GPU_DEVICE")
    temp_render_path: Path = Field(
        default=Path("storage/video_studio/render_temp"),
        alias="VIDEO_STUDIO_RENDER_TEMP",
    )
    chunk_size: int = Field(default=100, alias="VIDEO_STUDIO_CHUNK_SIZE")
    preview_enabled: bool = Field(default=True, alias="VIDEO_STUDIO_PREVIEW")

    model_config = {"env_prefix": "", "extra": "ignore"}


class AISettings(BaseSettings):
    """AI engine configuration."""
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=4096, alias="OPENAI_MAX_TOKENS")
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")
    stability_api_key: str = Field(default="", alias="STABILITY_API_KEY")
    elevenlabs_api_key: str = Field(default="", alias="ELEVENLABS_API_KEY")
    fal_api_key: str = Field(default="", alias="FAL_API_KEY")
    provider: str = Field(default="ollama", alias="VIDEO_STUDIO_AI_PROVIDER")
    temperature: float = Field(default=0.7, alias="VIDEO_STUDIO_AI_TEMPERATURE")
    max_retries: int = Field(default=3, alias="VIDEO_STUDIO_AI_RETRIES")

    model_config = {"env_prefix": "", "extra": "ignore"}


class PublisherSettings(BaseSettings):
    """Publisher configuration."""
    youtube_client_id: str = Field(default="", alias="YOUTUBE_CLIENT_ID")
    youtube_client_secret: str = Field(default="", alias="YOUTUBE_CLIENT_SECRET")
    tiktok_access_token: str = Field(default="", alias="TIKTOK_ACCESS_TOKEN")
    instagram_access_token: str = Field(default="", alias="INSTAGRAM_ACCESS_TOKEN")
    facebook_access_token: str = Field(default="", alias="FACEBOOK_ACCESS_TOKEN")
    linkedin_access_token: str = Field(default="", alias="LINKEDIN_ACCESS_TOKEN")
    s3_bucket: str = Field(default="", alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_access_key: str = Field(default="", alias="S3_ACCESS_KEY")
    s3_secret_key: str = Field(default="", alias="S3_SECRET_KEY")

    model_config = {"env_prefix": "", "extra": "ignore"}


class VideoStudioSettings(BaseSettings):
    """Main settings container for the video studio."""
    app_name: str = "AI Video Studio"
    version: str = "1.0.0"
    debug: bool = Field(default=False, alias="VIDEO_STUDIO_DEBUG")
    host: str = Field(default="0.0.0.0", alias="VIDEO_STUDIO_HOST")
    port: int = Field(default=8000, alias="VIDEO_STUDIO_PORT")
    workers: int = Field(default=1, alias="VIDEO_STUDIO_WORKERS")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        alias="VIDEO_STUDIO_CORS",
    )

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    storage: StorageSettings = StorageSettings()
    render: RenderSettings = RenderSettings()
    ai: AISettings = AISettings()
    publisher: PublisherSettings = PublisherSettings()

    model_config = {"env_prefix": "", "extra": "ignore", "env_file": ".env"}

    def initialize(self) -> VideoStudioSettings:
        """Initialize all subsystems."""
        self.storage.ensure_dirs()
        self.render.temp_render_path.mkdir(parents=True, exist_ok=True)
        return self


@lru_cache
def get_settings() -> VideoStudioSettings:
    """Get cached singleton settings instance."""
    return VideoStudioSettings().initialize()
