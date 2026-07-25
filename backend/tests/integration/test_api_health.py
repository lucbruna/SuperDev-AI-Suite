from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint_returns_200(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_structure(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] in ("healthy", "degraded")
    assert "version" in data["data"]
    assert "timestamp" in data["data"]
    assert "checks" in data["data"]


@pytest.mark.asyncio
async def test_readiness_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_liveness_check(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/alive")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_all_health_endpoints_consistent(client: AsyncClient) -> None:
    health = await client.get("/api/v1/health")
    ready = await client.get("/api/v1/health/ready")
    alive = await client.get("/api/v1/health/alive")

    assert health.status_code == 200
    assert ready.status_code == 200
    assert alive.status_code == 200

    health_data = health.json()
    ready_data = ready.json()
    alive_data = alive.json()

    assert health_data["data"]["version"] == ready_data["version"] == alive_data["version"]
    assert health_data["success"] is True


@pytest.mark.asyncio
async def test_health_unknown_endpoint_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health/unknown")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_response_content_type(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_health_version_matches(client: AsyncClient) -> None:
    response = await client.get("/api/v1/health")
    assert response.json()["data"]["version"] == "5.0.0"