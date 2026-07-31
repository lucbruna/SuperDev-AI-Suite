"""Tests for the API Gateway subsystem (gateway/)."""

from __future__ import annotations

import pytest

from integration.gateway.caching import GatewayCache
from integration.gateway.filtering import RequestFilter
from integration.gateway.gateway_engine import GatewayEngine
from integration.gateway.load_balancing import LoadBalancer
from integration.gateway.monitoring import GatewayMonitoring
from integration.gateway.rate_limit import RateLimiter
from integration.gateway.request_router import RequestRouter
from integration.gateway.security import GatewaySecurity


class TestRateLimiter:
    def test_allow_within_limit(self) -> None:
        limiter = RateLimiter(limit=3, window=60)
        assert limiter.allow("client-1") is True
        assert limiter.allow("client-1") is True
        assert limiter.allow("client-1") is True
        assert limiter.allow("client-1") is False
        assert limiter.remaining("client-1") == 0

    def test_per_client_independent(self) -> None:
        limiter = RateLimiter(limit=2, window=60)
        assert limiter.allow("a") is True
        assert limiter.allow("a") is True
        assert limiter.allow("a") is False
        assert limiter.allow("b") is True

    def test_reset(self) -> None:
        limiter = RateLimiter(limit=1, window=60)
        assert limiter.allow("x") is True
        limiter.reset("x")
        assert limiter.allow("x") is True

    def test_snapshot(self) -> None:
        limiter = RateLimiter(limit=5, window=30)
        assert limiter.snapshot()["limit"] == 5
        assert limiter.snapshot()["window"] == 30


class TestLoadBalancer:
    def test_round_robin(self) -> None:
        balancer = LoadBalancer()
        balancer.add_target("svc-1")
        balancer.add_target("svc-2")
        first = balancer.next()
        second = balancer.next()
        assert {first, second} == {"svc-1", "svc-2"}
        assert balancer.next() == first  # wraps around

    def test_no_targets(self) -> None:
        balancer = LoadBalancer()
        assert balancer.next() is None

    def test_remove_target(self) -> None:
        balancer = LoadBalancer()
        balancer.add_target("svc-1")
        assert balancer.remove_target("svc-1") is True
        assert balancer.remove_target("svc-1") is False
        assert balancer.count() == 0


