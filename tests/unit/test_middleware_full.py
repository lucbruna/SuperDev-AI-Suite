"""Tests for the security middleware (headers, request ID)."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def security_app():
    """Create a test app with security middleware."""
    from backend.middleware.security import SecurityHeadersMiddleware
    from backend.middleware.request_id import RequestIDMiddleware

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/test")
    async def test_route():
        return {"ok": True}

    @app.get("/echo")
    async def echo_route(request: Request):
        return {
            "request_id": getattr(request.state, "request_id", None),
        }

    return app


class TestSecurityHeaders:
    @pytest.mark.asyncio
    async def test_x_content_type_options(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test")
        assert resp.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_referrer_policy(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test")
        assert "referrer-policy" in resp.headers

    @pytest.mark.asyncio
    async def test_permissions_policy(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test")
        assert "permissions-policy" in resp.headers


class TestRequestIDMiddleware:
    @pytest.mark.asyncio
    async def test_generates_request_id(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test")
        rid = resp.headers.get("x-request-id")
        assert rid is not None
        assert len(rid) > 0

    @pytest.mark.asyncio
    async def test_preserves_existing_request_id(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/test", headers={"X-Request-ID": "my-custom-id"})
        rid = resp.headers.get("x-request-id")
        assert rid == "my-custom-id"

    @pytest.mark.asyncio
    async def test_different_requests_get_different_ids(self, security_app):
        transport = ASGITransport(app=security_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            r1 = await client.get("/test")
            r2 = await client.get("/test")
        assert r1.headers.get("x-request-id") != r2.headers.get("x-request-id")
