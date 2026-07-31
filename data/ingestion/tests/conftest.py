"""Shared fixtures for the Data Ingestion subsystem tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.data.data_config import DataConfig
from SuperDev.data.data_engine import DataEngine


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config() -> DataConfig:
    return DataConfig.default()


@pytest.fixture
async def engine(config: DataConfig) -> DataEngine:
    engine = DataEngine(config=config)
    await engine.start()
    yield engine
    await engine.stop()
