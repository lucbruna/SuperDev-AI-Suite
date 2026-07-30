"""Tests for the Prometheus metrics endpoint."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def metrics_app():
    """Create a minimal FastAPI app with just the metrics router."""
    from fastapi import FastAPI
    from backend.api.v1.metrics import router
    app = FastAPI()
    app.include_router(router)
    return app


class TestPrometheusMetrics:
    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_200(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_metrics_returns_prometheus_format(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics")
        body = resp.text
        assert "superdev_uptime_seconds" in body
        assert "superdev_http_requests_total" in body
        assert "# HELP" in body
        assert "# TYPE" in body

    @pytest.mark.asyncio
    async def test_metrics_content_type_is_text_plain(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics")
        assert "text/plain" in resp.headers["content-type"]

    @pytest.mark.asyncio
    async def test_metrics_json_endpoint(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics/json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "uptime_seconds" in data["data"]

    @pytest.mark.asyncio
    async def test_metrics_reflects_requests(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Hit the JSON endpoint a few times
            for _ in range(3):
                await client.get("/metrics/json")
            # Now check Prometheus metrics
            resp = await client.get("/metrics")
        body = resp.text
        assert "superdev_http_requests_total" in body

    @pytest.mark.asyncio
    async def test_metrics_includes_info(self, metrics_app):
        transport = ASGITransport(app=metrics_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/metrics")
        body = resp.text
        assert 'superdev_info{version="5.0.0"' in body
