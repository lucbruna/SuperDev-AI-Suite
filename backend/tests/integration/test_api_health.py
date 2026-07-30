"""Testes de health check da API."""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint_returns_200(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_structure(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    data = response.json()
    assert "status" in data
    assert "checks" in data


@pytest.mark.asyncio
async def test_health_unknown_endpoint_returns_404(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/health/unknown")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health_response_content_type(async_client: AsyncClient) -> None:
    response = await async_client.get("/health")
    assert "application/json" in response.headers["content-type"]
