"""Testes de integração: API de Autenticação."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://localhost:8000", timeout=60.0,
        headers={"Host": "localhost:8000"},
    ) as ac:
        yield ac


class TestAuthIntegration:
    """Testes de integração para autenticação."""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_sem_credenciais(self, client):
        response = await client.post("/api/v1/auth/login", json={})
        assert response.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_usuario_nao_autenticado(self, client):
        response = await client.get("/api/v1/users/me")
        assert response.status_code in (400, 401)

    @pytest.mark.asyncio
    async def test_api_key_invalida(self, client):
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code in (400, 401)
