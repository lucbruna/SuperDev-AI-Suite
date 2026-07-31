"""Lake partitioning by date."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DatePartitioner:
    """Builds partition keys from dates (yyyy/MM/dd or yyyy/MM)."""

    def __init__(self, granularity: str = "day") -> None:
        if granularity not in ("day", "month", "year"):
            raise ValueError(f"invalid granularity: {granularity}")
        self.granularity = granularity

    def partition_key(self, date_value: Any) -> str:
        """Returns the partition folder for the given date."""
        dt = self._coerce(date_value)
        if self.granularity == "day":
            return f"{dt.year:04d}/{dt.month:02d}/{dt.day:02d}"
        if self.granularity == "month":
            return f"{dt.year:04d}/{dt.month:02d}"
        return f"{dt.year:04d}"

    def object_key(self, name: str, date_value: Any) -> str:
        return f"{self.partition_key(date_value)}/{name}"

    @staticmethod
    def _coerce(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        raise ValueError(f"cannot partition value: {value!r}")
