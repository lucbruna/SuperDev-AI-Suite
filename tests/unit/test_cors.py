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


class TestStrListEnvParsing:
    """Regression: .env uses comma-separated values (CORS_ALLOW_METHODS=GET,POST,...)
    which pydantic-settings 2.x cannot JSON-decode for list[str] fields. The
    StrList type (NoDecode + BeforeValidator) must accept JSON arrays,
    comma-separated strings, single bare values and empty values.
    """

    def test_comma_separated(self, monkeypatch):
        monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST,PUT,DELETE")
        from backend.settings import CorsSettings

        assert CorsSettings().allow_methods == ["GET", "POST", "PUT", "DELETE"]

    def test_json_array(self, monkeypatch):
        monkeypatch.setenv("CORS_ALLOW_METHODS", '["GET", "POST"]')
        from backend.settings import CorsSettings

        assert CorsSettings().allow_methods == ["GET", "POST"]

    def test_single_bare_value(self, monkeypatch):
        monkeypatch.setenv("CORS_ALLOW_HEADERS", "*")
        from backend.settings import CorsSettings

        assert CorsSettings().allow_headers == ["*"]

    def test_empty_value(self, monkeypatch):
        monkeypatch.setenv("REDIS_SENTINEL_HOSTS", "")
        from backend.settings import RedisSettings

        assert RedisSettings().sentinel_hosts == []

    def test_absent_env_uses_default(self, monkeypatch):
        monkeypatch.delenv("CORS_ALLOW_METHODS", raising=False)
        from backend.settings import CorsSettings

        assert CorsSettings().allow_methods == ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    def test_config_imports_with_comma_separated_env(self, monkeypatch):
        """The full backend.config (conftest import chain) must load with the
        comma-separated .env format — no SettingsError.

        Reloading is required because the nested settings (e.g. ``cors``) are
        instantiated at class-definition time, so a plain ``AppConfig()``
        would not re-read the environment. The module singleton is restored in
        ``finally`` so the fabricated values do not leak into other tests.
        """
        import importlib

        import backend.config

        env = {
            "CORS_ALLOW_METHODS": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
            "CORS_ALLOW_ORIGINS": "http://a,http://b",
            "CORS_ALLOW_HEADERS": "*",
            "CORS_EXPOSE_HEADERS": "X-Request-ID,X-Process-Time",
            "RUNTIME_DROP_CAPABILITIES": "all",
            "PLUGIN_PERMISSIONS_REQUIRED": "filesystem.read",
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        try:
            importlib.reload(backend.config)
            cfg = backend.config.config
            assert cfg.cors.allow_methods == ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
            assert cfg.cors.allow_origins == ["http://a", "http://b"]
            assert cfg.sandbox.drop_capabilities == ["all"]
            assert cfg.plugins.permissions_required == ["filesystem.read"]
        finally:
            # Restore the module singleton from the real environment/.env so
            # the fabricated values don't leak into subsequent tests.
            for key in env:
                monkeypatch.delenv(key, raising=False)
            importlib.reload(backend.config)
