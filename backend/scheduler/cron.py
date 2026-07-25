from __future__ import annotations

from datetime import UTC, datetime


def parse_cron(expression: str) -> dict:
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Invalid cron expression: {expression}")
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day": parts[2],
        "month": parts[3],
        "weekday": parts[4],
    }


def cron_matches(expression: str, dt: datetime | None = None) -> bool:
    if dt is None:
        dt = datetime.now(UTC)
    parsed = parse_cron(expression)
    fields = {
        "minute": dt.minute,
        "hour": dt.hour,
        "day": dt.day,
        "month": dt.month,
        "weekday": dt.weekday(),
    }
    for field_name, value in fields.items():
        pattern = parsed[field_name]
        if pattern == "*":
            continue
        if "/" in pattern:
            _, step = pattern.split("/")
            if value % int(step) != 0:
                return False
        elif "-" in pattern:
            start, end = map(int, pattern.split("-"))
            if not (start <= value <= end):
                return False
        elif "," in pattern:
            if value not in map(int, pattern.split(",")):
                return False
        elif value != int(pattern):
            return False
    return True
