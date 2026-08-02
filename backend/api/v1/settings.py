"""Settings API with PostgreSQL persistence (via ``settings_service``).

Endpoints:
- GET/PUT   /settings/general
- GET/PUT   /settings/appearance
- GET       /settings/providers          (API keys masked)
- GET       /settings/providers/raw      (internal, unmasked)
- POST      /settings/providers          (add a provider)
- PUT       /settings/providers/{id}     (update a provider)
- DELETE    /settings/providers/{id}     (remove a provider)
- POST      /settings/providers/{id}/test
- GET/PUT   /settings/llm
- GET       /settings/all
- POST      /settings/reset
"""

from __future__ import annotations

import copy
import logging
import re
import time
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.services import settings_service

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_active_user)])

# Default settings
_DEFAULTS: dict[str, Any] = {
    "general": {
        "defaultLanguage": "en",
        "timezone": "UTC",
        "dateFormat": "YYYY-MM-DD",
    },
    "appearance": {
        "theme": "dark",
        "fontSize": 14,
        "sidebarPosition": "left",
        "compactMode": False,
    },
    "llm": {
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 4096,
        "system_prompt": "You are a helpful coding assistant.",
    },
    # Shared with settings_service so the runtime and the API never drift.
    "providers": settings_service.PROVIDER_DEFAULTS,
}


async def _get_providers(db: AsyncSession) -> list[dict[str, Any]]:
    """Load provider configs (raw, unmasked) from storage.

    Returns a deep copy so downstream mutations (update/delete) never leak
    into the shared PROVIDER_DEFAULTS that the runtime resolver reads.
    """
    await settings_service.ensure_table(db)
    providers = await settings_service.get_setting_with_default(db, "providers", _DEFAULTS)
    return copy.deepcopy(list(providers))


def _invalidate_runtime_provider(provider_id: str) -> None:
    """Drop cached provider instances so the LLM runtime honors the new config.

    ProviderRegistry caches one instance per name; without invalidating it, a
    saved API key / base URL change would only take effect after a restart.
    Unknown ids are a no-op (nothing cached).
    """
    try:
        from backend.providers.provider_registry import ProviderRegistry

        ProviderRegistry.invalidate(provider_id)
    except Exception:  # noqa: BLE001 — runtime not importable in isolation
        pass


# ── General Settings ─────────────────────────────────────────────────────────


@router.get("/general")
async def get_general_settings(db: AsyncSession = Depends(get_db)):
    await settings_service.ensure_table(db)
    data = await settings_service.get_setting_with_default(db, "general", _DEFAULTS)
    return {"success": True, "data": data}


@router.put("/general")
async def update_general_settings(data: dict, db: AsyncSession = Depends(get_db)):
    await settings_service.ensure_table(db)
    existing = await settings_service.get_setting_with_default(db, "general", _DEFAULTS)
    existing.update(data)
    await settings_service.save_setting(db, "general", existing, category="general")
    return {"success": True, "data": existing}


# ── Appearance Settings ──────────────────────────────────────────────────────


@router.get("/appearance")
async def get_appearance_settings(db: AsyncSession = Depends(get_db)):
    await settings_service.ensure_table(db)
    data = await settings_service.get_setting_with_default(db, "appearance", _DEFAULTS)
    return {"success": True, "data": data}


@router.put("/appearance")
async def update_appearance_settings(data: dict, db: AsyncSession = Depends(get_db)):
    await settings_service.ensure_table(db)
    existing = await settings_service.get_setting_with_default(db, "appearance", _DEFAULTS)
    existing.update(data)
    await settings_service.save_setting(db, "appearance", existing, category="appearance")
    return {"success": True, "data": existing}


# ── Provider Configurations ──────────────────────────────────────────────────


@router.get("/providers")
async def get_provider_configs(db: AsyncSession = Depends(get_db)):
    """List providers with API keys masked for the UI."""
    providers = await _get_providers(db)
    return {"success": True, "data": settings_service.mask_api_keys(providers)}


@router.get("/providers/raw")
async def get_provider_configs_raw(db: AsyncSession = Depends(get_db)):
    """Get provider configs without masking (for internal use)."""
    providers = await _get_providers(db)
    return {"success": True, "data": providers}


@router.post("/providers")
async def create_provider_config(data: dict, db: AsyncSession = Depends(get_db)):
    """Add a new provider to the providers list."""
    await settings_service.ensure_table(db)
    providers = await _get_providers(db)

    name = str(data.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="Provider name is required")

    # Idempotent id: slug from name, deduplicated with a short suffix if needed.
    provider_id = str(data.get("id") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "provider")
    existing_ids = {p.get("id") for p in providers}
    if provider_id in existing_ids:
        provider_id = f"{provider_id}-{uuid.uuid4().hex[:6]}"

    provider: dict[str, Any] = {
        "id": provider_id,
        "name": name,
        "type": data.get("type", "llm"),
        "apiKey": data.get("apiKey", ""),
        "baseUrl": data.get("baseUrl", ""),
        "models": list(data.get("models") or []),
        "enabled": bool(data.get("enabled", True)),
    }
    # Carry over any extra config fields the client sent.
    for key, value in data.items():
        if key not in provider and key not in ("id",):
            provider[key] = value

    providers.append(provider)
    await settings_service.save_setting(db, "providers", providers, category="providers")
    _invalidate_runtime_provider(provider_id)
    return {"success": True, "data": settings_service.mask_api_keys([provider])[0]}


