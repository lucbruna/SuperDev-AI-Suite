from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.base import BaseSchema


class ProviderBase(BaseSchema):
    """Base provider fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Provider display name")
    type: str = Field(..., description="Provider type: openai, anthropic, gemini, ollama, openrouter, azure, cohere")
    config: dict = Field(..., description="Provider configuration JSON (API keys, endpoints, etc.)")
    models: list[str] = Field(default_factory=list, description="Available model identifiers")
    is_default: bool = Field(False, description="Whether this is the default provider")
    priority: int = Field(0, description="Priority for provider selection (higher = preferred)")


class ProviderCreate(BaseModel):
    """Request to create a new provider configuration."""

    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., min_length=1, max_length=100, description="Provider name")
    type: str = Field(..., description="Provider type")
    config: dict = Field(..., description="Provider configuration")
    models: list[str] = Field(default_factory=list, description="Available models")
    is_default: bool = Field(False, description="Set as default provider")
    priority: int = Field(0, description="Provider priority")


class ProviderUpdate(BaseModel):
    """Request to update provider fields."""

    name: str | None = Field(None, min_length=1, max_length=100, description="Provider name")
    config: dict | None = Field(None, description="Provider configuration")
    models: list[str] | None = Field(None, description="Available models")
    is_default: bool | None = Field(None, description="Default provider flag")
    is_active: bool | None = Field(None, description="Active flag")
    priority: int | None = Field(None, description="Provider priority")


class ProviderResponse(BaseSchema):
    """Full provider response."""

    id: str = Field(..., description="Provider UUID")
    project_id: str = Field(..., description="Project UUID")
    name: str = Field(..., description="Provider name")
    type: str = Field(..., description="Provider type")
    config: dict = Field(..., description="Provider configuration")
    models: list[str] = Field(default_factory=list, description="Available models")
    is_default: bool = Field(False, description="Whether default")
    is_active: bool = Field(True, description="Whether active")
    priority: int = Field(0, description="Provider priority")
    created_by: str = Field(..., description="Creator user UUID")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
