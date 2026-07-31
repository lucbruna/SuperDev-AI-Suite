"""API Key management routes — CRUD with expiry support.

Endpoints:
- POST   /api/v1/api-keys        — create new API key
- GET    /api/v1/api-keys        — list API keys
- GET    /api/v1/api-keys/{id}   — get API key details
- DELETE /api/v1/api-keys/{id}   — revoke (soft-delete) API key
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user

router = APIRouter()


# ------------------------------------------------------------------
# Request / Response models
# ------------------------------------------------------------------


class APIKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(
        default=None,
        description="Number of days until the key expires. None = never.",
        ge=1,
        le=3650,
    )


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    expires_at: str | None
    last_used_at: str | None
    created_at: str
    is_active: bool


class APIKeyCreateResponse(BaseModel):
    id: str
    name: str
    key: str  # Only returned on creation — the raw secret
    key_prefix: str
    scopes: list[str]
    expires_at: str | None
    created_at: str


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

_PREFIX_LENGTH = 8
_KEY_BYTES = 32


def _generate_api_key() -> tuple[str, str, str]:
    """Return (raw_key, key_hash, key_prefix).

    The raw key is ``sk_`` + random hex.
    The prefix is the first ``_PREFIX_LENGTH`` chars after ``sk_``.
    The hash is SHA-256 of the raw key for storage.
    """
    raw = "sk_" + secrets.token_hex(_KEY_BYTES)
    prefix = raw[: _PREFIX_LENGTH + 3]  # include the sk_ part
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, key_hash, prefix


def _verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return hashlib.sha256(raw_key.encode()).hexdigest() == stored_hash


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------


@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIKeyCreateResponse)
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create a new API key.

    Returns the raw key **once** — it cannot be retrieved later.
    """
    from backend.database.models.api_key import APIKey

    # Resolve user's default org
    from backend.database.models.organization import OrganizationMember

    membership = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == current_user["id"])
        .order_by(OrganizationMember.role.desc())
        .limit(1)
    )
    org_member = membership.scalar_one_or_none()
    if not org_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a member of any organization",
        )

    raw_key, key_hash, key_prefix = _generate_api_key()

    expires_at = None
    if request.expires_in_days is not None:
        expires_at = datetime.now(UTC) + timedelta(days=request.expires_in_days)

    api_key = APIKey(
        organization_id=org_member.organization_id,
        name=request.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        scopes=request.scopes,
        expires_at=expires_at,
        created_by=current_user["id"],
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key": raw_key,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes or [],
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "created_at": api_key.created_at.isoformat(),
    }


@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List API keys for the current user's organization."""
    from backend.database.models.api_key import APIKey
    from backend.database.models.organization import OrganizationMember

    membership = await db.execute(
        select(OrganizationMember).where(OrganizationMember.user_id == current_user["id"]).limit(1)
    )
    org_member = membership.scalar_one_or_none()
    if not org_member:
        return []

    result = await db.execute(
        select(APIKey)
        .where(APIKey.organization_id == org_member.organization_id)
        .where(APIKey.created_by == current_user["id"])
        .order_by(APIKey.created_at.desc())
    )
    keys = result.scalars().all()

    return [
        {
            "id": str(k.id),
            "name": k.name,
            "key_prefix": k.key_prefix,
            "scopes": k.scopes or [],
            "expires_at": k.expires_at.isoformat() if k.expires_at else None,
            "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat(),
            "is_active": k.is_active,
        }
        for k in keys
    ]


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get details of a specific API key."""
    from backend.database.models.api_key import APIKey

    api_key = await db.get(APIKey, key_id)
    if not api_key or api_key.created_by != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "key_prefix": api_key.key_prefix,
        "scopes": api_key.scopes or [],
        "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
        "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        "created_at": api_key.created_at.isoformat(),
        "is_active": api_key.is_active,
    }


@router.delete("/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Revoke (soft-delete) an API key."""
    from backend.database.models.api_key import APIKey

    api_key = await db.get(APIKey, key_id)
    if not api_key or api_key.created_by != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    api_key.is_active = False
    db.add(api_key)
    await db.commit()

    return {"success": True, "message": "API key revoked"}
