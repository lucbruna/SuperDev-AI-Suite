from __future__ import annotations

import pytest

from SuperDev.monitoring.recovery.recovery_manager import RecoveryManager
from SuperDev.monitoring.recovery.action import ActionExecutor
from SuperDev.monitoring.recovery.rollback import RollbackManager
from SuperDev.monitoring.recovery.failover import FailoverManager
from SuperDev.monitoring.recovery.circuit_breaker import CircuitBreaker, CircuitBreakerOpenError
from SuperDev.monitoring.recovery.retry import RetryHandler


class TestRecoveryManager:
    def test_execute_action(self) -> None:
        mgr = RecoveryManager()
        mgr.execute_action(
            action_type="restart",
            target="svc",
            reason="test",
        )
        assert len(mgr._actions) == 1


class TestActionExecutor:
    def test_execute(self) -> None:
        exec_ = ActionExecutor()
        exec_.register_action("echo", lambda: None)
        # execute registered action
        exec_.execute("echo")  # should not raise


class TestRollbackManager:
    def test_checkpoint_and_rollback(self) -> None:
        mgr = RollbackManager()
        mgr.checkpoint("state1", {"key": "val"})
        assert mgr.has_checkpoint("state1")
        assert mgr.rollback("state1") is True


class TestFailoverManager:
    def test_failover(self) -> None:
        mgr = FailoverManager()
        mgr.configure(primary="p1", standby="s1")
        assert mgr.active == "p1"
        mgr.failover()
        assert mgr.active == "s1"
        assert mgr.is_failed_over is True


class TestCircuitBreaker:
    def test_closed_to_open(self) -> None:
        cb = CircuitBreaker(name="test", failure_threshold=2)
        assert cb.state.value == "closed"

        def failing() -> None:
            raise ValueError("fail")

        for _ in range(2):
            try:
                cb.call(failing)
            except (ValueError, CircuitBreakerOpenError):
                pass

        assert cb.state.value == "open"


class TestRetryHandler:
    def test_retry_failure(self) -> None:
        handler = RetryHandler(max_retries=1, base_delay=0.01)

        call_count = 0

        def failing() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            handler.execute(failing)

        assert call_count == 2
