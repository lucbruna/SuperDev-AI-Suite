"""Pytest fixtures for CLI tests."""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.base_url = "http://localhost:8000"
    client.api_key = "test-key"
    return client


@pytest.fixture
def mock_api():
    api = MagicMock()
    api.get.return_value = {"status": "ok"}
    return api
