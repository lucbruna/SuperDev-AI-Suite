from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from {{project_name}}.config import get_settings
from {{project_name}}.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    is_active: bool
    created_at: str


# In-memory user store for demo (replace with database)
_users_db: dict[str, dict] = {}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> UserResponse:
    """Register a new user."""
    if user_data.email in _users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    user_id = str(uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
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


@router.post("/login", response_model=TokenResponse)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenResponse:
    """Authenticate user and return tokens."""
    user = _users_db.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": user["id"], "email": user["email"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = create_refresh_token(data={"sub": user["id"]})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str) -> TokenResponse:
    """Refresh access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user_id = payload.get("sub")
    user = next((u for u in _users_db.values() if u["id"] == user_id), None)
    
    if not user or not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": user_id, "email": user["email"]},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """Get current authenticated user."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    user = next((u for u in _users_db.values() if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Get current user info."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
    )