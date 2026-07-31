"""Shared fixtures for the performance subsystem deep-dive tests."""

from __future__ import annotations

import asyncio

import pytest

from SuperDev.quality.quality_engine import QualityEngine


@pytest.fixture
async def engine() -> QualityEngine:
    engine = QualityEngine()
    await engine.start()
    yield engine
    await engine.stop()
