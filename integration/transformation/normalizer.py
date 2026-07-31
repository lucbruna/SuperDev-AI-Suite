"""Value normalization for transformed data."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


class Normalizer:
    """Normalizes common value types (numbers, dates, strings)."""

    def to_str(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    def to_float(self, value: Any) -> float:
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            value = value.replace(",", ".").strip()
        return float(value)

    def to_int(self, value: Any) -> int:
        if isinstance(value, bool):
            return int(value)
        return int(self.to_float(value))

    def to_date(self, value: Any) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(value)  # type: ignore[arg-type]

    def to_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "sim"}
        return bool(value)
