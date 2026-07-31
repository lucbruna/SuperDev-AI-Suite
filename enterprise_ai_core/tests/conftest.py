"""
Test configuration and fixtures
"""

import asyncio

import pytest


@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await asyncio.sleep(0.01)
