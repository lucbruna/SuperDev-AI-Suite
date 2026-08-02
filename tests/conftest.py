"""Shared test fixtures for the SuperDev test suite.

Provides async engine/session fixtures using SQLite in-memory (aiosqlite)
so integration tests can run without a real PostgreSQL instance.

Configure pytest via pyproject.toml or pytest.ini:
    [tool.pytest.ini_options]
    asyncio_mode = "auto"
"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.database.base import Base

# ---------------------------------------------------------------------------
# Event loop — managed by pytest-asyncio 1.x (loop scopes configured in
# pytest.ini via asyncio_default_fixture_loop_scope). The old custom
# `event_loop` fixture was removed because it conflicts with the runner.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Engine — session-scoped, creates all tables once per test run
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Session — function-scoped, transactional rollback per test
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    connection = await async_engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    # Patch models that reference Organization/Project if they aren't importable
    # by making relationships lazy so they don't fire during unit tests
    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


# ---------------------------------------------------------------------------
# HTTPX async test client
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from backend.app import create_app

    app = create_app()

    # Override the DB dependency to return our test session
    async def _override_get_db():
        yield db_session

    # Try to override common dependency names used in routes
    try:
        from backend.database import get_db
        app.dependency_overrides[get_db] = _override_get_db
    except (ImportError, AttributeError):
        pass

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------

def _generate_uuid() -> str:
    return str(uuid.uuid4())


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Create and return a standard test user."""
    from backend.auth.passwords import hash_password
    from backend.database.models.user import User

    user_id = _generate_uuid()
    user = User(
        id=user_id,
        email=f"test-{user_id[:8]}@example.com",
        username=f"testuser_{user_id[:8]}",
        hashed_password=hash_password("TestPass123!"),
        full_name="Test User",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user) -> dict[str, str]:
    """Provide JWT authorization headers for the test user."""
    from backend.config import settings

    from backend.auth.jwt import JWTManager

    jwt_mgr = JWTManager(secret_key=settings.SECRET_KEY)
    token = jwt_mgr.create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def superuser(db_session: AsyncSession):
    """Create and return a superuser."""
    from backend.auth.passwords import hash_password
    from backend.database.models.user import User

    user_id = _generate_uuid()
    user = User(
        id=user_id,
        email=f"admin-{user_id[:8]}@example.com",
        username=f"admin_{user_id[:8]}",
        hashed_password=hash_password("AdminPass123!"),
        full_name="Admin User",
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def superuser_headers(superuser) -> dict[str, str]:
    """Provide JWT authorization headers for the superuser."""
    from backend.config import settings

    from backend.auth.jwt import JWTManager

    jwt_mgr = JWTManager(secret_key=settings.SECRET_KEY)
    token = jwt_mgr.create_access_token(subject=str(superuser.id))
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Model-specific fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession, test_user):
    """Create and return a test project owned by the test user."""
    from sqlalchemy import text as sa_text
    from backend.database.models.project import Project

    # Ensure the user has an organization
    org_result = await db_session.execute(
        sa_text("SELECT id FROM organizations LIMIT 1")
    )
    org_row = org_result.fetchone()
    if org_row is None:
        org_id = _generate_uuid()
        await db_session.execute(
            sa_text("INSERT INTO organizations (id, name, slug) VALUES (:id, :name, :slug)"),
            {"id": org_id, "name": "Test Org", "slug": f"test-org-{org_id[:8]}"},
        )
    else:
        org_id = str(org_row[0])

    project_id = _generate_uuid()
    project = Project(
        id=project_id,
        name=f"Test Project {project_id[:8]}",
        description="A project created for testing",
        owner_id=str(test_user.id),
        organization_id=org_id,
        slug=f"test-project-{project_id[:8]}",
    )
    db_session.add(project)
    await db_session.flush()
    return project


@pytest_asyncio.fixture
async def test_workflow(db_session: AsyncSession, test_user, test_project):
    """Create and return a test workflow."""
    from backend.database.models.workflow import Workflow

    wf_id = _generate_uuid()
    workflow = Workflow(
        id=wf_id,
        name=f"Test Workflow {wf_id[:8]}",
        description="A workflow for testing",
        created_by=str(test_user.id),
        project_id=str(test_project.id),
        definition={"nodes": [], "edges": []},
    )
    db_session.add(workflow)
    await db_session.flush()
    return workflow


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

async def create_test_user(
    session: AsyncSession,
    email: str | None = None,
    username: str | None = None,
    is_superuser: bool = False,
) -> Any:
    """Create a user with sensible defaults and return it."""
    from backend.auth.passwords import hash_password
    from backend.database.models.user import User

    uid = _generate_uuid()
    user = User(
        id=uid,
        email=email or f"user-{uid[:8]}@test.com",
        username=username or f"user_{uid[:8]}",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
        is_superuser=is_superuser,
        is_verified=True,
    )
    session.add(user)
    await session.flush()
    return user


async def create_test_project(
    session: AsyncSession,
    owner_id: str,
    name: str | None = None,
) -> Any:
    """Create a project with sensible defaults and return it."""
    from sqlalchemy import text as sa_text
    from backend.database.models.project import Project

    # Ensure org exists
    org_result = await session.execute(sa_text("SELECT id FROM organizations LIMIT 1"))
    org_row = org_result.fetchone()
    if org_row is None:
        org_id = _generate_uuid()
        await session.execute(
            sa_text("INSERT INTO organizations (id, name, slug) VALUES (:id, :name, :slug)"),
            {"id": org_id, "name": "Test Org", "slug": f"test-org-{org_id[:8]}"},
        )
    else:
        org_id = str(org_row[0])

    pid = _generate_uuid()
    project = Project(
        id=pid,
        name=name or f"Project {pid[:8]}",
        description="Auto-created test project",
        owner_id=owner_id,
        organization_id=org_id,
        slug=f"test-{pid[:8]}",
    )
    session.add(project)
    await session.flush()
    return project
