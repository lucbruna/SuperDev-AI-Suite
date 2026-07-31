"""Shared fixtures for the analysis subsystem deep-dive tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.quality.quality_engine import QualityEngine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def engine() -> QualityEngine:
    engine = QualityEngine()
    await engine.start()
    yield engine
    await engine.stop()
