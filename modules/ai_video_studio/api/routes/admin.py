"""Admin endpoints — workspace users and roles."""
from __future__ import annotations
from datetime import datetime, UTC
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str  # owner | admin | editor | viewer
    avatarUrl: str | None = None
    status: str  # active | invited | suspended
    lastActive: str | None = None


def _seed_users() -> dict[str, dict]:
    """Workspace user seed mirroring the frontend contract (in-memory store)."""
    now = datetime.now(UTC).isoformat()
    rows: list[dict] = [
        {"id": "u1", "name": "Ana Souza", "email": "ana@superdev.app", "role": "owner", "avatarUrl": None, "status": "active", "lastActive": now},
        {"id": "u2", "name": "Bruno Lima", "email": "bruno@superdev.app", "role": "editor", "avatarUrl": None, "status": "active", "lastActive": now},
        {"id": "u3", "name": "Carla Mendes", "email": "carla@superdev.app", "role": "viewer", "avatarUrl": None, "status": "invited", "lastActive": None},
        {"id": "u4", "name": "Diego Alves", "email": "diego@superdev.app", "role": "admin", "avatarUrl": None, "status": "active", "lastActive": now},
        {"id": "u5", "name": "Elisa Rocha", "email": "elisa@superdev.app", "role": "editor", "avatarUrl": None, "status": "suspended", "lastActive": None},
    ]
    return {row["id"]: row for row in rows}


_users: dict[str, dict] = _seed_users()


@router.get("/users", response_model=list[UserResponse])
async def list_users(role: str | None = None, status: str | None = None):
    """List workspace users (optionally filtered by role/status)."""
    items = list(_users.values())
    if role:
        items = [u for u in items if u["role"] == role]
    if status:
        items = [u for u in items if u["status"] == status]
    return [UserResponse(**u) for u in items]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    if user_id not in _users:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return UserResponse(**_users[user_id])
