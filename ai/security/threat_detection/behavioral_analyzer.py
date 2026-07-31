"""Behavioral analysis."""
from __future__ import annotations

import statistics
import time
from typing import Any


class UserBehaviorProfile:
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.login_times: list[float] = []
        self.access_patterns: list[dict[str, Any]] = []
        self.resource_usage: list[dict[str, Any]] = []
        self.anomaly_score: float = 0.0

class BehavioralAnalyzer:
    def __init__(self) -> None:
        self._profiles: dict[str, UserBehaviorProfile] = {}
        self._alerts: list[dict[str, Any]] = []
        self._baseline_window = 30 * 86400  # 30 days
    def record_login(self, user_id: str, timestamp: float = 0.0) -> None:
        ts = timestamp or time.time()
        profile = self._profiles.setdefault(user_id, UserBehaviorProfile(user_id))
        profile.login_times.append(ts)
        self._analyze_login_pattern(profile)
    def record_access(self, user_id: str, resource: str, action: str) -> None:
        profile = self._profiles.setdefault(user_id, UserBehaviorProfile(user_id))
        profile.access_patterns.append({"resource": resource, "action": action, "timestamp": time.time()})
    def record_resource_usage(self, user_id: str, resource: str, usage: float) -> None:
        profile = self._profiles.setdefault(user_id, UserBehaviorProfile(user_id))
        profile.resource_usage.append({"resource": resource, "usage": usage, "timestamp": time.time()})
    def _analyze_login_pattern(self, profile: UserBehaviorProfile) -> None:
        if len(profile.login_times) > 20:
            recent = profile.login_times[-20:]
            intervals = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
            if len(intervals) > 1:
                mean_interval = statistics.mean(intervals)
                stdev_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
                if stdev_interval > 0 and mean_interval / stdev_interval < 2:
                    profile.anomaly_score += 0.1
    def get_profile(self, user_id: str) -> dict[str, Any] | None:
        profile = self._profiles.get(user_id)
        if profile:
            return {"user_id": profile.user_id, "logins": len(profile.login_times), "access_count": len(profile.access_patterns), "anomaly_score": profile.anomaly_score}
        return None
    def get_alerts(self, user_id: str = "", limit: int = 100) -> list[dict[str, Any]]:
        alerts = self._alerts
        if user_id:
            alerts = [a for a in alerts if a.get("user_id") == user_id]
        return alerts[-limit:]
    def get_high_risk_users(self, threshold: float = 0.5) -> list[dict[str, Any]]:
        return [{"user_id": p.user_id, "anomaly_score": p.anomaly_score} for p in self._profiles.values() if p.anomaly_score > threshold]
