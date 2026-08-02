"""End-to-end integration test for the API-key flow (finding 2f29e692).

Covers the full HTTP contract that was broken by the prefix/hash drift:
created keys must actually authenticate via ``Authorization: Bearer sk_...``.

Flow:
1. Register a user over HTTP (real JWT flow).
2. Seed an organization + membership (no public org endpoint exists).
3. ``POST /api/v1/api-keys`` with the JWT → 201 + raw ``sk_`` key.
4. ``GET /api/v1/api-keys/me`` with ``Bearer sk_...`` → 200 (authenticated).
5. Invalid / revoked keys → 401.

Loop-scope note: pytest-asyncio is configured (pytest.ini /
backend/pyproject.toml) with ``asyncio_default_fixture_loop_scope = session``
AND ``asyncio_default_test_loop_scope = session``, so every async test runs on
the SAME session event loop. The module-global async engine
(``backend/database/engine.py``) therefore binds its pooled connections to the
session loop and stays valid across tests — no more "Task attached to a
different loop" / "Event loop is closed" fragility. Each test still disposes
the engine (``finally``) to isolate pooled connections between flows.

Requires a reachable Postgres (defaults to localhost:5432 — see conftest).
"""

from __future__ import annotations

import uuid

from httpx import ASGITransport, AsyncClient

from backend.app import create_app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _reset_db_state() -> None:
    """Dispose the global engine and drop the cached session factory.

    The engine is a module singleton; resetting both globals gives each test a
    fresh engine/session factory. Safe on the shared session loop.
    """
    from backend.database import session as session_module
    from backend.database.engine import dispose_engine

    await dispose_engine()
    session_module._session_factory = None  # noqa: SLF001 — test-only reset


async def _register_user(client: AsyncClient) -> tuple[str, str, str]:
    """Register a user over HTTP; returns (user_id, jwt_access_token, email)."""
    suffix = uuid.uuid4().hex[:10]
    email = f"e2e-{suffix}@example.com"
    username = f"e2e_{suffix}"
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Str0ng!Passw0rd", "username": username},
    )
    assert reg.status_code == 201, reg.text
    data = reg.json()["data"]
    return data["user"]["id"], data["accessToken"], data["user"]["email"]


async def _seed_org_membership(user_id: str) -> str:
    """Create an org + owner membership; returns the org_id."""
    from backend.database.models.organization import Organization, OrganizationMember
    from backend.database.session import async_session_factory

    org_id = str(uuid.uuid4())
    async with async_session_factory()() as session:
        session.add(Organization(id=org_id, name="E2E Org", slug=f"e2e-{uuid.uuid4().hex[:10]}"))
        session.add(OrganizationMember(organization_id=org_id, user_id=user_id, role="owner"))
        await session.commit()
    return org_id


async def _cleanup(user_id: str, org_id: str | None) -> None:
    """Delete created rows in FK-safe order."""
    from sqlalchemy import delete

    from backend.database.models.api_key import APIKey
    from backend.database.models.organization import Organization, OrganizationMember
    from backend.database.models.user import User
    from backend.database.session import async_session_factory

    async with async_session_factory()() as session:
        await session.execute(delete(APIKey).where(APIKey.created_by == user_id))
        await session.execute(delete(OrganizationMember).where(OrganizationMember.user_id == user_id))
        if org_id:
            await session.execute(delete(Organization).where(Organization.id == org_id))
        await session.execute(delete(User).where(User.id == user_id))
        await session.commit()


# ---------------------------------------------------------------------------
# Tests (async — run on the pytest-asyncio session event loop)
# ---------------------------------------------------------------------------


async def test_api_key_create_and_authenticate_e2e() -> None:
    """POST /api/v1/api-keys creates a key; Bearer sk_ authenticates over HTTP."""
    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            user_id, jwt_token, email = await _register_user(client)
            org_id: str | None = None
            try:
                org_id = await _seed_org_membership(user_id)

                # 3. Create the key with the JWT
                created = await client.post(
                    "/api/v1/api-keys",
                    json={"name": "e2e key", "scopes": ["read"]},
                    headers={"Authorization": f"Bearer {jwt_token}"},
                )
                assert created.status_code == 201, created.text
                body = created.json()
                raw_key = body["key"]

                # Contract from the 2f29e692 fix: sk_ prefix, 24-char prefix, bcrypt hash.
                assert raw_key.startswith("sk_")
                assert len(raw_key) == 3 + 64  # sk_ + 32 random bytes as hex
                assert body["key_prefix"] == raw_key[:24]
                assert len(body["key_prefix"]) == 24  # API_KEY_PREFIX_LENGTH

                # 4. Authenticate with the raw key via Authorization: Bearer sk_...
                me = await client.get(
                    "/api/v1/api-keys/me",
                    headers={"Authorization": f"Bearer {raw_key}"},
                )
                assert me.status_code == 200, me.text
                me_body = me.json()
                assert me_body["id"] == user_id
                assert me_body["email"] == email
                assert me_body["org_id"] == org_id
                assert me_body["auth_method"] == "api_key"
            finally:
                await _cleanup(user_id, org_id)
    finally:
        await _reset_db_state()


