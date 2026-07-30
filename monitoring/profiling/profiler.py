from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import ProfilingSample


@dataclass
class ProfilerConfig:
    interval: float = 10.0
    enabled: bool = True
    collect_cpu: bool = True
    collect_memory: bool = True
    collect_io: bool = True
    collect_network: bool = True
    collect_gc: bool = True


class Profiler:
    """Base profiler that collects system resource metrics."""

    def __init__(self, config: ProfilerConfig | None = None) -> None:
        self._config = config or ProfilerConfig()
        self._samples: list[ProfilingSample] = []
        self._callbacks: list[Callable[[ProfilingSample], None]] = []
        self._running = False

    @property
    def config(self) -> ProfilerConfig:
        return self._config

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def sample(self) -> ProfilingSample:
        sample = ProfilingSample()
        if self._config.collect_cpu:
            sample.cpu_percent = self._get_cpu()
        if self._config.collect_memory:
            sample.memory_mb = self._get_memory()
        if self._config.collect_io:
            sample.io_read_bytes, sample.io_write_bytes = self._get_io()
        if self._config.collect_network:
            sample.network_rx_bytes, sample.network_tx_bytes = self._get_network()
        self._samples.append(sample)
        self._notify(sample)
        return sample

    def _get_cpu(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def _get_memory(self) -> float:
        try:
            import psutil
            return psutil.virtual_memory().used / (1024 * 1024)
        except ImportError:
            return 0.0

    def _get_io(self) -> tuple[int, int]:
        try:
            import psutil
            io = psutil.disk_io_counters()
            if io:
                return int(io.read_bytes), int(io.write_bytes)
        except ImportError:
            pass
        return 0, 0

    def _get_network(self) -> tuple[int, int]:
        try:
            import psutil
            net = psutil.net_io_counters()
            if net:
                return int(net.bytes_recv), int(net.bytes_sent)
        except ImportError:
            pass
        return 0, 0

    def on_sample(self, callback: Callable[[ProfilingSample], None]) -> None:
        self._callbacks.append(callback)

    def _notify(self, sample: ProfilingSample) -> None:
        for cb in self._callbacks:
            try:
                cb(sample)
            except Exception:
                pass

    def get_samples(self, limit: int = 100) -> list[ProfilingSample]:
        return list(self._samples[-limit:])

    def clear(self) -> None:
        self._samples.clear()