class TestGatewayCache:
    def test_set_get_invalidate(self) -> None:
        cache = GatewayCache(ttl=60)
        cache.set("k", {"x": 1})
        assert cache.get("k") == {"x": 1}
        assert cache.invalidate("k") is True
        assert cache.get("k") is None

    def test_ttl_expiry(self) -> None:
        cache = GatewayCache(ttl=0.01)
        cache.set("k", "v")
        import time

        time.sleep(0.02)
        assert cache.get("k") is None

    def test_max_entries_eviction(self) -> None:
        cache = GatewayCache(ttl=60, max_entries=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.size() == 2


class TestRequestFilter:
    def test_allow_by_default(self) -> None:
        filter_ = RequestFilter()
        assert filter_.allow("GET", "/health") is True

    def test_deny_method(self) -> None:
        filter_ = RequestFilter()
        filter_.deny_method("DELETE")
        assert filter_.allow("DELETE", "/x") is False
        assert filter_.allow("GET", "/x") is True

    def test_block_ip_and_header(self) -> None:
        filter_ = RequestFilter()
        filter_.block_ip("1.2.3.4")
        assert filter_.allow("GET", "/x", client_ip="1.2.3.4") is False
        filter_.unblock_ip("1.2.3.4")
        assert filter_.allow("GET", "/x", client_ip="1.2.3.4") is True
        filter_.block_header_value("user-agent", "badbot")
        assert filter_.allow("GET", "/x", headers={"User-Agent": "badbot"}) is False

    def test_path_pattern(self) -> None:
        filter_ = RequestFilter()
        filter_.add_path_pattern(r"^/admin")
        assert filter_.allow("GET", "/admin/secret") is False
        assert filter_.allow("GET", "/public") is True


class TestGatewaySecurity:
    def test_authenticate_bearer(self) -> None:
        security = GatewaySecurity()
        security.register_key("token-123", "alice")
        ok, owner = security.authenticate({"Authorization": "Bearer token-123"})
        assert ok is True and owner == "alice"

    def test_authenticate_api_key_header(self) -> None:
        security = GatewaySecurity()
        security.register_key("sk-abc", "bob")
        ok, owner = security.authenticate({"X-Api-Key": "sk-abc"})
        assert ok is True and owner == "bob"

    def test_invalid_credentials(self) -> None:
        security = GatewaySecurity()
        ok, _ = security.authenticate({"Authorization": "Bearer nope"})
        assert ok is False
        ok, _ = security.authenticate({})
        assert ok is False

    def test_enforce(self) -> None:
        security = GatewaySecurity()
        security.register_key("k", "carol")
        assert security.enforce({"X-Api-Key": "k"}) == "carol"
        with pytest.raises(PermissionError):
            security.enforce({"X-Api-Key": "bad"})
        assert security.enforce({}, required=False) is None

    def test_revoke(self) -> None:
        security = GatewaySecurity()
        security.register_key("k", "dave")
        assert security.revoke_key("k") is True
        assert security.revoke_key("k") is False


class TestGatewayMonitoring:
    def test_record_requests(self) -> None:
        monitoring = GatewayMonitoring()
        monitoring.record_request("GET /orders", 0.01)
        monitoring.record_request("GET /orders", 0.02)
        monitoring.record_request("GET /orders", 0.03, status="error")
        assert monitoring.total_requests() == 3
        assert monitoring.total_errors() == 1
        assert monitoring.error_rate() == pytest.approx(0.3333, abs=0.001)
        assert monitoring.average_latency("GET /orders") == pytest.approx(0.02, abs=0.001)

    def test_snapshot(self) -> None:
        monitoring = GatewayMonitoring()
        snapshot = monitoring.snapshot()
        assert snapshot["total_requests"] == 0
        assert snapshot["error_rate"] == 0.0


class TestRequestRouter:
    def test_register_dispatch(self) -> None:
        router = RequestRouter()

        def handler(params: dict) -> str:
            return f"handled:{params.get('id')}"

        router.register("GET", "/orders", handler)
        assert router.has("GET", "/orders") is True
        assert router.dispatch("GET", "/orders", {"id": 1}) == "handled:1"

    def test_missing_handler_raises(self) -> None:
        router = RequestRouter()
        with pytest.raises(KeyError):
            router.dispatch("GET", "/missing")

    def test_unregister(self) -> None:
        router = RequestRouter()

        def handler(params: dict) -> None:
            pass

        router.register("GET", "/x", handler)
        assert router.unregister("GET", "/x") is True
        assert router.routes() == []


class TestGatewayEngine:
    def test_full_pipeline(self) -> None:
        gateway = GatewayEngine(rate_limit=10)
        gateway.route(
            "GET",
            "/health",
            lambda params: {"status": "ok"},
        )
        result = gateway.handle("GET", "/health", params={})
        assert result == {"status": "ok"}
        assert gateway.stats()["routes"] == 1

    def test_rate_limit_blocked(self) -> None:
        gateway = GatewayEngine(rate_limit=1)
        gateway.route("GET", "/x", lambda params: "ok")
        gateway.handle("GET", "/x", params={}, client_id="c")
        with pytest.raises(RuntimeError):
            gateway.handle("GET", "/x", params={}, client_id="c")

    def test_filter_blocked(self) -> None:
        gateway = GatewayEngine()
        gateway.filter.deny_method("POST")
        with pytest.raises(PermissionError):
            gateway.handle("POST", "/x", params={})

    def test_caching(self) -> None:
        gateway = GatewayEngine()
        calls = {"n": 0}

        def handler(params: dict) -> dict:
            calls["n"] += 1
            return {"count": calls["n"]}

        gateway.route("GET", "/x", handler)
        first = gateway.handle("GET", "/x", params={})
        second = gateway.handle("GET", "/x", params={})
        assert first == second
        assert calls["n"] == 1  # cached

    def test_missing_route_returns_error(self) -> None:
        gateway = GatewayEngine()
        result = gateway.handle("GET", "/missing", params={})
        assert "error" in result

    def test_load_balance_and_keys(self) -> None:
        gateway = GatewayEngine()
        gateway.add_target("svc-1")
        gateway.register_key("k", "owner")
        assert gateway.stats()["targets"] == 1
        ok, owner = gateway.security.authenticate({"X-Api-Key": "k"})
        assert ok is True and owner == "owner"
