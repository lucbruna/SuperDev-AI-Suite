from __future__ import annotations

import time

from frontend.state.state_engine import StateEngine
from frontend.state.cache_state import CacheState
from frontend.routing.routing_engine import RoutingEngine
from frontend.api_client.api_client import APIClient
from frontend.permissions.permissions_engine import PermissionsEngine


def test_state_pub_sub() -> None:
    state = StateEngine()
    updates: list[dict] = []

    def on_update(_key: str, value: dict) -> None:
        updates.append(value)

    state.subscribe("projects", on_update)
    state.set("projects", {"count": 3})
    assert updates and updates[-1].get("count") == 3


def test_cache_ttl() -> None:
    cache = CacheState()
    cache.set("key", "value", ttl=0.01)
    assert cache.get("key") == "value"
    time.sleep(0.02)
    assert cache.get("key") is None


def test_routing_params() -> None:
    router = RoutingEngine()
    router.add("/projects/:id", "project_detail", handler=lambda **kw: kw)
    route = router.resolve("/projects/42")
    assert route is not None
    assert route.name == "project_detail"
    assert route.path == "/projects/:id"
    # non-matching path returns None
    assert router.resolve("/agents/42") is None


def test_api_client_url_build() -> None:
    client = APIClient(base_url="https://api.example.com")
    assert client.url("/agents") == "https://api.example.com/agents"


def test_permissions_rbac() -> None:
    perms = PermissionsEngine()
    perms.define_role("admin", ["delete_project"])
    perms.assign_role("alice", "admin")
    assert perms.can("alice", "delete_project") is True
    assert perms.can("bob", "delete_project") is False
