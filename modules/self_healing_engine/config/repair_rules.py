"""Repair rules: which repairs are allowed and how they behave."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config._env import (
    env_bool,
    env_int,
    env_str,
)
from modules.self_healing_engine.config.constants import (
    REPAIR_KINDS,
    RISK_MEDIUM,
)


@dataclass(slots=True)
class RepairRulesConfig:
    """Policy governing automatic and manual repairs."""

    allowed_repair_kinds: tuple[str, ...] = REPAIR_KINDS
    max_attempts_per_repair: int = 2
    auto_approve_below_risk: str = RISK_MEDIUM
    repair_timeout_seconds: int = 120
    notify_on_failure: bool = True
    stop_on_failed_validation: bool = True

    @classmethod
    def from_env(cls) -> "RepairRulesConfig":
        return cls(
            allowed_repair_kinds=tuple(
                kind.strip()
                for kind in env_str("ALLOWED_REPAIR_KINDS", ",".join(REPAIR_KINDS))
                .split(",")
                if kind.strip()
            ),
            max_attempts_per_repair=env_int("MAX_ATTEMPTS_PER_REPAIR", 2),
            auto_approve_below_risk=env_str(
                "AUTO_APPROVE_BELOW_RISK", RISK_MEDIUM
            ),
            repair_timeout_seconds=env_int("REPAIR_TIMEOUT_SECONDS", 120),
            notify_on_failure=env_bool("NOTIFY_ON_FAILURE", True),
            stop_on_failed_validation=env_bool("STOP_ON_FAILED_VALIDATION", True),
        )

    def allows_repair_kind(self, kind: str) -> bool:
        return kind in self.allowed_repair_kinds

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed_repair_kinds": list(self.allowed_repair_kinds),
            "max_attempts_per_repair": self.max_attempts_per_repair,
            "auto_approve_below_risk": self.auto_approve_below_risk,
            "repair_timeout_seconds": self.repair_timeout_seconds,
            "notify_on_failure": self.notify_on_failure,
            "stop_on_failed_validation": self.stop_on_failed_validation,
        }
