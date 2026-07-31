"""5-field cron expression parser."""

from __future__ import annotations

from datetime import datetime, timedelta


def _first_of_next_month(dt: datetime) -> datetime:
    return (dt.replace(day=28) + timedelta(days=4)).replace(day=1,
                                                            hour=0, minute=0)


class CronParser:
    """Parses cron expressions like ``0 8 * * *``.

    Fields: minute hour day-of-month month day-of-week.
    Supports ``*``, ``*/n``, ``a-b``, ``a-b/n``, and comma lists.
    Day-of-week: 0-7 with 0 and 7 meaning Sunday.
    """

    def __init__(self, expression: str) -> None:
        self.expression = expression
        parts = expression.split()
        if len(parts) != 5:
            raise ValueError(
                f"cron expression must have 5 fields, got {len(parts)}: {expression!r}")
        self.minutes = self._parse_field(parts[0], 0, 59)
        self.hours = self._parse_field(parts[1], 0, 23)
        self.dom = self._parse_field(parts[2], 1, 31)
        self.months = self._parse_field(parts[3], 1, 12)
        self.dow = self._parse_dow(parts[4])

    # -- parsing -----------------------------------------------------------
    @staticmethod
    def _expand(token: str, lo: int, hi: int) -> set[int]:
        if token == "*":
            return set(range(lo, hi + 1))
        if token.startswith("*/"):
            step = int(token[2:])
            return set(range(lo, hi + 1, step))
        if "/" in token and "-" in token:
            rng, _, step = token.partition("/")
            a, b = rng.split("-")
            return set(range(int(a), int(b) + 1, int(step)))
        if "-" in token:
            a, b = token.split("-")
            return set(range(int(a), int(b) + 1))
        if "," in token:
            result: set[int] = set()
            for part in token.split(","):
                result |= CronParser._expand(part, lo, hi)
            return result
        return {int(token)}

    @staticmethod
    def _parse_field(field: str, lo: int, hi: int) -> set[int]:
        return CronParser._expand(field, lo, hi)

    @staticmethod
    def _parse_dow(field: str) -> set[int]:
        values = CronParser._expand(field, 0, 7)
        # Normalize to Python isoweekday: Monday=1 .. Sunday=7.
        return {7 if v == 0 else v for v in values}

    # -- matching ----------------------------------------------------------
    def matches(self, dt: datetime) -> bool:
        if dt.month not in self.months:
            return False
        if not self._day_matches(dt):
            return False
        if dt.hour not in self.hours:
            return False
        if dt.minute not in self.minutes:
            return False
        return True

    def _day_matches(self, dt: datetime) -> bool:
        dom_restricted = self.dom != set(range(1, 32))
        dow_restricted = self.dow != set(range(1, 8))
        dom_ok = dt.day in self.dom
        dow_ok = dt.isoweekday() in self.dow
        if dom_restricted and dow_restricted:
            return dom_ok or dow_ok
        if dom_restricted:
            return dom_ok
        if dow_restricted:
            return dow_ok
        return True

    # -- next occurrence ---------------------------------------------------
    def next_after(self, after: datetime) -> datetime | None:
        cur = after.replace(second=0, microsecond=0) + timedelta(minutes=1)
        while cur.year <= after.year + 5:
            if cur.month not in self.months:
                cur = _first_of_next_month(cur)
                continue
            if not self._day_matches(cur):
                cur = (cur + timedelta(days=1)).replace(hour=0, minute=0)
                continue
            if cur.hour not in self.hours:
                cur = cur.replace(minute=0) + timedelta(hours=1)
                continue
            if cur.minute not in self.minutes:
                cur += timedelta(minutes=1)
                continue
            return cur
        return None
