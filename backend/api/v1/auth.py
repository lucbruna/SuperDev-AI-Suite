from datetime import datetime, UTC
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth.jwt import JWTManager
from backend.auth.passwords import verify_password
from backend.auth.sessions import SessionManager
from backend.config import config
from backend.database.session import get_db
from backend.users.service import UserService

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str
    full_name: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(BaseModel):
    user: dict[str, Any]
    accessToken: str
    refreshToken: str
    expiresIn: int


jwt_manager = JWTManager(secret_key=str(config.auth.secret_key))
session_manager = SessionManager()


@router.post("/login")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user_service = UserService(db)
    user = await user_service.get_user_by_email(request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = jwt_manager.create_access_token(subject=str(user.id))
    refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": getattr(user, "username", user.email.split("@")[0]),
                "fullName": getattr(user, "full_name", ""),
                "avatarUrl": getattr(user, "avatar_url", ""),
                "role": getattr(user, "role", "user"),
                "isEmailVerified": getattr(user, "is_verified", False),
                "createdAt": getattr(user, "created_at", datetime.now(UTC)).isoformat() if hasattr(user, "created_at") else datetime.now(UTC).isoformat(),
                "updatedAt": getattr(user, "updated_at", datetime.now(UTC)).isoformat() if hasattr(user, "updated_at") else datetime.now(UTC).isoformat(),
            },
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": jwt_manager.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    user_service = UserService(db)
    existing = await user_service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = await user_service.create_user(
        email=request.email,
        password=request.password,
        username=request.username,
        full_name=request.full_name,
    )
    access_token = jwt_manager.create_access_token(subject=str(user.id))
    refresh_token = jwt_manager.create_refresh_token(subject=str(user.id))
    return {
        "success": True,
        "data": {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": getattr(user, "username", user.email.split("@")[0]),
                "fullName": getattr(user, "full_name", ""),
                "avatarUrl": getattr(user, "avatar_url", ""),
                "role": getattr(user, "role", "user"),
                "isEmailVerified": getattr(user, "is_verified", False),
                "createdAt": getattr(user, "created_at", datetime.now(UTC)).isoformat() if hasattr(user, "created_at") else datetime.now(UTC).isoformat(),
                "updatedAt": getattr(user, "updated_at", datetime.now(UTC)).isoformat() if hasattr(user, "updated_at") else datetime.now(UTC).isoformat(),
            },
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "expiresIn": jwt_manager.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        },
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshRequest,
) -> TokenResponse:
    payload = jwt_manager.decode_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    access_token = jwt_manager.create_access_token(subject=subject)
    new_refresh_token = jwt_manager.create_refresh_token(subject=subject)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me")
async def get_current_user(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    from backend.dependencies import get_current_user as auth_dependency

    from backend.users.service import UserService

    return {"success": True, "data": {"user": None}}
