"""Tests for the LLM API endpoints."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from backend.api.v1.llm import router

# ---------------------------------------------------------------------------
# Test app (standalone, avoids importing full backend)
# ---------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a FastAPI app with just the LLM router."""
    application = FastAPI()
    application.include_router(router, prefix="/api/v1/llm")
    return application


@pytest.fixture
def client(app):
    """Create an async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ---------------------------------------------------------------------------
# Mock provider for tests
# ---------------------------------------------------------------------------

MOCK_CHAT_RESPONSE = {
    "content": "Test response",
    "success": True,
    "finish_reason": "stop",
    "tokens_prompt": 10,
    "tokens_completion": 20,
    "cost_usd": 0.0001,
}

MOCK_STREAM_CHUNKS = [
    {"content": "Hello", "finish_reason": None, "delta": {"content": "Hello"}},
    {"content": " world", "finish_reason": None, "delta": {"content": " world"}},
    {"content": "", "finish_reason": "stop", "delta": {"content": "", "finish_reason": "stop"}},
]


class MockProvider:
    def __init__(self, **kwargs):
        self._name = kwargs.get("name", "mock")
        self._model = kwargs.get("model", "mock-model")

    def name(self):
        return self._name

    def model(self):
        return self._model

    async def generate(self, prompt: str, **kwargs):
        return MOCK_CHAT_RESPONSE

    async def generate_stream(self, prompt: str, **kwargs):
        async def _gen():
            for chunk in MOCK_STREAM_CHUNKS:
                yield chunk
        return _gen()

    async def health(self):
        return {"status": "healthy", "latency_ms": 42.0, "provider": self._name, "model": self._model}

    async def list_models(self):
        return [{"id": "mock-model", "name": "Mock Model", "capabilities": ["chat"]}]


@pytest.fixture(autouse=True)
def setup_env():
    """Set up environment variables for tests."""
    old_keys = {}
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "MOCK_API_KEY"]:
        old_keys[key] = os.environ.get(key)
    os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
    yield
    for key, val in old_keys.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_providers(client: AsyncClient):
    """GET /api/v1/llm/providers should list all providers."""
    response = await client.get("/api/v1/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "providers" in data["data"]
    assert data["data"]["count"] > 0


@pytest.mark.asyncio
async def test_get_provider_found(client: AsyncClient):
    """GET /api/v1/llm/providers/{name} should return provider details."""
    response = await client.get("/api/v1/llm/providers/openai")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "openai"
    assert "class" in data["data"]
    assert "default_model" in data["data"]


@pytest.mark.asyncio
async def test_get_provider_not_found(client: AsyncClient):
    """GET /api/v1/llm/providers/{name} should 404 for unknown provider."""
    response = await client.get("/api/v1/llm/providers/unknown-xyz")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_models_default(client: AsyncClient):
    """GET /api/v1/llm/models should return models for OpenAI (has env key)."""
    response = await client.get("/api/v1/llm/models")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # Should have at least OpenAI (since we set the env var)
    assert "openai" in data["data"] or len(data["data"]) > 0


@pytest.mark.asyncio
async def test_list_models_by_provider(client: AsyncClient):
    """GET /api/v1/llm/models?provider=openai should filter."""
    response = await client.get("/api/v1/llm/models?provider=openai")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@pytest.mark.asyncio
async def test_chat_completion_no_key(client: AsyncClient):
    """POST /api/v1/llm/chat without any configured provider should 400."""
    # Remove env vars for this test
    with patch.dict(os.environ, {}, clear=True):
        response = await client.post(
            "/api/v1/llm/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )
        assert response.status_code == 400
        assert "No LLM provider configured" in response.text


@pytest.mark.asyncio
async def test_chat_completion_success(client: AsyncClient):
    """POST /api/v1/llm/chat should return a completion."""
    with patch("backend.api.v1.llm._create_provider_instance", return_value=MockProvider(name="openai", model="gpt-4o")):
        response = await client.post(
            "/api/v1/llm/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "provider": "openai",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["content"] == "Test response"
        assert data["data"]["provider"] == "openai"
        assert data["data"]["usage"]["prompt_tokens"] == 10


@pytest.mark.asyncio
async def test_chat_completion_with_system(client: AsyncClient):
    """POST /api/v1/llm/chat with system message."""
    with patch("backend.api.v1.llm._create_provider_instance", return_value=MockProvider(name="openai", model="gpt-4o")):
        response = await client.post(
            "/api/v1/llm/chat",
            json={
                "messages": [{"role": "user", "content": "Hi"}],
                "provider": "openai",
                "system": "You are a helpful assistant.",
                "temperature": 0.5,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
async def test_chat_stream(client: AsyncClient):
    """POST /api/v1/llm/chat/stream should return SSE stream."""
    with patch("backend.api.v1.llm._create_provider_instance", return_value=MockProvider(name="openai", model="gpt-4o")):
        response = await client.post(
            "/api/v1/llm/chat/stream",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "provider": "openai",
            },
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Read stream content
        content = response.text
        assert "Hello" in content
        assert "world" in content
        assert "[DONE]" in content


@pytest.mark.asyncio
async def test_test_provider(client: AsyncClient):
    """POST /api/v1/llm/providers/{name}/test should return health."""
    with patch("backend.api.v1.llm._create_provider_instance", return_value=MockProvider(name="openai", model="gpt-4o")):
        response = await client.post("/api/v1/llm/providers/openai/test")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert data["data"]["latency_ms"] == 42.0
