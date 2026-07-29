import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class HealthResult:
    status: str  # healthy, degraded, unhealthy
    latency_ms: float
    last_check: float
    details: Dict[str, Any] = field(default_factory=dict)


class HealthMonitor:
    def __init__(self) -> None:
        self._services: Dict[str, HealthResult] = {}

    def register_service(self, name: str) -> None:
        if name not in self._services:
            self._services[name] = HealthResult(
                status="healthy",
                latency_ms=0.0,
                last_check=time.time(),
                details={},
            )

    def check_service(self, name: str) -> HealthResult:
        result = self._services.get(name)
        if result is None:
            result = HealthResult(status="unhealthy", latency_ms=0.0, last_check=time.time())
            self._services[name] = result
        start = time.time()
        try:
            result.latency_ms = (time.time() - start) * 1000
            result.last_check = time.time()
            result.status = "healthy"
        except Exception as e:
            result.latency_ms = (time.time() - start) * 1000
            result.last_check = time.time()
            result.status = "unhealthy"
            result.details["error"] = str(e)
        return result

    def check_all(self) -> Dict[str, HealthResult]:
        return {name: self.check_service(name) for name in list(self._services.keys())}

    def get_service(self, name: str) -> Optional[HealthResult]:
        return self._services.get(name)
