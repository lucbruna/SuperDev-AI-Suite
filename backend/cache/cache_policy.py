from typing import Any

DEFAULT_TTLS: dict[str, int] = {
    "superdev:user": 300,
    "superdev:project": 300,
    "superdev:session": 3600,
    "superdev:permission": 300,
    "superdev:token": 3600,
    "superdev:config": 600,
    "superdev:ratelimit": 60,
}


class CachePolicy:
    def __init__(self, custom_ttls: dict[str, int] | None = None) -> None:
        self._ttls = dict(DEFAULT_TTLS)
        if custom_ttls:
            self._ttls.update(custom_ttls)

    def get_ttl(self, key: str) -> int:
        for prefix, ttl in self._ttls.items():
            if key.startswith(prefix):
                return ttl
        return 300

    def should_cache(self, key: str, value: Any) -> bool:
        if value is None:
            return False
        return not (isinstance(value, (list, dict, str)) and not value)

    def set_ttl(self, prefix: str, ttl: int) -> None:
        self._ttls[prefix] = ttl

    def get_all_ttls(self) -> dict[str, int]:
        return dict(self._ttls)
