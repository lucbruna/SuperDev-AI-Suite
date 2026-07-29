"""
Threat Detection - Detects security threats
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List


class ThreatDetector:
    """Detects security threats"""

    def __init__(self, config):
        self.config = config
        self._rate_limits: Dict[str, List[datetime]] = defaultdict(list)
        self._failed_attempts: Dict[str, int] = defaultdict(int)

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def check_rate_limit(self, identifier: str, limit: int, window: int) -> bool:
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)

        self._rate_limits[identifier] = [
            t for t in self._rate_limits[identifier] if t > cutoff
        ]

        if len(self._rate_limits[identifier]) >= limit:
            return False

        self._rate_limits[identifier].append(now)
        return True

    async def analyze_failed_access(self, context, resource: str, action: str) -> None:
        key = f"{context.ip_address}:{resource}:{action}"
        self._failed_attempts[key] += 1

        if self._failed_attempts[key] > 10:
            pass

    async def scan(self, data: Dict, context) -> List[Dict]:
        threats = []

        if self._contains_sensitive_data(data):
            threats.append({"type": "sensitive_data_exposure", "severity": "high"})

        if self._contains_sql_injection(data):
            threats.append({"type": "sql_injection_attempt", "severity": "critical"})

        return threats

    def _contains_sensitive_data(self, data: Dict) -> bool:
        sensitive = ["ssn", "credit_card", "password", "secret", "token"]
        data_str = str(data).lower()
        return any(s in data_str for s in sensitive)

    def _contains_sql_injection(self, data: Dict) -> bool:
        patterns = ["'", "union select", "drop table", "or 1=1", ";--"]
        data_str = str(data).lower()
        return any(p in data_str for p in patterns)

    def get_stats(self) -> Dict:
        return {
            "active_rate_limits": len(self._rate_limits),
            "failed_attempts_tracked": len(self._failed_attempts),
        }