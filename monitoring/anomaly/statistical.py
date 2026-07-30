from __future__ import annotations

import math
from typing import Any


class StatisticalDetector:
    """Statistical anomaly detection methods."""

    @staticmethod
    def zscore(values: list[float], threshold: float = 3.0) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / (n - 1)
        std = math.sqrt(variance) if variance > 0 else 1.0
        z = abs(values[-1] - mean) / std
        return z

    @staticmethod
    def iqr(values: list[float], multiplier: float = 1.5) -> float:
        sorted_v = sorted(values)
        n = len(sorted_v)
        if n < 4:
            return 0.0

        def percentile(data: list[float], p: float) -> float:
            idx = p * (len(data) - 1)
            lo = int(math.floor(idx))
            hi = int(math.ceil(idx))
            if lo == hi:
                return data[lo]
            return data[lo] + (idx - lo) * (data[hi] - data[lo])

        q1 = percentile(sorted_v, 0.25)
        q3 = percentile(sorted_v, 0.75)
        iqr_val = q3 - q1
        upper = q3 + multiplier * iqr_val
        lower = q1 - multiplier * iqr_val

        last = values[-1]
        if last > upper:
            return (last - upper) / (iqr_val or 1)
        if last < lower:
            return (lower - last) / (iqr_val or 1)
        return 0.0

    @staticmethod
    def mad(values: list[float], threshold: float = 3.0) -> float:
        n = len(values)
        if n < 2:
            return 0.0
        median = sorted(values)[n // 2]
        abs_devs = sorted(abs(v - median) for v in values)
        mad_val = abs_devs[len(abs_devs) // 2]
        if mad_val == 0:
            mad_val = sum(abs_devs) / n
        return abs(values[-1] - median) / (mad_val or 1)
