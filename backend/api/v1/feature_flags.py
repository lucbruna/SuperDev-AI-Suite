"""Feature flags endpoint backed by the enterprise FeatureFlagManager.

Wraps ``core.enterprise.feature_flags.flag_manager`` (the single source of
truth used by the rest of the suite) so the admin dashboard can list and
toggle flags without importing enterprise internals.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies import get_current_active_user

logger = logging.getLogger("superdev.api.feature_flags")

router = APIRouter(
    tags=["feature-flags"],
    dependencies=[Depends(get_current_active_user)],
)


def _manager() -> Any:
    """Instantiate the flag manager (matches enterprise_api pattern)."""
    from core.enterprise.feature_flags.flag_manager import FeatureFlagManager

    return FeatureFlagManager()


@router.get("")
async def list_flags() -> dict[str, Any]:
    """Return all feature flags with their enabled state."""
    try:
        flags = await _manager().get_flags()
        return {"success": True, "flags": flags}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flags list failed: %s", exc)
        return {"success": True, "flags": [], "warning": str(exc)}


@router.get("/{flag_name}")
async def get_flag(flag_name: str) -> dict[str, Any]:
    """Return a single feature flag."""
    try:
        flags = await _manager().get_flags()
        for flag in flags:
            if flag.get("name") == flag_name:
                return {"success": True, "flag": flag}
        raise HTTPException(status_code=404, detail=f"Flag '{flag_name}' não encontrada")
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flag get failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/{flag_name}/toggle")
async def toggle_flag(flag_name: str) -> dict[str, Any]:
    """Toggle a feature flag on/off."""
    try:
        enabled = await _manager().toggle_flag(flag_name)
        return {"success": True, "flag": flag_name, "enabled": enabled}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flag toggle failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{flag_name}")
async def set_flag(flag_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Set a feature flag to an explicit value."""
    enabled = bool(payload.get("enabled"))
    try:
        result = await _manager().set_flag(flag_name, enabled)
        return {"success": True, "flag": flag_name, "enabled": result}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flag set failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{flag_name}")
async def delete_flag(flag_name: str) -> dict[str, Any]:
    """Delete a feature flag."""
    try:
        await _manager().delete_flag(flag_name)
        return {"success": True, "flag": flag_name, "deleted": True}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flag delete failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/check/{flag_name}")
async def check_flag(flag_name: str) -> dict[str, Any]:
    """Evaluate a flag (used by the frontend feature gate)."""
    try:
        enabled = await _manager().is_enabled(flag_name)
        return {"success": True, "name": flag_name, "enabled": enabled}
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("feature flag check failed: %s", exc)
        return {"success": True, "name": flag_name, "enabled": False}
