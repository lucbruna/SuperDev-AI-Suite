"""
Test configuration for marketing_growth_ai
"""

import pytest
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def cleanup():
    yield
    await asyncio.sleep(0.01)