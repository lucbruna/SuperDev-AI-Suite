from __future__ import annotations

from backend.schemas.base import BaseSchema
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    """Request to log in with email and password."""

    email: str = Field(..., min_length=5, max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower().strip()


class RegisterRequest(BaseModel):
    """Request to register a new user account."""

    email: str = Field(..., min_length=5, max_length=255, description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    full_name: str | None = Field(None, max_length=255, description="Full display name")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email address")
        return v.lower().strip()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        import re

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username must contain only letters, numbers, underscores, and hyphens")
        return v.strip()


class RefreshRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str = Field(..., min_length=10, description="Valid refresh token")


class TokenResponse(BaseSchema):
    """JWT token pair returned after authentication."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token lifetime in seconds")


class LoginResponse(BaseSchema):
    """Successful login response with user info and tokens."""

    user: dict = Field(..., description="Authenticated user details")
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    expires_in: int = Field(..., alias="expiresIn")

    model_config = {"from_attributes": True, "populate_by_name": True}


class MFASetupResponse(BaseSchema):
    """MFA setup response with OTP auth URL and secret."""

    otpauth_url: str = Field(..., description="OTP auth URL for QR code generation")
    secret: str = Field(..., description="MFA secret key")


class MFAVerifyRequest(BaseModel):
    """Request to verify an MFA code."""

    code: str = Field(..., min_length=6, max_length=6, description="6-digit MFA code")
