import time
from typing import List, Optional


class Counter:
    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._value: float = 0.0

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def export(self) -> str:
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} counter",
            f"{self._name} {self._value}",
        ]
        return "\n".join(lines)


class Gauge:
    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._value: float = 0.0

    def set(self, value: float) -> None:
        self._value = value

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        self._value -= amount

    def export(self) -> str:
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} gauge",
            f"{self._name} {self._value}",
        ]
        return "\n".join(lines)


class Histogram:
    def __init__(self, name: str, description: str = "", buckets: Optional[List[float]] = None) -> None:
        self._name = name
        self._description = description
        self._buckets = sorted(buckets) if buckets else [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._counts: List[int] = [0] * (len(self._buckets) + 1)
        self._sum: float = 0.0
        self._count: int = 0

    def observe(self, value: float) -> None:
        self._sum += value
        self._count += 1
        for i, bucket in enumerate(self._buckets):
            if value <= bucket:
                self._counts[i] += 1
        self._counts[-1] += 1

    def export(self) -> str:
        lines = [
            f"# HELP {self._name} {self._description}",
            f"# TYPE {self._name} histogram",
        ]
        for i, bucket in enumerate(self._buckets):
            lines.append(f"{self._name}_bucket{{le=\"{bucket}\"}} {self._counts[i]}")
        lines.append(f"{self._name}_bucket{{le=\"+Inf\"}} {self._counts[-1]}")
        lines.append(f"{self._name}_count {self._count}")
        lines.append(f"{self._name}_sum {self._sum}")
        return "\n".join(lines)
