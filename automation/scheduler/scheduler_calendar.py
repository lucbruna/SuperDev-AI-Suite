"""Business-day calendar helpers."""

from __future__ import annotations

from datetime import date, timedelta


class SchedulerCalendar:
    """Tracks holidays and business days."""

    def __init__(self, holidays: list[date] | None = None) -> None:
        self.holidays: set[date] = set(holidays or [])

    def add_holiday(self, day: date) -> None:
        self.holidays.add(day)

    def is_business_day(self, day: date) -> bool:
        return day.weekday() < 5 and day not in self.holidays

    def next_business_day(self, day: date) -> date:
        candidate = day + timedelta(days=1)
        while not self.is_business_day(candidate):
            candidate += timedelta(days=1)
        return candidate
