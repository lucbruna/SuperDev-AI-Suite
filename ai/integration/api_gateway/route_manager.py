"""
Route Manager - Route configuration
"""

from dataclasses import dataclass, field
from enum import Enum


class RouteGroup(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    ADMIN = "admin"
    EXTERNAL = "external"


@dataclass
class RouteConfig:
    path: str
    target: str
    group: RouteGroup = RouteGroup.INTERNAL
    version: str = "v1"
    timeout: int = 30
    cache_ttl: int = 0
    cors_origins: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


class RouteManager:
    def __init__(self):
        self.routes: dict[str, RouteConfig] = {}
        self.groups: dict[str, list[str]] = {}
        self.versions: dict[str, list[str]] = {}

    def add_route(self, path: str, target: str, group: RouteGroup = RouteGroup.INTERNAL, **kwargs) -> RouteConfig:
        config = RouteConfig(path=path, target=target, group=group, **kwargs)
        self.routes[path] = config
        self.groups.setdefault(group.value, []).append(path)
        self.versions.setdefault(config.version, []).append(path)
        return config

    def remove_route(self, path: str) -> bool:
        if path in self.routes:
            del self.routes[path]
            return True
        return False

    def get_route(self, path: str) -> RouteConfig | None:
        return self.routes.get(path)

    def get_by_group(self, group: RouteGroup) -> list[RouteConfig]:
        paths = self.groups.get(group.value, [])
        return [self.routes[p] for p in paths if p in self.routes]

    def get_by_version(self, version: str) -> list[RouteConfig]:
        paths = self.versions.get(version, [])
        return [self.routes[p] for p in paths if p in self.routes]

    def update_route(self, path: str, **kwargs) -> bool:
        config = self.routes.get(path)
        if config:
            for k, v in kwargs.items():
                if hasattr(config, k):
                    setattr(config, k, v)
            return True
        return False

    def list_all(self) -> list[RouteConfig]:
        return list(self.routes.values())

    def count(self) -> int:
        return len(self.routes)
