"""SSO Authentication API routes."""

from __future__ import annotations

import secrets
from typing import Any

from backend.dependencies import get_current_active_user
from backend.security.sso import SSOProviderType, sso_manager
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class SSOReturn(BaseModel):
    provider: str
    authorization_url: str
    state: str


class SSOCallbackRequest(BaseModel):
    provider: str
    code: str
    state: str


@router.get("/providers")
async def list_sso_providers(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> list[dict[str, Any]]:
    return sso_manager.list_providers()


@router.get("/authorize/{provider}", response_model=SSOReturn)
async def authorize_sso(
    provider: str,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> SSOReturn:
    state = secrets.token_urlsafe(32)
    try:
        url = await sso_manager.get_authorization_url(provider, state)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return SSOReturn(provider=provider, authorization_url=url, state=state)


@router.post("/callback")
async def sso_callback(
    request: SSOCallbackRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    try:
        user_info = await sso_manager.handle_callback(request.provider, request.code, request.state)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"SSO provider error: {e}")
    return {
        "success": True,
        "data": {
            "subject": user_info.subject,
            "email": user_info.email,
            "name": user_info.name,
            "provider": request.provider,
        },
    }


@router.post("/validate-token")
async def validate_sso_token(
    provider: str = Query(...),
    token: str = Query(...),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    user_info = await sso_manager.validate_token(provider, token)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid SSO token")
    return {
        "valid": True,
        "subject": user_info.subject,
        "email": user_info.email,
    }
