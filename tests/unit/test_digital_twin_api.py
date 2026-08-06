"""Unit tests for the Digital Twin api package."""
from __future__ import annotations

from typing import cast

from modules.digital_twin.api import (
    ALL_ENDPOINTS,
    ApiResponse,
    DigitalTwinAPI,
    MiddlewareChain,
    TwinRouter,
    audit_middleware,
    permission_middleware,
)
from modules.digital_twin.config.constants import (
    ENTITY_MODULE,
    ENTITY_PROJECT,
    PERM_MANAGE_TWIN,
    PERM_RUN_SIMULATION,
    PERM_VIEW_TWIN,
    REL_DEPENDS_ON,
)
from modules.digital_twin.config.permissions import Permissions
from modules.digital_twin.core.digital_twin_manager import DigitalTwinManager
from modules.digital_twin.twin_engine import TwinEngine, TwinModelRegistry


def _router() -> TwinRouter:
    return TwinRouter(permissions=Permissions.for_role("admin"))


def _api() -> DigitalTwinAPI:
    return DigitalTwinAPI(
        manager=DigitalTwinManager(),
        permissions=Permissions.for_role("admin"),
        twin_engine=TwinEngine(),
        twin_registry=TwinModelRegistry(),
    )


class TestApiResponse:
    def test_success(self) -> None:
        response = ApiResponse.success({"a": 1})
        assert response.ok
        assert response.status_code == 200
        assert response.data == {"a": 1}

    def test_failure_defaults_to_bad_request(self) -> None:
        response = ApiResponse.failure("bad")
        assert not response.ok
        assert response.status_code == 400
        assert response.error == "bad"

    def test_status_code_classes(self) -> None:
        assert ApiResponse.forbidden().status_code == 403
        assert ApiResponse.not_found().status_code == 404
        assert ApiResponse.internal().status_code == 500

    def test_to_dict(self) -> None:
        data = ApiResponse.success({"a": 1}).to_dict()
        assert data == {"ok": True, "data": {"a": 1}, "error": "", "status_code": 200}


class TestPermissions:
    def test_role_grants(self) -> None:
        viewer = Permissions.for_role("viewer")
        operator = Permissions.for_role("operator")
        admin = Permissions.for_role("admin")
        assert viewer.can(PERM_VIEW_TWIN)
        assert not viewer.can(PERM_RUN_SIMULATION)
        assert operator.can(PERM_RUN_SIMULATION)
        assert not operator.can(PERM_MANAGE_TWIN)
        assert admin.can(PERM_MANAGE_TWIN)

    def test_unknown_role_falls_back_to_viewer(self) -> None:
        perms = Permissions.for_role("ghost")
        assert perms.role == "viewer"
        assert perms.can(PERM_VIEW_TWIN)
        assert not perms.can(PERM_MANAGE_TWIN)

    def test_explicit_grants_are_additive(self) -> None:
        perms = Permissions(
            role="viewer", grants=frozenset({PERM_RUN_SIMULATION})
        )
        assert perms.can(PERM_RUN_SIMULATION)


class TestMiddlewareChain:
    def test_passes_through_when_none_reject(self) -> None:
        assert MiddlewareChain().run("status", "admin", {}) is None

    def test_first_rejection_short_circuits(self) -> None:
        def reject(endpoint: str, role: str, params: dict[str, object]):
            return ApiResponse.forbidden() if endpoint == "a" else None

        def unreachable(endpoint: str, role: str, params: dict[str, object]):
            raise AssertionError("should not run")

        chain = MiddlewareChain()
        chain.add(reject)
        chain.add(unreachable)
        response = chain.run("a", "admin", {})
        assert response is not None
        assert response.status_code == 403

    def test_permission_middleware_rejects(self) -> None:
        chain = MiddlewareChain()
        chain.add(permission_middleware(Permissions.for_role("viewer")))
        response = chain.run(
            "build_twin", "viewer", {"_permission": PERM_RUN_SIMULATION}
        )
        assert response is not None
        assert response.status_code == 403

    def test_permission_middleware_allows(self) -> None:
        chain = MiddlewareChain()
        chain.add(permission_middleware(Permissions.for_role("admin")))
        assert (
            chain.run("build_twin", "admin", {"_permission": PERM_RUN_SIMULATION})
            is None
        )

    def test_audit_middleware_records(self) -> None:
        log: list[dict[str, object]] = []
        chain = MiddlewareChain()
        chain.add(audit_middleware(log))
        assert chain.run("status", "viewer", {}) is None
        assert log == [{"endpoint": "status", "role": "viewer"}]


