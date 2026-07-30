from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from backend.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """Base user fields shared across request/response schemas."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str | None = Field(None, max_length=255, description="Full display name")
    avatar_url: str | None = Field(None, max_length=500, description="Profile avatar URL")
    is_active: bool = Field(True, description="Whether the account is active")
    is_superuser: bool = Field(False, description="Whether the user has superuser privileges")
    is_verified: bool = Field(False, description="Whether the email is verified")
    mfa_enabled: bool = Field(False, description="Whether MFA is enabled")
    last_login: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime | None = Field(None, description="Account creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class UserCreate(BaseModel):
    """Request to create a new user."""

    email: EmailStr = Field(..., min_length=5, max_length=255, description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str | None = Field(None, max_length=255, description="Full display name")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v.strip()


class UserUpdate(BaseModel):
    """Request to update user profile fields."""

    email: EmailStr | None = Field(None, description="New email address")
    username: str | None = Field(None, min_length=3, max_length=50, description="New username")
    full_name: str | None = Field(None, max_length=255, description="New full name")
    avatar_url: str | None = Field(None, max_length=500, description="New avatar URL")


class UserResponse(BaseSchema):
    """Full user response with all profile fields."""

    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: str | None = Field(None, description="Full display name")
    avatar_url: str | None = Field(None, description="Profile avatar URL")
    is_active: bool = Field(True, description="Whether the account is active")
    is_superuser: bool = Field(False, description="Whether the user has superuser privileges")
    is_verified: bool = Field(False, description="Whether the email is verified")
    mfa_enabled: bool = Field(False, description="Whether MFA is enabled")
    last_login: datetime | None = Field(None, description="Last login timestamp")
    created_at: datetime | None = Field(None, description="Account creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")


class UserListItem(BaseSchema):
    """Compact user representation for list endpoints."""

    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., description="Unique username")
    full_name: str | None = Field(None, description="Full display name")
    avatar_url: str | None = Field(None, description="Profile avatar URL")
    is_active: bool = Field(True, description="Whether the account is active")
    created_at: datetime | None = Field(None, description="Account creation timestamp")
