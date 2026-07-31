"""Unit tests for the authentication rate limiter."""

from __future__ import annotations

import pytest

from backend.middleware.auth_rate_limit import AuthRateLimiter


class TestAuthRateLimiter:
    def test_allows_requests_within_limit(self) -> None:
        limiter = AuthRateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            assert limiter.is_allowed("1.2.3.4") is True

    def test_blocks_beyond_limit(self) -> None:
        limiter = AuthRateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_allowed("5.6.7.8") is True
        assert limiter.is_allowed("5.6.7.8") is True
        assert limiter.is_allowed("5.6.7.8") is False
        # Different IPs are not affected by each other.
        assert limiter.is_allowed("9.9.9.9") is True

    def test_window_expiry_allows_again(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import time

        now = [1_000_000.0]
        monkeypatch.setattr(time, "time", lambda: now[0])
        limiter = AuthRateLimiter(max_requests=1, window_seconds=5)
        assert limiter.is_allowed("1.1.1.1") is True
        assert limiter.is_allowed("1.1.1.1") is False
        now[0] += 6
        assert limiter.is_allowed("1.1.1.1") is True

    def test_reset_clears_ip(self) -> None:
        limiter = AuthRateLimiter(max_requests=1, window_seconds=60)
        assert limiter.is_allowed("2.2.2.2") is True
        assert limiter.is_allowed("2.2.2.2") is False
        limiter.reset("2.2.2.2")
        assert limiter.is_allowed("2.2.2.2") is True