class TestTwinRouter:
    def test_endpoints_endpoint(self) -> None:
        response = _router().dispatch("endpoints", role="admin")
        assert response.ok
        assert "endpoints" in response.data

    def test_unknown_endpoint_not_found(self) -> None:
        response = _router().dispatch("nope", role="admin")
        assert not response.ok
        assert response.status_code == 404

    def test_known_endpoint_without_handler_not_found(self) -> None:
        response = _router().dispatch("status", role="admin")
        assert not response.ok
        assert response.status_code == 404

    def test_permission_rejection(self) -> None:
        router = TwinRouter(
            handlers={"build_twin": lambda **kwargs: ApiResponse.success()},
            permissions=Permissions.for_role("viewer"),
        )
        response = router.dispatch("build_twin", role="viewer")
        assert response.status_code == 403

    def test_handler_type_error_becomes_bad_request(self) -> None:
        def handler(**kwargs):
            raise TypeError("bad params")

        router = TwinRouter(
            handlers={"build_twin": handler},
            permissions=Permissions.for_role("admin"),
        )
        response = router.dispatch("build_twin", {"name": "x"}, role="admin")
        assert not response.ok
        assert response.status_code == 400

    def test_handler_exception_becomes_internal_error(self) -> None:
        def handler(**kwargs):
            raise RuntimeError("boom")

        router = TwinRouter(
            handlers={"build_twin": handler},
            permissions=Permissions.for_role("admin"),
        )
        response = router.dispatch("build_twin", role="admin")
        assert not response.ok
        assert response.status_code == 500

    def test_register_adds_handler(self) -> None:
        router = _router()
        router.register("ping", lambda **kwargs: ApiResponse.success())
        assert "ping" in router.endpoint_names()

    def test_dispatch_strips_internal_permission_param(self) -> None:
        received: dict[str, object] = {}

        def spy(**kwargs):
            received.update(kwargs)
            return ApiResponse.success()

        router = TwinRouter(
            handlers={"status": spy},
            permissions=Permissions.for_role("admin"),
        )
        response = router.dispatch("status", role="admin")
        assert response.ok
        assert "_permission" not in received


class TestDigitalTwinAPI:
    def test_status(self) -> None:
        data = cast(dict, _api().dispatch("status", role="admin").data)
        assert data["running"] is False
        assert data["cycles"] == 0
        assert data["twin_status"] == "synced"

    def test_config(self) -> None:
        data = cast(dict, _api().dispatch("config", role="admin").data)
        assert data["enabled"] is True
        assert data["sync_interval_seconds"] > 0

    def test_start_stop(self) -> None:
        api = _api()
        assert cast(dict, api.dispatch("start", role="admin").data)["running"] is True
        assert cast(dict, api.dispatch("stop", role="admin").data)["running"] is False

    def test_cycle_increments(self) -> None:
        api = _api()
        data = cast(dict, api.dispatch("cycle", role="admin").data)
        assert data["cycle"] == 1
        assert cast(dict, api.dispatch("cycle", role="admin").data)["cycle"] == 2

    def test_tick(self) -> None:
        data = cast(dict, _api().dispatch("tick", {"steps": 3}, role="admin").data)
        assert data["steps"] == 3

    def test_build_then_snapshot_analyze_validate(self) -> None:
        api = _api()
        build = api.dispatch(
            "build_twin",
            {
                "name": "site",
                "raw_entities": [
                    {"id": "p1", "type": ENTITY_PROJECT, "name": "Acme"},
                    {"id": "m1", "type": ENTITY_MODULE, "name": "core"},
                ],
                "relationships": [("p1", "m1", REL_DEPENDS_ON)],
            },
            role="admin",
        )
        assert build.ok
        assert cast(dict, cast(dict, build.data)["twin"])["name"] == "site"

        snap = cast(dict, api.dispatch("snapshot", {"name": "site"}, role="admin").data)
        assert snap["twin_name"] == "site"
        assert snap["sequence"] == 1

        analysis = cast(dict, api.dispatch("analyze", {"name": "site"}, role="admin").data)
        assert analysis["entity_count"] == 2

        validation = cast(dict, api.dispatch("validate", {"name": "site"}, role="admin").data)
        assert validation["valid"] is True

    def test_analyze_missing_twin_not_found(self) -> None:
        response = _api().dispatch("analyze", {"name": "ghost"}, role="admin")
        assert not response.ok
        assert response.status_code == 404

    def test_validate_missing_twin_not_found(self) -> None:
        response = _api().dispatch("validate", {"name": "ghost"}, role="admin")
        assert response.status_code == 404

    def test_register_component(self) -> None:
        api = _api()

        def component(ctx):  # noqa: ARG001
            return {"ok": True}

        data = cast(
            dict,
            api.dispatch(
                "register_component",
                {"name": "extra", "component": component},
                role="admin",
            ).data,
        )
        assert data["registered"] is True

    def test_viewer_cannot_build_but_can_view(self) -> None:
        api = DigitalTwinAPI(
            manager=DigitalTwinManager(),
            permissions=Permissions.for_role("viewer"),
        )
        assert api.dispatch("status", role="viewer").ok
        forbidden = api.dispatch("build_twin", role="viewer")
        assert forbidden.status_code == 403

    def test_audit_log_records_allowed_calls(self) -> None:
        audit: list[dict[str, object]] = []
        api = DigitalTwinAPI(
            manager=DigitalTwinManager(),
            permissions=Permissions.for_role("admin"),
            audit_log=audit,
        )
        api.dispatch("status", role="admin")
        api.dispatch("cycle", role="admin")
        assert [entry["endpoint"] for entry in audit] == ["status", "cycle"]

    def test_all_operational_endpoints_exposed(self) -> None:
        data = cast(dict, _api().dispatch("endpoints", role="admin").data)
        names = set(cast(list, data["endpoints"]))
        assert set(ALL_ENDPOINTS) - {"endpoints"} == names
