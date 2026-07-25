import pytest
from httpx import AsyncClient, ASGITransport
from backend.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.mark.asyncio
async def test_health_check(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200