"""Tests for CORS middleware configuration."""
from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient

from backend.config import config


def _create_cors_test_app() -> FastAPI:
    """Create a minimal app with only CORS middleware (no TrustedHost)."""
    app = FastAPI(title="CORS Test")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allow_origins,
        allow_credentials=config.cors.allow_credentials,
        allow_methods=config.cors.allow_methods,
        allow_headers=config.cors.allow_headers,
        expose_headers=config.cors.expose_headers,
        max_age=config.cors.max_age,
    )

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


@pytest.fixture()
def app():
    return _create_cors_test_app()


@pytest.fixture()
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


class TestCORSHeaders:
    """Verify CORS preflight and response headers."""

    @pytest.mark.anyio
    async def test_options_preflight_returns_200(self, client):
        resp = await client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.status_code == 200

    @pytest.mark.anyio
    async def test_cors_allows_origin_header(self, client):
        resp = await client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"},
        )
        assert "access-control-allow-origin" in resp.headers

    @pytest.mark.anyio
    async def test_cors_allow_credentials(self, client):
        resp = await client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"},
        )
        if "access-control-allow-credentials" in resp.headers:
            assert resp.headers["access-control-allow-credentials"].lower() == "true"

    @pytest.mark.anyio
    async def test_cors_expose_headers(self, client):
        resp = await client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"},
        )
        if "access-control-expose-headers" in resp.headers:
            exposed = resp.headers["access-control-expose-headers"].lower()
            assert "x-request-id" in exposed

    @pytest.mark.anyio
    async def test_regular_get_has_no_cors_headers_without_origin(self, client):
        resp = await client.get("/test")
        assert "access-control-allow-origin" not in resp.headers


class TestCORSConfig:
    """Verify CORS config values from the app config."""

    def test_config_has_cors_settings(self):
        from backend.config import config

        assert hasattr(config.cors, "allow_origins")
        assert hasattr(config.cors, "allow_methods")
        assert hasattr(config.cors, "allow_headers")
        assert hasattr(config.cors, "allow_credentials")
        assert hasattr(config.cors, "max_age")

    def test_cors_origins_is_list(self):
        from backend.config import config

        assert isinstance(config.cors.allow_origins, list)
        assert len(config.cors.allow_origins) > 0

    def test_cors_methods_include_common(self):
        from backend.config import config

        methods = config.cors.allow_methods
        assert "GET" in methods
        assert "POST" in methods
        assert "PUT" in methods or "PATCH" in methods
        assert "DELETE" in methods

    def test_cors_max_age_is_positive(self):
        from backend.config import config

        assert config.cors.max_age > 0
