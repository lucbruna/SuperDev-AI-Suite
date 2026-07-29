from __future__ import annotations

from datetime import datetime
from typing import Annotated, List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from {{project_name}}.api.v1.auth import get_current_user


router = APIRouter()


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: str


# In-memory user store (replace with database)
_users_db: dict[str, dict] = {}


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Create a new user."""
    if user_data.email in _users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_id = str(uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    _users_db[user_data.email] = user
    
    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True,
        created_at=user["created_at"],
    )


@router.get("", response_model=List[UserResponse])
async def list_users(
    current_user: Annotated[dict, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponse]:
    """List all users."""
    users = list(_users_db.values())[skip:skip + limit]
    return [
        UserResponse(
            id=u["id"],
            email=u["email"],
            full_name=u["full_name"],
            is_active=u["is_active"],
            created_at=u["created_at"],
        )
        for u in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Get a specific user."""
    user = next((u for u in _users_db.values() if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        created_at=user["created_at"],
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Update a user."""
    user = next((u for u in _users_db.values() if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "email" in update_data and update_data["email"] != user["email"]:
        if update_data["email"] in _users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        # Update dict key
        del _users_db[user["email"]]
        user["email"] = update_data["email"]
        _users_db[user["email"]] = user
    
    for key, value in update_data.items():
        if key != "email":
            user[key] = value
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        is_active=user["is_active"],
        created_at=user["created_at"],
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Delete a user."""
    user = next((u for u in _users_db.values() if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    del _users_db[user["email"]]