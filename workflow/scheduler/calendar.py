from __future__ import annotations

import datetime
from typing import Any


class WorkflowCalendar:
    """Business calendar for scheduling constraints."""

    def __init__(self) -> None:
        self._holidays: set[datetime.date] = set()
        self._working_hours: tuple[int, int] = (9, 18)

    @property
    def holidays(self) -> set[datetime.date]:
        return self._holidays

    @holidays.setter
    def holidays(self, dates: set[datetime.date]) -> None:
        self._holidays = dates

    @property
    def working_hours(self) -> tuple[int, int]:
        return self._working_hours

    @working_hours.setter
    def working_hours(self, hours: tuple[int, int]) -> None:
        self._working_hours = hours

    def is_work_day(self, day: datetime.date) -> bool:
        return day.weekday() < 5 and day not in self._holidays

    def is_work_hour(self, dt: datetime.datetime) -> bool:
        return self._working_hours[0] <= dt.hour < self._working_hours[1]

    def next_work_time(self, dt: datetime.datetime | None = None) -> datetime.datetime:
        now = dt or datetime.datetime.now()
        while not self.is_work_day(now.date()):
            now += datetime.timedelta(days=1)
            now = now.replace(hour=self._working_hours[0], minute=0, second=0)
        if not self.is_work_hour(now):
            now = now.replace(hour=self._working_hours[0], minute=0, second=0)
        return now
