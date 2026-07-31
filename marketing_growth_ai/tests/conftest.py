"""
Test configuration for marketing_growth_ai
"""

import pytest
import asyncio


@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await asyncio.sleep(0.01)