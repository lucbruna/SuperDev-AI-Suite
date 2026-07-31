"""Tests for the scheduler subsystem (Volume 20, Fase 3)."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from automation.automation_events import AutomationEventType, AutomationEvents
from automation.automation_metrics import AutomationMetrics
from automation.scheduler.scheduler_calendar import SchedulerCalendar
from automation.scheduler.scheduler_engine import SchedulerEngine
from automation.scheduler.scheduler_models import SchedulerJob
from automation.scheduler.scheduler_parser import CronParser
from automation.scheduler.scheduler_planner import SchedulerPlanner


# ---------------------------------------------------------------------------
# cron parser
# ---------------------------------------------------------------------------
class TestCronParser:
    def test_field_parsing(self) -> None:
        parser = CronParser("0 8 * * *")
        assert parser.minutes == {0}
        assert parser.hours == {8}
        assert parser.dom == set(range(1, 32))
        assert parser.months == set(range(1, 13))
        assert parser.dow == set(range(1, 8))

    def test_steps_lists_and_ranges(self) -> None:
        assert CronParser("*/15 * * * *").minutes == {0, 15, 30, 45}
        assert CronParser("0 9,18 * * *").hours == {9, 18}
        assert CronParser("0 8-10 * * *").hours == {8, 9, 10}
        assert CronParser("0 * 1-15 * *").dom == set(range(1, 16))

    def test_dow_zero_means_sunday(self) -> None:
        parser = CronParser("0 18 * * 0")
        assert 7 in parser.dow  # python isoweekday Sunday
        assert parser.matches(datetime(2026, 7, 26, 18, 0))  # a Sunday

    def test_invalid_expression_raises(self) -> None:
        with pytest.raises(ValueError):
            CronParser("0 8 * *")

    def test_matches_daily(self) -> None:
        parser = CronParser("0 8 * * *")
        assert parser.matches(datetime(2026, 7, 30, 8, 0)) is True
        assert parser.matches(datetime(2026, 7, 30, 8, 1)) is False
        assert parser.matches(datetime(2026, 7, 30, 7, 0)) is False

    def test_next_after_daily(self) -> None:
        parser = CronParser("0 8 * * *")
        nxt = parser.next_after(datetime(2026, 7, 30, 7, 30))
        assert nxt == datetime(2026, 7, 30, 8, 0)
        nxt = parser.next_after(datetime(2026, 7, 30, 8, 30))
        assert nxt == datetime(2026, 7, 31, 8, 0)

    def test_next_after_weekday(self) -> None:
        # sexta-feira 18:00
        parser = CronParser("0 18 * * 5")
        # 2026-07-30 é quinta-feira
        nxt = parser.next_after(datetime(2026, 7, 30, 12, 0))
        assert nxt == datetime(2026, 7, 31, 18, 0)

    def test_next_after_monthly(self) -> None:
        parser = CronParser("0 2 1 * *")
        nxt = parser.next_after(datetime(2026, 7, 15, 10, 0))
        assert nxt == datetime(2026, 8, 1, 2, 0)

    def test_next_after_quarter_hour(self) -> None:
        parser = CronParser("*/15 * * * *")
        assert parser.next_after(datetime(2026, 7, 30, 10, 2)) \
            == datetime(2026, 7, 30, 10, 15)


# ---------------------------------------------------------------------------
# calendar
# ---------------------------------------------------------------------------
class TestSchedulerCalendar:
    def test_business_days(self) -> None:
        calendar = SchedulerCalendar()
        # 2026-07-30 é quinta-feira, 2026-08-01 é sábado
        assert calendar.is_business_day(date(2026, 7, 30)) is True
        assert calendar.is_business_day(date(2026, 8, 1)) is False
        assert calendar.is_business_day(date(2026, 8, 2)) is False

    def test_holiday(self) -> None:
        calendar = SchedulerCalendar([date(2026, 7, 31)])
        assert calendar.is_business_day(date(2026, 7, 31)) is False
        calendar.add_holiday(date(2026, 7, 30))
        assert calendar.is_business_day(date(2026, 7, 30)) is False

    def test_next_business_day(self) -> None:
        calendar = SchedulerCalendar()
        # sexta -> segunda
        assert calendar.next_business_day(date(2026, 7, 31)) \
            == date(2026, 8, 3)


# ---------------------------------------------------------------------------
# planner
# ---------------------------------------------------------------------------
class TestSchedulerPlanner:
    def _job(self) -> SchedulerJob:
        return SchedulerJob("j1", "wf-relatorio", cron="0 8 * * *")

    def test_next_run_cron(self) -> None:
        planner = SchedulerPlanner()
        nxt = planner.next_run(self._job(), after=datetime(2026, 7, 30, 7, 0))
        assert nxt == datetime(2026, 7, 30, 8, 0)

    def test_next_run_interval(self) -> None:
        planner = SchedulerPlanner()
        job = SchedulerJob("j2", "wf-monitor", interval_seconds=3600)
        nxt = planner.next_run(job, after=datetime(2026, 7, 30, 10, 0))
        assert nxt == datetime(2026, 7, 30, 11, 0)

    def test_next_runs_sequence(self) -> None:
        planner = SchedulerPlanner()
        runs = planner.next_runs(self._job(), count=3,
                                 after=datetime(2026, 7, 30, 7, 0))
        assert runs == [datetime(2026, 7, 30, 8, 0),
                        datetime(2026, 7, 31, 8, 0),
                        datetime(2026, 8, 1, 8, 0)]

    def test_job_without_schedule(self) -> None:
        job = SchedulerJob("j3", "wf-x")
        assert SchedulerPlanner().next_run(job, after=datetime(2026, 7, 30)) is None


# ---------------------------------------------------------------------------
# engine
# ---------------------------------------------------------------------------
class TestSchedulerEngine:
    def test_add_job_computes_next_run(self) -> None:
        engine = SchedulerEngine()
        job = engine.add_job("relatorio-diario", "wf-relatorio-financeiro",
                             cron="0 8 * * *")
        assert engine.list_jobs() == [job]
        assert engine.next_run("relatorio-diario",
                               after=datetime(2026, 7, 30, 7, 0)) \
            == datetime(2026, 7, 30, 8, 0)

    def test_run_due_fires_only_due_jobs(self) -> None:
        engine = SchedulerEngine()
        fired: list[str] = []
        engine.register_handler("wf-relatorio", lambda: fired.append("relatorio"))
        engine.register_handler("wf-backup", lambda: fired.append("backup"))
        engine.add_job("j-relatorio", "wf-relatorio", cron="0 8 * * *",
                       after=datetime(2026, 7, 30, 7, 0))
        engine.add_job("j-backup", "wf-backup", cron="0 2 * * *",
                       after=datetime(2026, 7, 30, 3, 0))

        results = engine.run_due(datetime(2026, 7, 30, 8, 5))
        assert results == [("j-relatorio", None)]
        assert fired == ["relatorio"]
        job = engine.jobs["j-relatorio"]
        assert job.last_run is not None
        assert datetime.fromtimestamp(job.next_run_ts) \
            == datetime(2026, 7, 31, 8, 0)

    def test_run_due_interval_job(self) -> None:
        engine = SchedulerEngine()
        count = [0]
        engine.register_handler("wf-ping", lambda: count.__setitem__(0, count[0] + 1))
        engine.add_job("j-ping", "wf-ping", interval_seconds=60,
                       after=datetime(2026, 7, 30, 9, 59, 0))
        engine.run_due(datetime(2026, 7, 30, 10, 0))
        engine.run_due(datetime(2026, 7, 30, 10, 0, 30))  # not yet
        engine.run_due(datetime(2026, 7, 30, 10, 1, 5))   # due again
        assert count[0] == 2

    def test_missing_handler_raises(self) -> None:
        engine = SchedulerEngine()
        engine.add_job("j-x", "wf-sem-handler", interval_seconds=1,
                       after=datetime(2026, 7, 30, 9, 59, 50))
        with pytest.raises(ValueError):
            engine.run_due(datetime(2026, 7, 30, 10, 0, 2))

    def test_events_and_metrics(self) -> None:
        events = AutomationEvents()
        metrics = AutomationMetrics()
        engine = SchedulerEngine(events=events, metrics=metrics)
        fired: list[str] = []
        events.on(AutomationEventType.SCHEDULE_FIRED,
                  lambda d: fired.append(d["job_id"]))
        engine.register_handler("wf-x", lambda: {"ok": True})
        engine.add_job("j-x", "wf-x", interval_seconds=1,
                       after=datetime(2026, 7, 30, 9, 59, 0))
        engine.run_due(datetime(2026, 7, 30, 10, 0, 5))
        assert fired == ["j-x"]
        assert metrics.counter("schedules.fired") == 1

    def test_remove_job(self) -> None:
        engine = SchedulerEngine()
        engine.add_job("j-1", "wf-1", interval_seconds=60)
        assert engine.remove_job("j-1") is True
        assert engine.remove_job("j-1") is False
        assert engine.next_run("j-1") is None

    def test_disabled_job_not_due(self) -> None:
        engine = SchedulerEngine()
        engine.add_job("j-off", "wf-off", interval_seconds=1)
        engine.jobs["j-off"].enabled = False
        assert engine.due_jobs(datetime(2026, 7, 30, 10, 0, 30)) == []

    def test_user_example_schedules(self) -> None:
        """Diário 08:00 relatório financeiro; sexta 18:00 análise de vendas;
        mensal 1o dia 02:00 backup."""
        engine = SchedulerEngine()
        engine.register_handler("wf-financeiro", lambda: "relatorio gerado")
        engine.register_handler("wf-vendas", lambda: "analise vendas")
        engine.register_handler("wf-backup", lambda: "backup ok")

        engine.add_job("financeiro", "wf-financeiro", cron="0 8 * * *")
        engine.add_job("vendas-sexta", "wf-vendas", cron="0 18 * * 5")
        engine.add_job("backup-mensal", "wf-backup", cron="0 2 1 * *")

        assert engine.next_run("financeiro", after=datetime(2026, 7, 30, 6, 0)) \
            == datetime(2026, 7, 30, 8, 0)
        # 2026-07-30 = quinta; próxima sexta = 31/07 18:00
        assert engine.next_run("vendas-sexta", after=datetime(2026, 7, 30, 12, 0)) \
            == datetime(2026, 7, 31, 18, 0)
        assert engine.next_run("backup-mensal", after=datetime(2026, 7, 15, 12, 0)) \
            == datetime(2026, 8, 1, 2, 0)

        results = engine.run_due(datetime(2026, 7, 31, 18, 5))
        assert results == [("vendas-sexta", "analise vendas")]
