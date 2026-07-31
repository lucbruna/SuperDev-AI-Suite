"""Shared fixtures for the Testing & Quality Engine tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.quality.quality_config import QualityConfig
from SuperDev.quality.quality_engine import QualityEngine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config() -> QualityConfig:
    return QualityConfig.default()


@pytest.fixture
async def engine(config: QualityConfig) -> QualityEngine:
    engine = QualityEngine(config=config)
    await engine.start()
    yield engine
    await engine.stop()
