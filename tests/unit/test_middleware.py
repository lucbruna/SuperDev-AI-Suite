"""Unit tests for middleware.rate_limit module."""

import time

import pytest

from backend.middleware.rate_limit import CircuitBreaker, RateLimitMiddleware


class TestCircuitBreaker:
    """Tests for the CircuitBreaker resilience pattern."""

    def test_initial_state(self):
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_successful_call_resets(self):
        cb = CircuitBreaker(failure_threshold=3)

        def success():
            return "ok"

        result = cb.call(success)
        assert result == "ok"
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_failure_increments_count(self):
        cb = CircuitBreaker(failure_threshold=3)

        def fail():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            cb.call(fail)
        assert cb.failure_count == 1
        assert cb.state == "closed"

    def test_threshold_opens_circuit(self):
        cb = CircuitBreaker(failure_threshold=2)

        def fail():
            raise ValueError("fail")

        with pytest.raises(ValueError):
            cb.call(fail)
        with pytest.raises(ValueError):
            cb.call(fail)
        assert cb.state == "open"
        assert cb.failure_count == 2

    def test_open_circuit_rejects(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.state = "open"
        cb.last_failure_time = time.time()

        def success():
            return "ok"

        with pytest.raises(Exception, match="Circuit breaker is open"):
            cb.call(success)

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
        cb.state = "open"
        cb.last_failure_time = time.time() - 1.0  # 1 second ago

        def success():
            return "recovered"

        result = cb.call(success)
        assert result == "recovered"
        assert cb.state == "closed"

    def test_success_in_half_open_resets(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)
        # Trip the breaker
        def fail():
            raise ValueError("fail")

        for _ in range(2):
            try:
                cb.call(fail)
            except ValueError:
                pass
        assert cb.state == "open"

        # Wait for recovery
        time.sleep(0.02)

        def success():
            return "ok"

        cb.call(success)
        assert cb.state == "closed"
        assert cb.failure_count == 0


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware configuration."""

    def test_initialization(self):
        from unittest.mock import MagicMock

        app = MagicMock()
        middleware = RateLimitMiddleware(app, max_requests=50, window_seconds=30)
        assert middleware.max_requests == 50
        assert middleware.window_seconds == 30

    def test_default_values(self):
        from unittest.mock import MagicMock

        app = MagicMock()
        middleware = RateLimitMiddleware(app)
        assert middleware.max_requests == 100
        assert middleware.window_seconds == 60
