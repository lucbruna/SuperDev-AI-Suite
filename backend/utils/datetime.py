from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
    return dt.strftime(fmt)


def parse_datetime(value: str, fmt: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> datetime:
    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


def time_ago(dt: datetime, reference: datetime | None = None) -> str:
    if reference is None:
        reference = utc_now()
    diff = reference - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 30:
        return f"{days}d ago"
    months = days // 30
    if months < 12:
        return f"{months}mo ago"
    years = months // 12
    return f"{years}y ago"
