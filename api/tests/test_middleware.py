from __future__ import annotations

import sys
from typing import Any

import pytest  # type: ignore[import-untyped]

sys.path.insert(0, "SuperDev")

from api.middleware import CORSMiddleware, LoggingMiddleware, RateLimitMiddleware, RequestIDMiddleware  # noqa: E402


class TestCORSMiddleware:
    def test_allows_origin(self) -> None:
        mw = CORSMiddleware(allowed_origins=["https://example.com"])
        assert mw.is_origin_allowed("https://example.com")
        assert not mw.is_origin_allowed("https://evil.com")

    def test_allows_all_origins(self) -> None:
        # Wildcard origins are only allowed without credentials (the
        # wildcard+credentials combination is rejected at construction).
        mw = CORSMiddleware(allowed_origins=["*"], allow_credentials=False)
        assert mw.is_origin_allowed("https://anything.com")

    def test_rejects_wildcard_with_credentials(self) -> None:
        with pytest.raises(ValueError, match="wildcard origin"):
            CORSMiddleware(allowed_origins=["*"], allow_credentials=True)

    def test_default_origins_are_explicit(self) -> None:
        # CORS_DEFAULT_ORIGINS is now [] — no wildcard, no implicit open CORS.
        mw = CORSMiddleware(allow_credentials=False)
        assert not mw.is_origin_allowed("https://anything.com")


class TestLoggingMiddleware:
    def test_initialization(self) -> None:
        mw = LoggingMiddleware()
        assert mw is not None


class TestRateLimitMiddleware:
    def test_initialization(self) -> None:
        mw = RateLimitMiddleware()
        assert mw is not None

    def test_is_limited(self) -> None:
        mw = RateLimitMiddleware(max_requests=3, window=60)
        client_id = "test-client"
        assert not mw.is_limited(client_id)
        assert not mw.is_limited(client_id)
        assert not mw.is_limited(client_id)
        assert mw.is_limited(client_id)

    def test_reset_window(self) -> None:
        mw = RateLimitMiddleware(max_requests=2, window=0)
        client_id = "test-client"
        # window=0 means it always resets
        assert not mw.is_limited(client_id)

    def test_bucket_map_is_bounded(self) -> None:
        """The bucket map must cap at _max_buckets (memory bound)."""
        mw = RateLimitMiddleware()
        # Override the cap to something tiny to exercise eviction.
        mw._max_buckets = 2
        for i in range(10):
            mw.is_limited(f"client-{i}")
        assert len(mw._buckets) <= 2


class TestRequestIDMiddleware:
    def test_generate_id(self) -> None:
        mw = RequestIDMiddleware()
        request_id = mw.generate_id()
        assert request_id is not None
        assert len(request_id) > 0

    def test_unique_ids(self) -> None:
        mw = RequestIDMiddleware()
        ids = {mw.generate_id() for _ in range(100)}
        assert len(ids) == 100
