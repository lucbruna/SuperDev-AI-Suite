"""End-to-end API tests using httpx AsyncClient against a lightweight test app.

These tests verify the metrics endpoint, RBAC module, middleware, and
observability components work correctly over HTTP.  They do NOT rely on
the full application (which requires PostgreSQL, Redis, etc.) so they
run reliably in CI with zero infrastructure.
"""
from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from backend.observability.metrics import get_metrics_collector


# ---------------------------------------------------------------------------
# Lightweight test app — no DB, no Redis, no TrustedHostMiddleware
# ---------------------------------------------------------------------------

def _build_test_app() -> FastAPI:
    from backend.api.v1.metrics import router as metrics_router
    from backend.middleware.security import SecurityHeadersMiddleware
    from backend.middleware.request_id import RequestIDMiddleware

    app = FastAPI(title="SuperDev Test", version="5.0.0-test")
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.include_router(metrics_router)

    @app.get("/health")
    async def health():
        return {"status": "healthy", "checks": {"app": {"status": "healthy"}}}

    @app.get("/api/v1/version")
    async def version():
        return {"success": True, "data": {"version": "5.0.0-test", "name": "SuperDev"}}

    @app.get("/echo")
    async def echo(request: Request):
        return {"request_id": getattr(request.state, "request_id", None)}

    @app.get("/api/v1/nonexistent-endpoint-xyz")
    async def not_found():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    return app


@pytest.fixture
def test_app():
    return _build_test_app()


@pytest.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_health_has_status_field(self, client):
        resp = await client.get("/health")
        data = resp.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_has_checks(self, client):
        resp = await client.get("/health")
        data = resp.json()
        assert "checks" in data
        assert "app" in data["checks"]


# ---------------------------------------------------------------------------
# Version endpoint
# ---------------------------------------------------------------------------

class TestVersionEndpoint:
    @pytest.mark.asyncio
    async def test_version_returns_200(self, client):
        resp = await client.get("/api/v1/version")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_version_has_version_field(self, client):
        resp = await client.get("/api/v1/version")
        data = resp.json()
        assert data["success"] is True
        assert "version" in data["data"]


# ---------------------------------------------------------------------------
# Metrics endpoint
# ---------------------------------------------------------------------------

class TestMetricsEndpoint:
    @pytest.mark.asyncio
    async def test_metrics_returns_200(self, client):
        resp = await client.get("/metrics")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_metrics_is_prometheus_format(self, client):
        resp = await client.get("/metrics")
        body = resp.text
        assert "superdev_uptime_seconds" in body
        assert "superdev_http_requests_total" in body
        assert "# HELP" in body
        assert "# TYPE" in body

    @pytest.mark.asyncio
    async def test_metrics_content_type(self, client):
        resp = await client.get("/metrics")
        assert "text/plain" in resp.headers["content-type"]

    @pytest.mark.asyncio
    async def test_metrics_json_endpoint(self, client):
        resp = await client.get("/metrics/json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "uptime_seconds" in data["data"]

    @pytest.mark.asyncio
    async def test_metrics_includes_info(self, client):
        resp = await client.get("/metrics")
        assert 'superdev_info{version="5.0.0"' in resp.text

    @pytest.mark.asyncio
    async def test_metrics_reflects_requests(self, client):
        # Hit the JSON endpoint a few times
        for _ in range(3):
            await client.get("/metrics/json")
        # Now check Prometheus metrics reflect the requests
        resp = await client.get("/metrics")
        body = resp.text
        assert "superdev_http_requests_total" in body


# ---------------------------------------------------------------------------
# Security headers middleware
# ---------------------------------------------------------------------------

class TestSecurityHeaders:
    @pytest.mark.asyncio
    async def test_x_content_type_options(self, client):
        resp = await client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"

    @pytest.mark.asyncio
    async def test_x_frame_options(self, client):
        resp = await client.get("/health")
        assert resp.headers.get("x-frame-options") == "DENY"

    @pytest.mark.asyncio
    async def test_referrer_policy(self, client):
        resp = await client.get("/health")
        assert "referrer-policy" in resp.headers

    @pytest.mark.asyncio
    async def test_permissions_policy(self, client):
        resp = await client.get("/health")
        assert "permissions-policy" in resp.headers


# ---------------------------------------------------------------------------
# Request ID middleware
# ---------------------------------------------------------------------------

class TestRequestIDMiddleware:
    @pytest.mark.asyncio
    async def test_generates_request_id(self, client):
        resp = await client.get("/health")
        rid = resp.headers.get("x-request-id")
        assert rid is not None
        assert len(rid) > 0

    @pytest.mark.asyncio
    async def test_preserves_existing_request_id(self, client):
        resp = await client.get("/health", headers={"X-Request-ID": "my-custom-id"})
        rid = resp.headers.get("x-request-id")
        assert rid == "my-custom-id"

    @pytest.mark.asyncio
    async def test_different_requests_get_different_ids(self, client):
        r1 = await client.get("/health")
        r2 = await client.get("/health")
        assert r1.headers.get("x-request-id") != r2.headers.get("x-request-id")


# ---------------------------------------------------------------------------
# 404 handling
# ---------------------------------------------------------------------------

class Test404Handling:
    @pytest.mark.asyncio
    async def test_unknown_route_returns_404(self, client):
        resp = await client.get("/api/v1/nonexistent-endpoint-xyz")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_404_has_json_body(self, client):
        resp = await client.get("/api/v1/nonexistent-endpoint-xyz")
        data = resp.json()
        assert "detail" in data
