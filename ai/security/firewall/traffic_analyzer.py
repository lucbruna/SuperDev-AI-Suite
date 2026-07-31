"""Traffic analysis."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid, statistics

class TrafficSample:
    def __init__(self, timestamp: float, bytes_in: int, bytes_out: int, packets: int) -> None:
        self.timestamp = timestamp
        self.bytes_in = bytes_in
        self.bytes_out = bytes_out
        self.packets = packets

class TrafficAnalyzer:
    def __init__(self) -> None:
        self._samples: List[TrafficSample] = []
        self._anomalies: List[Dict[str, Any]] = []
        self._threshold_multiplier = 3.0
    def record(self, bytes_in: int = 0, bytes_out: int = 0, packets: int = 0) -> TrafficSample:
        sample = TrafficSample(time.time(), bytes_in, bytes_out, packets)
        self._samples.append(sample)
        self._check_anomaly(sample)
        return sample
    def _check_anomaly(self, sample: TrafficSample) -> None:
        if len(self._samples) > 20:
            recent = self._samples[-20:-1]
            total_bytes = [s.bytes_in + s.bytes_out for s in recent]
            mean = statistics.mean(total_bytes)
            stdev = statistics.stdev(total_bytes) if len(total_bytes) > 1 else 0
            current = sample.bytes_in + sample.bytes_out
            if stdev > 0 and abs(current - mean) / stdev > self._threshold_multiplier:
                self._anomalies.append({"timestamp": sample.timestamp, "bytes": current, "mean": mean, "stdev": stdev, "z_score": abs(current - mean) / stdev})
    def get_summary(self, duration_seconds: int = 3600) -> Dict[str, Any]:
        cutoff = time.time() - duration_seconds
        samples = [s for s in self._samples if s.timestamp >= cutoff]
        if not samples:
            return {"samples": 0, "total_bytes_in": 0, "total_bytes_out": 0, "avg_bytes": 0}
        total_in = sum(s.bytes_in for s in samples)
        total_out = sum(s.bytes_out for s in samples)
        total_packets = sum(s.packets for s in samples)
        return {"samples": len(samples), "total_bytes_in": total_in, "total_bytes_out": total_out, "total_packets": total_packets, "avg_bytes": (total_in + total_out) / max(len(samples), 1)}
    def get_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._anomalies[-limit:]
    def get_bandwidth(self) -> Dict[str, float]:
        if len(self._samples) < 2:
            return {"in_bps": 0.0, "out_bps": 0.0}
        last = self._samples[-1]
        prev = self._samples[-2]
        dt = max(last.timestamp - prev.timestamp, 0.001)
        return {"in_bps": last.bytes_in / dt, "out_bps": last.bytes_out / dt}
