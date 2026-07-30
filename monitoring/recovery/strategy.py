from __future__ import annotations

from typing import Any

from ..monitoring_models import RecoveryAction


class RecoveryStrategy:
    """Base strategies for common recovery actions."""

    @staticmethod
    def restart(target: str) -> None:
        from ..monitoring_models import RecoveryAction
        action = RecoveryAction(
            action_type="restart",
            target=target,
            reason=f"Restarting {target}",
        )
        action.status = "running"
        try:
            import logging
            logging.getLogger("superdev.recovery").info(
                "Restarting %s...", target
            )
            action.status = "succeeded"
        except Exception:
            action.status = "failed"
        action.completed_at = __import__("time").time()

    @staticmethod
    def log_only(action: RecoveryAction) -> None:
        import logging
        logger = logging.getLogger("superdev.recovery")
        logger.info(
            "Recovery action: %s on %s (reason: %s)",
            action.action_type, action.target, action.reason,
        )

    @staticmethod
    def compose(*strategies: Any) -> Any:
        def combined(action: RecoveryAction) -> None:
            for strategy in strategies:
                strategy(action)
        return combined
