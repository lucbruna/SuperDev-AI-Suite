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

# The JWT manager rejects placeholder secrets (see backend/auth/jwt.py), and
# the shell may export a stale placeholder that overrides .env — so tests
# FORCE a dedicated test key, exactly like DATABASE_URL above.
os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "SUPERDEV_TEST_JWT_SECRET",
    "test-only-secret-key-superdev-e2e",
)

# Tests must not attempt to export traces/metrics to a local OTLP collector
# — forced, like JWT_SECRET_KEY, so a developer's shell export can't turn
# telemetry back on mid-suite.
os.environ["OTEL_ENABLED"] = "false"

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
