"""Settings storage service — persistent key/value settings in PostgreSQL.

This module owns all reads/writes to the ``app_settings`` table so the
Settings API and the Admin API share one storage layer (no more in-memory
dicts that die on restart). The table is created by the Alembic migration
``c1d2e3f4a5b6_add_app_settings``; ``ensure_table`` is kept as a defensive
fallback for fresh installs that run migrations lazily.

PostgreSQL-compatible only (TIMESTAMPTZ, ``now()``). The previous lazy DDL
used SQLite's ``datetime('now')`` which fails on Postgres.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

__all__ = [
    "ensure_table",
    "load_setting",
    "save_setting",
    "get_setting_with_default",
    "get_all_settings",
    "reset_settings",
    "mask_api_keys",
    "PROVIDER_DEFAULTS",
    "get_runtime_provider_config",
]

# Default LLM provider registry used by the Settings API and the runtime.
# The runtime resolver (get_runtime_provider_config) overlays these with any
# API key / base URL saved via the Settings UI, falling back to env vars.
PROVIDER_DEFAULTS: list[dict[str, Any]] = [
    {
        "id": "openai",
        "name": "OpenAI",
        "type": "llm",
        "apiKey": "",
        "baseUrl": "https://api.openai.com/v1",
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
        "enabled": True,
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "type": "llm",
        "apiKey": "",
        "baseUrl": "https://api.anthropic.com",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
        "enabled": False,
    },
    {
        "id": "google",
        "name": "Google (Gemini)",
        "type": "llm",
        "apiKey": "",
        "baseUrl": "https://generativelanguage.googleapis.com",
        "models": ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"],
        "enabled": False,
    },
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "type": "llm",
        "apiKey": "",
        "baseUrl": "https://openrouter.ai/api/v1",
        "models": ["anthropic/claude-3-opus", "openai/gpt-4", "meta-llama/llama-3-70b"],
        "enabled": False,
    },
    {
        "id": "groq",
        "name": "Groq",
        "type": "llm",
        "apiKey": "",
        "baseUrl": "https://api.groq.com/openai/v1",
        "models": ["llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
        "enabled": False,
    },
]

_TABLE_DDL = sa_text(
    """
    CREATE TABLE IF NOT EXISTS app_settings (
        id TEXT PRIMARY KEY,
        key TEXT UNIQUE NOT NULL,
        value TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'general',
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """
)


async def ensure_table(db: AsyncSession) -> None:
    """Create the settings table if it doesn't exist (PG-compatible)."""
    await db.execute(_TABLE_DDL)
    await db.commit()


async def load_setting(db: AsyncSession, key: str) -> Any | None:
    """Load a stored setting by key (JSON-decoded). Returns None if absent."""
    result = await db.execute(
        sa_text("SELECT value FROM app_settings WHERE key = :key"),
        {"key": key},
    )
    row = result.fetchone()
    if row:
        try:
            return json.loads(row[0])
        except (TypeError, json.JSONDecodeError):
            return row[0]
    return None


async def save_setting(db: AsyncSession, key: str, value: Any, category: str = "general") -> None:
    """Upsert a setting (JSON-encoded value)."""
    now = datetime.now(UTC).isoformat()
    value_json = json.dumps(value, default=str)
    await db.execute(
        sa_text(
            """
            INSERT INTO app_settings (id, key, value, category, created_at, updated_at)
            VALUES (:id, :key, :value, :category, :created_at, :updated_at)
            ON CONFLICT (key) DO UPDATE
                SET value = :value, category = :category, updated_at = :updated_at
            """
        ),
        {
            "id": f"setting_{key}",
            "key": key,
            "value": value_json,
            "category": category,
            "created_at": now,
            "updated_at": now,
        },
    )
    await db.commit()


async def get_setting_with_default(db: AsyncSession, key: str, defaults: dict[str, Any]) -> Any:
    """Return stored value, falling back to the provided defaults dict."""
    value = await load_setting(db, key)
    if value is not None:
        return value
    return defaults.get(key, {})


async def get_all_settings(db: AsyncSession, defaults: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return every key in ``defaults`` resolved against storage."""
    result: dict[str, Any] = {}
    for key in defaults:
        result[key] = await get_setting_with_default(db, key, defaults)
    return result


async def reset_settings(db: AsyncSession, defaults: dict[str, dict[str, Any]]) -> None:
    """Persist every default value back to storage."""
    for key, default_value in defaults.items():
        await save_setting(db, key, default_value, category=key)


def mask_api_keys(providers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of provider configs with API keys masked.

    Replaces the raw key with ``apiKeyConfigured`` plus a truncated preview
    (first 8 + last 4 chars) so UIs can show state without leaking secrets.
    """
    masked: list[dict[str, Any]] = []
    for p in providers:
        p_copy = dict(p)
        raw_key = p_copy.get("apiKey") or ""
        if raw_key:
            p_copy["apiKeyConfigured"] = True
            p_copy["apiKey"] = (
                f"{raw_key[:8]}...{raw_key[-4:]}" if len(raw_key) > 12 else "***"
            )
        else:
            p_copy["apiKeyConfigured"] = False
        masked.append(p_copy)
    return masked


async def get_runtime_provider_config(
    db: AsyncSession,
    provider_name: str,
) -> dict[str, Any]:
    """Resolve a provider's runtime kwargs (api_key/base_url/model) for the
    AI runtime, merging DB-saved settings with env-var fallback.

    Priority: saved DB setting (apiKey/baseUrl/models from the Settings UI)
    first, then environment variables, then provider defaults. This is what
    makes the LLM runtime (ai_router / ai.llm) actually honor the provider
    configuration saved in the UI instead of only reading env vars.
    """
    await ensure_table(db)
    providers = await get_setting_with_default(
        db, "providers", {"providers": PROVIDER_DEFAULTS}
    )
    providers = list(providers) if isinstance(providers, list) else []

    saved = next((p for p in providers if p.get("id") == provider_name), None)

    # Env-var fallback map (same keys the ai.llm runtime uses).
    try:
        from ai.llm.providers import PROVIDER_ENV_MAP, PROVIDER_DEFAULT_MODELS
    except Exception:  # ai.llm not importable in isolation
        provider_env_map = {}
        provider_default_models = {}
    else:
        provider_env_map = PROVIDER_ENV_MAP
        provider_default_models = PROVIDER_DEFAULT_MODELS

    env_map = provider_env_map.get(provider_name, {})
    api_key_var = env_map.get("api_key", "")
    base_url_var = env_map.get("base_url", "")

    result: dict[str, Any] = {
        "api_key": "",
        "base_url": "",
        "model": "",
    }

    if saved:
        result["api_key"] = saved.get("apiKey") or ""
        result["base_url"] = saved.get("baseUrl") or ""
        models = saved.get("models") or []
        if models:
            result["model"] = models[0]

    # Fall back to env vars for any field not saved in the DB.
    if not result["api_key"] and api_key_var:
        result["api_key"] = os.getenv(api_key_var, "")
    if not result["base_url"] and base_url_var:
        result["base_url"] = os.getenv(base_url_var, "")
    if not result["model"]:
        result["model"] = provider_default_models.get(provider_name, "")

    return result
