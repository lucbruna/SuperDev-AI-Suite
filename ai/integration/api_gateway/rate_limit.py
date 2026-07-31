"""
Rate Limiter - Request rate limiting
"""
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class RateLimitConfig:
    max_requests: int = 1000
    window_seconds: int = 60
    burst_size: int = 100
    strategy: str = "sliding_window"


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime | None = None
    retry_after: int = 0


class RateLimiter:
    def __init__(self):
        self.configs: dict[str, RateLimitConfig] = {}
        self.counters: dict[str, list[datetime]] = {}
        self.blocked: dict[str, datetime] = {}

    def set_config(self, key: str, max_requests: int = 1000, window_seconds: int = 60) -> RateLimitConfig:
        config = RateLimitConfig(max_requests=max_requests, window_seconds=window_seconds)
        self.configs[key] = config
        return config

    def check(self, key: str) -> RateLimitResult:
        if key in self.blocked:
            if datetime.now() < self.blocked[key]:
                remaining_time = (self.blocked[key] - datetime.now()).seconds
                return RateLimitResult(allowed=False, remaining=0, limit=0, retry_after=remaining_time)
            del self.blocked[key]
        config = self.configs.get(key, RateLimitConfig())
        now = datetime.now()
        window_start = now - timedelta(seconds=config.window_seconds)
        self.counters.setdefault(key, [])
        self.counters[key] = [t for t in self.counters[key] if t > window_start]
        count = len(self.counters[key])
        if count >= config.max_requests:
            self.blocked[key] = now + timedelta(seconds=config.window_seconds)
            return RateLimitResult(allowed=False, remaining=0, limit=config.max_requests, retry_after=config.window_seconds)
        self.counters[key].append(now)
        return RateLimitResult(allowed=True, remaining=config.max_requests - count - 1, limit=config.max_requests, reset_at=window_start + timedelta(seconds=config.window_seconds))

    def reset(self, key: str) -> None:
        self.counters.pop(key, None)
        self.blocked.pop(key, None)

    def get_usage(self, key: str) -> int:
        return len(self.counters.get(key, []))

    def count(self) -> int:
        return len(self.configs)
