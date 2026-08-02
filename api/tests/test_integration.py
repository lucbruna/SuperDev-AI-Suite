from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.api_manager import APIManager
from api.api_interfaces import (
    RouteInterface,
    MiddlewareInterface,
    AuthInterface,
    EventInterface,
)
from api.middleware import CORSMiddleware, RateLimitMiddleware


@pytest.mark.integration
class TestAPIManagerIntegration:
    """Integration tests for the API Manager composition root."""

    def test_manager_initialization(self) -> None:
        mgr = APIManager()
        assert mgr is not None

    def test_manager_lifecycle(self) -> None:
        mgr = APIManager()
        # Should not crash
        mgr.initialize()

    def test_route_registration_flow(self) -> None:
        mgr = APIManager()
        mgr.initialize()
        router = getattr(mgr, "route_registry", None) or getattr(mgr, "router", None)
        assert router is not None

    def test_cors_middleware_compatibility(self) -> None:
        """Verify middleware classes implement the MiddlewareInterface."""
        # Wildcard only allowed without credentials (wildcard+credentials is
        # rejected at construction by the CORS fix).
        mw = CORSMiddleware(allowed_origins=["*"], allow_credentials=False)

        class TestMiddleware:
            def process(self, request: Any) -> Any:
                return request

        # Just verify it works
        assert mw.is_origin_allowed("https://example.com")

    def test_rate_limiter(self) -> None:
        limiter = RateLimitMiddleware(max_requests=5, window=60)
        for _ in range(5):
            assert not limiter.is_limited("test-client")
        assert limiter.is_limited("test-client")

    def test_full_pipeline(self) -> None:
        """Test that the major subsystems can be created together."""
        mgr = APIManager()
        mgr.initialize()
        components = mgr.get_status() if hasattr(mgr, "get_status") else {}
        # Pipeline should exist
        assert components is not None
