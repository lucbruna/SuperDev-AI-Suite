"""Shared fixtures for the Data Quality subsystem tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.data.data_config import DataConfig
from SuperDev.data.data_engine import DataEngine


@pytest.fixture
def config() -> DataConfig:
    return DataConfig.default()


@pytest.fixture
async def engine(config: DataConfig) -> DataEngine:
    engine = DataEngine(config=config)
    await engine.start()
    yield engine
    await engine.stop()
