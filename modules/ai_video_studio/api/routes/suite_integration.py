"""Suite Integration API — Volume 10: AI Video Studio ↔ SuperDev platform."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class TokenCheckRequest(BaseModel):
    token: str = Field(..., min_length=1, description="Bearer token to verify")


class UrlCheckRequest(BaseModel):
    url: str = Field(..., min_length=1, description="URL to validate against the SSRF policy")
    allow_private: bool = False


@router.get("/status", summary="Platform capability matrix (Volume 10)")
async def suite_status() -> dict[str, Any]:
    """Which suite platform services the studio can reuse right now."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    return {"success": True, "data": get_suite_bridge().check()}


@router.get("/adapters", summary="List suite adapters (Volume 10)")
async def suite_adapters() -> dict[str, Any]:
    """Per-adapter availability and actions."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    return {"success": True, "data": get_suite_bridge().adapters()}


@router.get("/manifest", summary="Studio platform contract (Volume 10)")
async def suite_manifest() -> dict[str, Any]:
    """What the studio consumes from / provides to the platform."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    return {"success": True, "data": get_suite_bridge().manifest()}


@router.post("/register", summary="Register the studio with the platform (Volume 10)")
async def suite_register() -> dict[str, Any]:
    """Install the studio into the suite integration engine, workflows and plugins."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    return {"success": True, "data": get_suite_bridge().register_with_platform()}


@router.post("/verify-token", summary="Verify a token via the platform JWT manager")
async def suite_verify_token(req: TokenCheckRequest) -> dict[str, Any]:
    """Reuse the suite backend JWT verification."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    result = await get_suite_bridge().verify_token(req.token)
    if not result.get("ok"):
        raise HTTPException(status_code=401, detail=result.get("reason", "invalid token"))
    return {"success": True, "data": result}


@router.post("/validate-url", summary="Validate a URL against the SSRF policy")
async def suite_validate_url(req: UrlCheckRequest) -> dict[str, Any]:
    """Reuse the suite SSRF guards (or the local fallback policy)."""
    from modules.ai_video_studio.suite_integration import get_suite_bridge

    result = get_suite_bridge().validate_url(req.url, allow_private=req.allow_private)
    if not result.get("safe"):
        raise HTTPException(status_code=400, detail=result.get("reason", "url rejected"))
    return {"success": True, "data": result}
