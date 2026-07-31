"""LLM API endpoints using the new ai/llm provider system."""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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


def _get_available_providers() -> list[dict[str, Any]]:
    """Return list of providers that have API keys configured."""
    from ai.llm.providers import PROVIDER_ENV_MAP

    available = []
    for name, env_map in PROVIDER_ENV_MAP.items():
        api_key_var = env_map.get("api_key", "")
        key = os.getenv(api_key_var, "")
        available.append(
            {
                "name": name,
                "api_key_configured": bool(key),
                "env_var": api_key_var,
            }
        )
    return available


def _resolve_provider(provider_name: str | None = None, model: str | None = None) -> tuple[str, str]:
    """Resolve provider name from request params. Returns (provider_name, model)."""
    if provider_name:
        return provider_name, model or ""

    # Auto-detect from env vars using first available
    from ai.llm.providers import PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP

    for name, env_map in PROVIDER_ENV_MAP.items():
        api_key_var = env_map.get("api_key", "")
        if os.getenv(api_key_var, ""):
            return name, model or PROVIDER_DEFAULT_MODELS.get(name, "")

    return "", ""


def _create_provider_instance(provider_name: str, model: str | None = None) -> Any | None:
    """Create a provider instance from the factory."""
    factory = _get_llm_factory()
    if not factory:
        return None

    try:
        from ai.llm.providers import PROVIDER_DEFAULT_MODELS

        resolved_model = model or PROVIDER_DEFAULT_MODELS.get(provider_name, "")
        return factory.create(provider_name, model=resolved_model)
    except Exception as e:
        logger.error("Failed to create provider %s: %s", provider_name, e)
        return None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/providers", summary="List all LLM providers")
async def list_providers():
    """List all available LLM providers and their configuration status."""
    available = []

    for prov in _get_available_providers():
        available.append(
            {
                "name": prov["name"],
                "api_key_configured": prov["api_key_configured"],
            }
        )

    return {"success": True, "data": {"providers": available, "count": len(available)}}


@router.get("/providers/{provider_name}", summary="Get provider details")
async def get_provider(provider_name: str):
    """Get detailed information about a specific provider."""
    from ai.llm.providers import PROVIDER_CLASSES, PROVIDER_DEFAULT_MODELS, PROVIDER_ENV_MAP

    if provider_name not in PROVIDER_CLASSES:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_name}' not found")

    env_map = PROVIDER_ENV_MAP.get(provider_name, {})
    default_model = PROVIDER_DEFAULT_MODELS.get(provider_name, "")

    provider_cls = PROVIDER_CLASSES[provider_name]
    api_key_var = env_map.get("api_key", "")
    api_key_configured = bool(os.getenv(api_key_var, ""))

    # Create instance and get its models
    instance = _create_provider_instance(provider_name)
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
async def test_provider(provider_name: str):
    """Test if a provider is reachable with a health check."""
    instance = _create_provider_instance(provider_name)
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
):
    """List all supported models across providers."""
    from ai.llm.providers import PROVIDER_CLASSES, PROVIDER_DEFAULT_MODELS

    result = {}
    providers_to_check = [provider] if provider else list(PROVIDER_CLASSES.keys())

    for name in providers_to_check:
        if name not in PROVIDER_CLASSES:
            continue

        instance = _create_provider_instance(name)
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
async def chat_completion(request: ChatRequest):
    """Send a chat completion request to an LLM provider."""
    provider_name, model = _resolve_provider(request.provider, request.model)

    if not provider_name:
        raise HTTPException(
            status_code=400, detail="No LLM provider configured. Set API keys in environment variables."
        )

    instance = _create_provider_instance(provider_name, model)
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
async def chat_stream(request: ChatRequest):
    """Stream a chat completion response via SSE."""
    provider_name, model = _resolve_provider(request.provider, request.model)

    if not provider_name:
        raise HTTPException(
            status_code=400, detail="No LLM provider configured. Set API keys in environment variables."
        )

    instance = _create_provider_instance(provider_name, model)
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
async def llm_health():
    """Run health checks on all configured providers."""
    from ai.llm.providers import PROVIDER_ENV_MAP

    results = {}
    overall = True

    for name in PROVIDER_ENV_MAP:
        instance = _create_provider_instance(name)
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
