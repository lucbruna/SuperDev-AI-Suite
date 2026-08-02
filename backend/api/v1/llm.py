"""LLM API endpoints using the new ai/llm provider system.

Provider resolution now honors providers saved through the Settings UI
(``app_settings`` → ``providers``) with env-var fallback, so the runtime
matches what the user configures in the UI.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    provider: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = 4096
    top_p: float = 1.0
    stream: bool = False
    system: str | None = None
    tools: list[dict[str, Any]] | None = None


class ChatResponse(BaseModel):
    id: str
    model: str
    provider: str
    content: str
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ProviderInfo(BaseModel):
    name: str
    model: str
    available: bool
    api_key_configured: bool
    supports_streaming: bool = True


# ---------------------------------------------------------------------------
# Provider manager (lazy singleton)
# ---------------------------------------------------------------------------

_llm_manager: Any = None
_llm_factory: Any = None


def _get_llm_factory():
    """Lazy-init and return the LLMFactory singleton (sync)."""
    global _llm_factory
    if _llm_factory is not None:
        return _llm_factory

    try:
        from ai.llm import PROVIDER_CLASSES, LLMFactory

        factory = LLMFactory()
        factory.register_all(PROVIDER_CLASSES)
        _llm_factory = factory
        logger.info("LLMFactory initialized with %d provider types", factory.type_count)
        return factory
    except ImportError as e:
        logger.warning("LLM module not available: %s", e)
        _llm_factory = None
        return None
    except Exception as e:
        logger.error("Failed to initialize LLMFactory: %s", e)
        _llm_factory = None
        return None


async def _db_provider_config(
    db: AsyncSession | None, provider_name: str
) -> dict[str, Any]:
    """Return DB-saved provider config (api_key/base_url/model) or empty dict.

    Kept separate so both availability detection and instance creation share
    the same resolution without importing the settings service at module scope.
    """
    if db is None:
        return {}
    try:
        from backend.services.settings_service import get_runtime_provider_config

        return await get_runtime_provider_config(db, provider_name)
    except Exception as e:  # noqa: BLE001 — settings table may be missing
        logger.debug("DB provider config unavailable for %s: %s", provider_name, e)
        return {}


async def _get_available_providers(db: AsyncSession | None = None) -> list[dict[str, Any]]:
    """Return providers that have API keys configured (DB or env)."""
    from ai.llm.providers import PROVIDER_ENV_MAP

    available = []
    for name in PROVIDER_ENV_MAP:
        saved = await _db_provider_config(db, name)
        env_map = PROVIDER_ENV_MAP[name]
        api_key_var = env_map.get("api_key", "")
        key = saved.get("api_key") or os.getenv(api_key_var, "")
        available.append(
            {
                "name": name,
                "api_key_configured": bool(key),
                "env_var": api_key_var,
            }
        )
    return available


async def _resolve_provider(
    provider_name: str | None = None,
    model: str | None = None,
    db: AsyncSession | None = None,
) -> tuple[str, str]:
    """Resolve provider name from request params. Returns (provider_name, model)."""
    if provider_name:
        return provider_name, model or ""

    # Auto-detect: DB-saved providers first, then env vars.
    from ai.llm.providers import PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP

    for name in PROVIDER_ENV_MAP:
        saved = await _db_provider_config(db, name)
        api_key_var = PROVIDER_ENV_MAP[name].get("api_key", "")
        if saved.get("api_key") or os.getenv(api_key_var, ""):
            return name, model or saved.get("model") or PROVIDER_DEFAULT_MODELS.get(name, "")

    return "", ""


async def _create_provider_instance(
    provider_name: str,
    model: str | None = None,
    db: AsyncSession | None = None,
) -> Any | None:
    """Create a provider instance, overlaying DB-saved config over env defaults."""
    factory = _get_llm_factory()
    if not factory:
        return None

    try:
        from ai.llm.providers import PROVIDER_DEFAULT_MODELS

        resolved_model = model or PROVIDER_DEFAULT_MODELS.get(provider_name, "")
        kwargs: dict[str, Any] = {"model": resolved_model}

        saved = await _db_provider_config(db, provider_name)
        if saved.get("api_key"):
            kwargs["api_key"] = saved["api_key"]
        if saved.get("base_url"):
            kwargs["base_url"] = saved["base_url"]
        if saved.get("model"):
            kwargs["model"] = saved["model"]

        return factory.create(provider_name, **kwargs)
    except Exception as e:
        logger.error("Failed to create provider %s: %s", provider_name, e)
        return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/providers", summary="List all LLM providers")
async def list_providers(db: AsyncSession = Depends(get_db)):
    """List all available LLM providers and their configuration status."""
    available = []

    for prov in await _get_available_providers(db):
        available.append(
            {
                "name": prov["name"],
                "api_key_configured": prov["api_key_configured"],
            }
        )

    return {"success": True, "data": {"providers": available, "count": len(available)}}


@router.get("/providers/{provider_name}", summary="Get provider details")
async def get_provider(provider_name: str, db: AsyncSession = Depends(get_db)):
    """Get detailed information about a specific provider."""
    from ai.llm.providers import PROVIDER_CLASSES, PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP

    if provider_name not in PROVIDER_CLASSES:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    env_map = PROVIDER_ENV_MAP.get(provider_name, {})
    default_model = PROVIDER_DEFAULT_MODELS.get(provider_name, "")

    provider_cls = PROVIDER_CLASSES[provider_name]
    api_key_var = env_map.get("api_key", "")
    saved = await _db_provider_config(db, provider_name)
    api_key_configured = bool(saved.get("api_key") or os.getenv(api_key_var, ""))

    # Create instance and get its models
    instance = await _create_provider_instance(provider_name, db=db)
    models = []
    instance_available = False
    if instance:
        try:
            models = await instance.list_models()
            instance_available = True
        except Exception:
            models = [{"id": default_model, "name": provider_cls.__name__, "capabilities": ["chat"]}]

    result: dict[str, Any] = {
        "name": provider_name,
        "class": provider_cls.__name__,
        "default_model": default_model,
        "api_key_configured": api_key_configured,
        "api_key_env_var": api_key_var,
        "available": instance_available,
        "models": models,
    }

    return {"success": True, "data": result}


@router.post("/providers/{provider_name}/test", summary="Test provider connection")
async def test_provider(provider_name: str, db: AsyncSession = Depends(get_db)):
    """Test if a provider is reachable with a health check."""
    instance = await _create_provider_instance(provider_name, db=db)
    if not instance:
        raise HTTPException(
            status_code=400, detail=f"Provider '{provider_name}' not configured or failed to initialize"
        )

    try:
        health = await instance.health()
        return {
            "success": True,
            "data": {
                "provider": provider_name,
                "status": health.get("status", "unknown"),
                "latency_ms": health.get("latency_ms"),
                "model": instance.model(),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "data": {
                "provider": provider_name,
                "status": "error",
                "error": str(e),
            },
        }


@router.get("/models", summary="List supported models")
async def list_models(
    provider: str | None = Query(None, description="Filter by provider"),
    db: AsyncSession = Depends(get_db),
):
    """List all supported models across providers."""
    from ai.llm.providers import PROVIDER_CLASSES, PROVIDER_DEFAULT_MODELS

    result = {}
    providers_to_check = [provider] if provider else list(PROVIDER_CLASSES.keys())

    for name in providers_to_check:
        if name not in PROVIDER_CLASSES:
            continue

        instance = await _create_provider_instance(name, db=db)
        if instance:
            try:
                models = await instance.list_models()
                result[name] = {
                    "provider": name,
                    "default_model": PROVIDER_DEFAULT_MODELS.get(name, ""),
                    "models": models,
                }
            except Exception:
                result[name] = {
                    "provider": name,
                    "default_model": PROVIDER_DEFAULT_MODELS.get(name, ""),
                    "models": [{"id": PROVIDER_DEFAULT_MODELS.get(name, ""), "name": name, "capabilities": ["chat"]}],
                }

    return {"success": True, "data": result}


@router.post("/chat", summary="Chat completion")
async def chat_completion(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Send a chat completion request to an LLM provider."""
    provider_name, model = await _resolve_provider(request.provider, request.model, db)

    if not provider_name:
        raise HTTPException(
            status_code=400, detail="No LLM provider configured. Set API keys in environment variables or Settings."
        )

    instance = await _create_provider_instance(provider_name, model, db)
    if not instance:
        raise HTTPException(status_code=400, detail=f"Provider '{provider_name}' not available")

    # Build prompt from messages
    prompt = request.messages[-1].content if request.messages else ""
    kwargs: dict[str, Any] = {
        "temperature": request.temperature,
        "max_tokens": request.max_tokens or 4096,
        "top_p": request.top_p,
    }
    if request.system:
        kwargs["system"] = request.system
    if request.messages:
        kwargs["messages"] = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]
    if request.tools:
        kwargs["tools"] = request.tools

    try:
        result = await instance.generate(prompt, **kwargs)
    except Exception as e:
        logger.error("LLM generate failed: %s", e)
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "success": True,
        "data": {
            "id": str(uuid.uuid4()),
            "model": instance.model(),
            "provider": provider_name,
            "content": result.get("content", ""),
            "finish_reason": result.get("finish_reason", "stop"),
            "usage": {
                "prompt_tokens": result.get("tokens_prompt", 0),
                "completion_tokens": result.get("tokens_completion", 0),
                "total_tokens": (result.get("tokens_prompt", 0) or 0) + (result.get("tokens_completion", 0) or 0),
                "cost_usd": result.get("cost_usd", 0.0),
            },
            "tool_calls": result.get("tool_calls"),
        },
    }


