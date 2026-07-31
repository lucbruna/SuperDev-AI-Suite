"""Shared fixtures for the Security Engine tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.security.security_config import SecurityConfig
from SuperDev.security.security_engine import SecurityEngine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config() -> SecurityConfig:
    return SecurityConfig.default()


@pytest.fixture
async def engine(config: SecurityConfig) -> SecurityEngine:
    engine = SecurityEngine(config=config)
    await engine.start()
    yield engine
    await engine.stop()
