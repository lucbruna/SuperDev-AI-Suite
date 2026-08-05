from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.passwords import verify_password
from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.services import settings_service
from backend.users.schema import UserResponse, UserUpdate
from backend.users.service import UserService

router = APIRouter(dependencies=[Depends(get_current_active_user)])

_PREFERENCES_KEY = "user_preferences"


class UpdatePasswordRequest(BaseModel):
    currentPassword: str = Field(min_length=1)
    newPassword: str = Field(min_length=8)


class UserPreferences(BaseModel):
    theme: str = "system"
    fontSize: int = 14
    tabSize: int = 4
    fontFamily: str = "Inter"
    autoSave: bool = True
    autoSaveInterval: int = 5
    language: str = "en"
    notifications: dict[str, Any] = Field(default_factory=dict)


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    user = await service.get_user(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    update: UserUpdate,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    updated = await service.update_user(current_user["id"], **update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(updated)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.get("/", response_model=list[UserResponse])
async def list_users(
    page: int = 1,
    size: int = 20,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.USERS, Action.READ)),
) -> list[UserResponse]:
    service = UserService(db)
    users = await service.list_users(page=page, size=size)
    return [UserResponse.model_validate(u) for u in users]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.USERS, Action.DELETE)),
) -> None:
    service = UserService(db)
    await service.delete_user(user_id)


@router.get("/preferences")
async def get_preferences(
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    key = f"{_PREFERENCES_KEY}:{current_user['id']}"
    prefs = await settings_service.load_setting(db, key) or {}
    return {"success": True, "data": {"preferences": {**UserPreferences().model_dump(), **prefs}}}


@router.put("/preferences")
async def update_preferences(
    preferences: UserPreferences,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    key = f"{_PREFERENCES_KEY}:{current_user['id']}"
    await settings_service.save_setting(db, key, preferences.model_dump())
    return {"success": True, "data": {"preferences": preferences.model_dump()}}


@router.put("/password")
async def update_password(
    request: UpdatePasswordRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = UserService(db)
    user = await service.get_user(current_user["id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not verify_password(request.currentPassword, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    await service.update_password(str(user.id), request.newPassword)
    return {"success": True, "message": "Password updated successfully"}
