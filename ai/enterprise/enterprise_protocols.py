"""Enterprise protocols."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Billable(Protocol):
    def calculate_charge(self) -> float: ...
    def get_billing_items(self) -> list: ...


@runtime_checkable
class Subscribable(Protocol):
    def get_subscription_status(self) -> str: ...
    def get_plan_features(self) -> dict[str, Any]: ...


@runtime_checkable
class Licensable(Protocol):
    def get_license_key(self) -> str: ...
    def is_license_valid(self) -> bool: ...


@runtime_checkable
class Trackable(Protocol):
    def get_usage(self) -> dict[str, float]: ...
    def get_quota_remaining(self) -> dict[str, float]: ...


@runtime_checkable
class Reportable(Protocol):
    def generate_report(self, report_type: str = "") -> dict[str, Any]: ...