@router.post("/chat/stream", summary="Streaming chat completion")
async def chat_stream(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Stream a chat completion response via SSE."""
    provider_name, model = await _resolve_provider(request.provider, request.model, db)

    if not provider_name:
        raise HTTPException(
            status_code=400, detail="No LLM provider configured. Set API keys in environment variables or Settings."
        )

    instance = await _create_provider_instance(provider_name, model, db)
    if not instance:
        raise HTTPException(status_code=400, detail=f"Provider '{provider_name}' not available")

    prompt = request.messages[-1].content if request.messages else ""
    kwargs: dict[str, Any] = {
        "temperature": request.temperature,
        "max_tokens": request.max_tokens or 4096,
        "top_p": request.top_p,
    }
    if request.system:
        kwargs["system"] = request.system
    if request.messages:
        kwargs["messages"] = [{"role": m.role, "content": m.content} for m in request.messages[:-1]]
    if request.tools:
        kwargs["tools"] = request.tools

    async def event_stream():
        try:
            stream = await instance.generate_stream(prompt, **kwargs)
            async for chunk in stream:
                delta = chunk.get("delta")
                delta_content = ""
                if delta is not None:
                    if hasattr(delta, "content"):
                        delta_content = delta.content
                    elif isinstance(delta, dict):
                        delta_content = delta.get("content", "")
                else:
                    delta_content = chunk.get("content", "")

                data = json.dumps(
                    {
                        "content": chunk.get("content", ""),
                        "finish_reason": chunk.get("finish_reason"),
                        "delta": {"content": delta_content},
                    }
                )
                yield f"data: {data}\n\n"

                if chunk.get("finish_reason") in ("stop", "length", "error"):
                    # Send final usage if available
                    if chunk.get("usage"):
                        usage_data = json.dumps({"usage": chunk["usage"]})
                        yield f"data: {usage_data}\n\n"
                    break

            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/health", summary="LLM providers health check")
async def llm_health(db: AsyncSession = Depends(get_db)):
    """Run health checks on all configured providers."""
    from ai.llm.providers import PROVIDER_ENV_MAP

    results = {}
    overall = True

    for name in PROVIDER_ENV_MAP:
        instance = await _create_provider_instance(name, db=db)
        if not instance:
            results[name] = {"status": "not_configured", "error": "Missing API key"}
            continue

        try:
            health = await instance.health()
            results[name] = health
            if health.get("status") != "healthy":
                overall = False
        except Exception as e:
            results[name] = {"status": "error", "error": str(e)}
            overall = False

    return {
        "success": True,
        "data": {
            "overall": "healthy" if overall else "degraded",
            "providers": results,
        },
    }