async def test_jwt_fallback_authenticates() -> None:
    """GET /api/v1/api-keys/me accepts a Bearer JWT (fallback path in api_key_auth).

    api_key_auth (backend/auth/manager.py) treats non-``sk_`` tokens as JWTs:
    it verifies them with auth_manager.verify_token and resolves the user from
    the ``sub`` claim. The register JWT carries no ``org_id`` claim, so the
    fallback returns org=None here (org is only resolved when the JWT embeds
    ``org_id`` — covered by test_jwt_fallback_with_org_claim_resolves_org).
    """
    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            user_id, jwt_token, email = await _register_user(client)
            try:
                # 4. Authenticate with the JWT via Authorization: Bearer <jwt>
                me = await client.get(
                    "/api/v1/api-keys/me",
                    headers={"Authorization": f"Bearer {jwt_token}"},
                )
                assert me.status_code == 200, me.text
                me_body = me.json()
                assert me_body["id"] == user_id
                assert me_body["email"] == email
                # Register JWT has no org_id claim -> fallback resolves org=None.
                assert me_body["org_id"] is None
                assert me_body["org_name"] is None
            finally:
                await _cleanup(user_id, None)
    finally:
        await _reset_db_state()


async def test_jwt_fallback_with_org_claim_resolves_org() -> None:
    """A JWT embedding an ``org_id`` claim resolves the org on the fallback path.

    The fallback in api_key_auth reads ``payload.org_id`` (not DB membership),
    so minting a token that carries the claim must surface the org in the /me
    response — proving the org-resolution branch of the fallback works.
    """
    from backend.auth.jwt import get_jwt_manager

    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            user_id, _jwt_token, email = await _register_user(client)
            org_id: str | None = None
            try:
                org_id = await _seed_org_membership(user_id)
                jwt_with_org = get_jwt_manager().create_access_token(
                    subject=user_id,
                    extra_claims={"org_id": org_id},
                )

                me = await client.get(
                    "/api/v1/api-keys/me",
                    headers={"Authorization": f"Bearer {jwt_with_org}"},
                )
                assert me.status_code == 200, me.text
                me_body = me.json()
                assert me_body["id"] == user_id
                assert me_body["email"] == email
                assert me_body["org_id"] == org_id
                assert me_body["org_name"] == "E2E Org"
            finally:
                await _cleanup(user_id, org_id)
    finally:
        await _reset_db_state()


async def test_invalid_jwt_rejected() -> None:
    """A malformed Bearer token (not sk_, not a valid JWT) gets 401."""
    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get(
                "/api/v1/api-keys/me",
                headers={"Authorization": "Bearer not-a-jwt-not-an-api-key"},
            )
            assert resp.status_code == 401
    finally:
        await _reset_db_state()


async def test_invalid_api_key_rejected() -> None:
    """A malformed/unknown sk_ key gets 401 from the api_key_auth dependency."""
    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get(
                "/api/v1/api-keys/me",
                headers={"Authorization": f"Bearer sk_{'0' * 64}"},
            )
            assert resp.status_code == 401
    finally:
        await _reset_db_state()


async def test_revoked_api_key_rejected() -> None:
    """A revoked key no longer authenticates."""
    app = create_app()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            user_id, jwt_token, _email = await _register_user(client)
            org_id: str | None = None
            try:
                org_id = await _seed_org_membership(user_id)
                jwt_headers = {"Authorization": f"Bearer {jwt_token}"}

                created = await client.post(
                    "/api/v1/api-keys",
                    json={"name": "revocable"},
                    headers=jwt_headers,
                )
                assert created.status_code == 201, created.text
                raw_key = created.json()["key"]
                key_id = created.json()["id"]

                revoked = await client.delete(f"/api/v1/api-keys/{key_id}", headers=jwt_headers)
                assert revoked.status_code == 200

                me = await client.get(
                    "/api/v1/api-keys/me",
                    headers={"Authorization": f"Bearer {raw_key}"},
                )
                assert me.status_code == 401
            finally:
                await _cleanup(user_id, org_id)
    finally:
        await _reset_db_state()