@router.put("/providers/{provider_id}")
async def update_provider_config(provider_id: str, data: dict, db: AsyncSession = Depends(get_db)):
    providers = await _get_providers(db)
    for p in providers:
        if p["id"] == provider_id:
            # Don't overwrite apiKey if not provided
            if "apiKey" in data and data["apiKey"] == "":
                del data["apiKey"]
            p.update(data)
            await settings_service.save_setting(db, "providers", providers, category="providers")
            _invalidate_runtime_provider(provider_id)
            return {"success": True, "data": p}
    raise HTTPException(status_code=404, detail="Provider not found")


@router.delete("/providers/{provider_id}")
async def delete_provider_config(provider_id: str, db: AsyncSession = Depends(get_db)):
    providers = await _get_providers(db)
    for p in providers:
        if p["id"] == provider_id:
            providers.remove(p)
            await settings_service.save_setting(db, "providers", providers, category="providers")
            _invalidate_runtime_provider(provider_id)
            return {"success": True, "message": f"Provider '{provider_id}' removed"}
    raise HTTPException(status_code=404, detail="Provider not found")


@router.post("/providers/{provider_id}/test")
async def test_provider_connection(provider_id: str, db: AsyncSession = Depends(get_db)):
    """Test a provider connection against the real LLM backend."""
    providers = await _get_providers(db)
    provider = next((p for p in providers if p["id"] == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    api_key = provider.get("apiKey") or ""
    if not api_key:
        return {"success": False, "data": {"success": False, "error": "API key not configured"}}

    try:
        from ai.llm import PROVIDER_CLASSES, LLMFactory

        if provider_id not in PROVIDER_CLASSES:
            return {
                "success": False,
                "data": {"success": False, "error": f"Provider type '{provider_id}' not available in runtime"},
            }

        factory = LLMFactory()
        factory.register_all(PROVIDER_CLASSES)

        kwargs: dict[str, Any] = {"api_key": api_key}
        base_url = provider.get("baseUrl") or ""
        if base_url:
            kwargs["base_url"] = base_url
        models = provider.get("models") or []
        if models:
            kwargs["model"] = models[0]

        instance = factory.create(provider_id, **kwargs)
        start = time.monotonic()
        health = await instance.health()
        latency = round((time.monotonic() - start) * 1000, 1)

        status = health.get("status") if isinstance(health, dict) else "unknown"
        if status == "healthy":
            return {
                "success": True,
                "data": {
                    "success": True,
                    "message": f"Connection to {provider['name']} ok",
                    "latency_ms": health.get("latency_ms", latency),
                },
            }
        return {
            "success": False,
            "data": {"success": False, "error": health.get("error", "Provider unhealthy")},
        }
    except Exception as e:  # noqa: BLE001 — surface provider errors to the UI
        logger.warning("Provider test failed for %s: %s", provider_id, e)
        return {"success": False, "data": {"success": False, "error": str(e)}}


# ── LLM Default Settings ────────────────────────────────────────────────────


@router.get("/llm")
async def get_llm_settings(db: AsyncSession = Depends(get_db)):
    """Get default LLM settings (model, temperature, etc.)"""
    await settings_service.ensure_table(db)
    data = await settings_service.get_setting_with_default(db, "llm", _DEFAULTS)
    return {"success": True, "data": data}


@router.put("/llm")
async def update_llm_settings(data: dict, db: AsyncSession = Depends(get_db)):
    """Update default LLM settings."""
    await settings_service.ensure_table(db)
    existing = await settings_service.get_setting_with_default(db, "llm", _DEFAULTS)
    existing.update(data)
    await settings_service.save_setting(db, "llm", existing, category="llm")
    return {"success": True, "data": existing}


# ── Bulk Settings ────────────────────────────────────────────────────────────


@router.get("/all")
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Get all settings at once."""
    await settings_service.ensure_table(db)
    result = {}
    for key in _DEFAULTS:
        result[key] = await settings_service.get_setting_with_default(db, key, _DEFAULTS)
    return {"success": True, "data": result}


@router.post("/reset")
async def reset_settings(db: AsyncSession = Depends(get_db)):
    """Reset all settings to defaults."""
    await settings_service.ensure_table(db)
    await settings_service.reset_settings(db, _DEFAULTS)
    return {"success": True, "message": "Settings reset to defaults"}
