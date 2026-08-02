"""Shared test fixtures for backend unit/integration tests."""

from __future__ import annotations

import os

# The .env AND the shell both point DATABASE_URL at the docker-internal
# ``postgres`` host, which is NOT resolvable from the test host (getaddrinfo
# fails). Tests must reach the running Postgres via localhost, so we FORCE
# DATABASE_URL here (setdefault would keep the unresolvable docker host).
# Override with SUPERDEV_TEST_DATABASE_URL to point elsewhere (e.g. CI).
os.environ["DATABASE_URL"] = os.environ.get(
    "SUPERDEV_TEST_DATABASE_URL",
    "postgresql+asyncpg://superdev:superdev@localhost:5432/superdev",
)

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from backend.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}
