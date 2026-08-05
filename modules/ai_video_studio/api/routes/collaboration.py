"""Collaboration endpoints — workspace members and per-member permissions."""
from __future__ import annotations
from datetime import datetime, UTC
from fastapi import APIRouter
from pydantic import BaseModel

from modules.ai_video_studio.api.routes.admin import UserResponse, _users

router = APIRouter()


class CollaboratorResponse(BaseModel):
    id: str
    user: UserResponse
    permission: str
    joinedAt: str


_collaborators: dict[str, dict] = {
    "c1": {"id": "c1", "user_id": "u2", "permission": "project:write", "joinedAt": datetime.now(UTC).isoformat()},
    "c2": {"id": "c2", "user_id": "u3", "permission": "project:read", "joinedAt": datetime.now(UTC).isoformat()},
    "c3": {"id": "c3", "user_id": "u4", "permission": "project:write", "joinedAt": datetime.now(UTC).isoformat()},
}


@router.get("/members", response_model=list[CollaboratorResponse])
async def list_members():
    """List workspace collaborators with their effective permission."""
    members = []
    for collab in _collaborators.values():
        user = _users.get(collab["user_id"])
        if user is None:
            continue
        members.append(
            CollaboratorResponse(
                id=collab["id"],
                user=UserResponse(**user),
                permission=collab["permission"],
                joinedAt=collab["joinedAt"],
            )
        )
    return members
