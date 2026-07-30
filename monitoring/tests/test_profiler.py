from __future__ import annotations

import pytest

from SuperDev.monitoring.profiling.profiler import Profiler
from SuperDev.monitoring.profiling.cpu_profiler import CpuProfiler
from SuperDev.monitoring.profiling.memory_profiler import MemoryProfiler
from SuperDev.monitoring.profiling.code_profiler import CodeProfiler
from SuperDev.monitoring.profiling.flamegraph import Flamegraph


class TestProfiler:
    def test_start_stop(self) -> None:
        p = Profiler()
        p.start()
        p.stop()
        assert p._running is False


class TestCpuProfiler:
    def test_collect(self) -> None:
        p = CpuProfiler()
        data = p.collect()
        assert "cpu_percent" in data


class TestMemoryProfiler:
    def test_collect(self) -> None:
        p = MemoryProfiler()
        data = p.collect()
        assert "rss" in data


class TestCodeProfiler:
    def test_profile_sync(self) -> None:
        p = CodeProfiler()

        @p.profile
        def my_func() -> int:
            return 42

        result = my_func()
        assert result == 42


class TestFlamegraph:
    def test_folded_output(self) -> None:
        f = Flamegraph()
        f.add_frame("root;child;leaf", 10)
        output = f.to_folded()
        assert "root;child;leaf 10" in output
