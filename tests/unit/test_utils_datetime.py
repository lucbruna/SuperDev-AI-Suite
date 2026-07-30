"""Unit tests for utils.datetime module."""

from datetime import UTC, datetime, timedelta

from backend.utils.datetime import format_datetime, parse_datetime, time_ago, utc_now


class TestUtcNow:
    def test_returns_datetime_with_utc_tz(self):
        result = utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None
        assert result.tzinfo == UTC

    def test_returns_recent_time(self):
        before = datetime.now(UTC)
        result = utc_now()
        after = datetime.now(UTC)
        assert before <= result <= after


class TestFormatDatetime:
    def test_default_format(self):
        dt = datetime(2024, 6, 15, 10, 30, 45, 123456, tzinfo=UTC)
        result = format_datetime(dt)
        assert result == "2024-06-15T10:30:45.123456Z"

    def test_custom_format(self):
        dt = datetime(2024, 6, 15, 10, 30, 0, tzinfo=UTC)
        result = format_datetime(dt, fmt="%Y-%m-%d")
        assert result == "2024-06-15"


class TestParseDatetime:
    def test_default_format(self):
        result = parse_datetime("2024-06-15T10:30:45.123456Z")
        assert result.year == 2024
        assert result.month == 6
        assert result.day == 15
        assert result.tzinfo == UTC

    def test_custom_format(self):
        result = parse_datetime("2024-06-15", fmt="%Y-%m-%d")
        assert result.year == 2024
        assert result.month == 6


class TestTimeAgo:
    def test_just_now(self):
        now = utc_now()
        result = time_ago(now, reference=now)
        assert result == "just now"

    def test_minutes_ago(self):
        now = utc_now()
        past = now - timedelta(minutes=5)
        result = time_ago(past, reference=now)
        assert result == "5m ago"

    def test_hours_ago(self):
        now = utc_now()
        past = now - timedelta(hours=3)
        result = time_ago(past, reference=now)
        assert result == "3h ago"

    def test_days_ago(self):
        now = utc_now()
        past = now - timedelta(days=7)
        result = time_ago(past, reference=now)
        assert result == "7d ago"

    def test_months_ago(self):
        now = utc_now()
        past = now - timedelta(days=60)
        result = time_ago(past, reference=now)
        assert result == "2mo ago"

    def test_years_ago(self):
        now = utc_now()
        past = now - timedelta(days=400)
        result = time_ago(past, reference=now)
        assert result == "1y ago"
