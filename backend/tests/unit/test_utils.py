from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime, timedelta

import pytest

from backend.utils.datetime import format_datetime, parse_datetime, time_ago, utc_now
from backend.utils.retry import async_retry
from backend.utils.string_utils import slugify, truncate
from backend.utils.uuid_utils import generate_uuid, is_valid_uuid


class TestDatetimeUtils:
    def test_utc_now_returns_utc(self) -> None:
        now = utc_now()
        assert now.tzinfo is not None
        assert now.tzinfo.utcoffset(now) == timedelta(0)

    def test_utc_now_returns_datetime(self) -> None:
        assert isinstance(utc_now(), datetime)

    def test_format_datetime_default_format(self) -> None:
        dt = datetime(2024, 1, 15, 10, 30, 0, 123456, tzinfo=UTC)
        formatted = format_datetime(dt)
        assert formatted == "2024-01-15T10:30:00.123456Z"

    def test_format_datetime_custom_format(self) -> None:
        dt = datetime(2024, 1, 15, tzinfo=UTC)
        formatted = format_datetime(dt, "%Y-%m-%d")
        assert formatted == "2024-01-15"

    def test_parse_datetime(self) -> None:
        value = "2024-01-15T10:30:00.123456Z"
        parsed = parse_datetime(value)
        assert parsed.year == 2024
        assert parsed.month == 1
        assert parsed.day == 15
        assert parsed.tzinfo is not None

    def test_parse_datetime_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_datetime("not-a-date")

    def test_time_ago_just_now(self) -> None:
        now = utc_now()
        assert time_ago(now) == "just now"

    def test_time_ago_minutes(self) -> None:
        now = utc_now()
        past = now - timedelta(minutes=5)
        assert time_ago(past, now) == "5m ago"

    def test_time_ago_hours(self) -> None:
        now = utc_now()
        past = now - timedelta(hours=3)
        assert time_ago(past, now) == "3h ago"

    def test_time_ago_days(self) -> None:
        now = utc_now()
        past = now - timedelta(days=7)
        assert time_ago(past, now) == "7d ago"

    def test_time_ago_months(self) -> None:
        now = utc_now()
        past = now - timedelta(days=45)
        assert time_ago(past, now) == "1mo ago"

    def test_time_ago_years(self) -> None:
        now = utc_now()
        past = now - timedelta(days=400)
        assert time_ago(past, now) == "1y ago"

    def test_time_ago_without_reference(self) -> None:
        past = utc_now() - timedelta(minutes=10)
        result = time_ago(past)
        assert isinstance(result, str)
        assert "m ago" in result


class TestUUIDUtils:
    def test_generate_uuid_returns_string(self) -> None:
        result = generate_uuid()
        assert isinstance(result, str)

    def test_generate_uuid_format(self) -> None:
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        for _ in range(10):
            assert re.match(pattern, generate_uuid(), re.IGNORECASE)

    def test_generate_uuid_unique(self) -> None:
        uuids = {generate_uuid() for _ in range(100)}
        assert len(uuids) == 100

    def test_is_valid_uuid_valid(self) -> None:
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        assert is_valid_uuid(uuid_str) is True

    def test_is_valid_uuid_invalid(self) -> None:
        assert is_valid_uuid("not-a-uuid") is False

    def test_is_valid_uuid_empty(self) -> None:
        assert is_valid_uuid("") is False

    def test_is_valid_uuid_case_insensitive(self) -> None:
        upper = "550E8400-E29B-41D4-A716-446655440000"
        assert is_valid_uuid(upper) is True


class TestStringUtils:
    @pytest.mark.parametrize(
        ("input_str", "expected"),
        [
            ("Hello World", "hello-world"),
            ("  Hello   World  ", "hello-world"),
            ("Hello!@#$World", "helloworld"),
            ("  spaces  ", "spaces"),
            ("already-slugified", "already-slugified"),
            ("", ""),
            ("---hello---", "hello"),
        ],
    )
    def test_slugify(self, input_str: str, expected: str) -> None:
        assert slugify(input_str) == expected

    def test_slugify_with_unicode(self) -> None:
        assert slugify("café") == "cafe"

    def test_truncate_short_string(self) -> None:
        assert truncate("Hello", max_length=10) == "Hello"

    def test_truncate_exact_length(self) -> None:
        assert truncate("Hello World", max_length=11) == "Hello World"

    def test_truncate_long_string(self) -> None:
        result = truncate("Hello World This Is Long", max_length=10)
        assert result == "Hello ..."
        assert len(result) <= 10

    def test_truncate_custom_suffix(self) -> None:
        result = truncate("Hello World This Is Long", max_length=10, suffix="!!")
        assert result == "Hello !!"
        assert result.endswith("!!")

    def test_truncate_empty_string(self) -> None:
        assert truncate("", max_length=10) == ""


class TestRetryDecorator:
    @pytest.mark.asyncio
    async def test_retry_success_first_attempt(self) -> None:
        call_count = 0

        @async_retry(max_retries=3, delay=0.01)
        async def succeeds() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await succeeds()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_success_after_retries(self) -> None:
        call_count = 0

        @async_retry(max_retries=3, delay=0.01)
        async def fails_twice() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary failure")
            return "success"

        result = await fails_twice()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_fails_after_max_retries(self) -> None:
        call_count = 0

        @async_retry(max_retries=3, delay=0.01)
        async def always_fails() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("persistent failure")

        with pytest.raises(ValueError, match="persistent failure"):
            await always_fails()
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_only_catches_specified_exceptions(self) -> None:
        @async_retry(max_retries=2, delay=0.01, exceptions=(ValueError,))
        async def raises_type_error() -> str:
            raise TypeError("not caught")

        with pytest.raises(TypeError):
            await raises_type_error()

    @pytest.mark.asyncio
    async def test_retry_with_backoff(self) -> None:
        call_count = 0
        delays: list[float] = []

        original_sleep = asyncio.sleep

        async def tracking_sleep(delay: float) -> None:
            delays.append(delay)
            await original_sleep(delay)

        @async_retry(max_retries=3, delay=0.01, backoff=2.0)
        async def fails_with_backoff() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await fails_with_backoff()

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_single_attempt(self) -> None:
        call_count = 0

        @async_retry(max_retries=1, delay=0.01)
        async def single_attempt() -> str:
            nonlocal call_count
            call_count += 1
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            await single_attempt()
        assert call_count == 1