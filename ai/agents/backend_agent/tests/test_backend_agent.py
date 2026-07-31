from __future__ import annotations

from ..api_generator import APIGenerator
from ..async_optimizer import AsyncOptimizer
from ..authentication_generator import AuthenticationGenerator
from ..backend_agent import BackendAgent
from ..database_mapper import DatabaseMapper
from ..middleware_generator import MiddlewareGenerator
from ..model_generator import ModelGenerator
from ..performance import Performance
from ..repository_generator import RepositoryGenerator
from ..security import Security
from ..service_generator import ServiceGenerator
from ..websocket_generator import WebSocketGenerator


class TestAPIGenerator:
    def test_add_endpoint(self) -> None:
        api = APIGenerator()
        key = api.add_endpoint("/users", "GET", "list_users")
        assert key == "GET:/users"

    def test_get_endpoint(self) -> None:
        api = APIGenerator()
        api.add_endpoint("/users", "GET", "list_users")
        assert api.get_endpoint("/users") is not None

    def test_remove_endpoint(self) -> None:
        api = APIGenerator()
        api.add_endpoint("/u", "GET", "h")
        assert api.remove_endpoint("/u") is True
        assert api.remove_endpoint("/u") is False

    def test_list_endpoints(self) -> None:
        api = APIGenerator()
        api.add_endpoint("/", "GET", "root")
        assert len(api.list_endpoints()) == 1

    def test_endpoint_count(self) -> None:
        api = APIGenerator()
        assert api.endpoint_count == 0
        api.add_endpoint("/", "GET", "root")
        assert api.endpoint_count == 1

    def test_generate_routes(self) -> None:
        api = APIGenerator()
        api.add_endpoint("/", "GET", "root")
        assert "Route Table" in api.generate_routes()

    def test_to_dict(self) -> None:
        api = APIGenerator()
        api.add_endpoint("/", "GET", "root")
        d = api.to_dict()
        assert "endpoints" in d


class TestServiceGenerator:
    def test_add_service(self) -> None:
        sg = ServiceGenerator()
        sg.add_service("UserService", ["create", "find"])
        assert sg.service_count == 1

    def test_get_service(self) -> None:
        sg = ServiceGenerator()
        sg.add_service("Svc", ["m"])
        assert sg.get_service("Svc") is not None

    def test_list_services(self) -> None:
        sg = ServiceGenerator()
        sg.add_service("S", ["m"])
        assert len(sg.list_services()) == 1

    def test_service_count(self) -> None:
        sg = ServiceGenerator()
        assert sg.service_count == 0

    def test_generate_service_code(self) -> None:
        sg = ServiceGenerator()
        sg.add_service("TestSvc", ["run"])
        code = sg.generate_service_code("TestSvc")
        assert "class TestSvc" in code

    def test_to_dict(self) -> None:
        sg = ServiceGenerator()
        sg.add_service("S", ["m"])
        assert "services" in sg.to_dict()


class TestRepositoryGenerator:
    def test_add_repository(self) -> None:
        rg = RepositoryGenerator()
        rg.add_repository("UserRepo", "User")
        assert rg.repository_count == 1

    def test_get_repository(self) -> None:
        rg = RepositoryGenerator()
        rg.add_repository("R", "E")
        assert rg.get_repository("R") is not None

    def test_generate_code(self) -> None:
        rg = RepositoryGenerator()
        rg.add_repository("PostRepo", "Post")
        code = rg.generate_repository_code("PostRepo")
        assert "class PostRepo" in code

    def test_to_dict(self) -> None:
        rg = RepositoryGenerator()
        rg.add_repository("R", "E")
        assert "repositories" in rg.to_dict()


class TestModelGenerator:
    def test_add_model(self) -> None:
        mg = ModelGenerator()
        mg.add_model("User", [{"name": "id", "type": "int"}])
        assert mg.model_count == 1

    def test_remove_model(self) -> None:
        mg = ModelGenerator()
        mg.add_model("U", [{"name": "id"}])
        assert mg.remove_model("U") is True

    def test_generate_code(self) -> None:
        mg = ModelGenerator()
        mg.add_model("User", [{"name": "name", "type": "str"}])
        code = mg.generate_model_code("User")
        assert "@dataclass" in code

    def test_to_dict(self) -> None:
        mg = ModelGenerator()
        mg.add_model("U", [{"name": "id"}])
        d = mg.to_dict()
        assert "models" in d


class TestMiddlewareGenerator:
    def test_add_middleware(self) -> None:
        mw = MiddlewareGenerator()
        mw.add_middleware("auth", 1, "AuthMiddleware")
        assert mw.middleware_count == 1

    def test_list_sorted(self) -> None:
        mw = MiddlewareGenerator()
        mw.add_middleware("b", 2, "B")
        mw.add_middleware("a", 1, "A")
        items = mw.list_middleware()
        assert items[0]["order"] == 1

    def test_generate_pipeline(self) -> None:
        mw = MiddlewareGenerator()
        mw.add_middleware("auth", 1, "Auth")
        assert "Pipeline" in mw.generate_pipeline()

    def test_to_dict(self) -> None:
        mw = MiddlewareGenerator()
        mw.add_middleware("m", 1, "M")
        assert "middleware" in mw.to_dict()


class TestAuthenticationGenerator:
    def test_add_provider(self) -> None:
        ag = AuthenticationGenerator()
        ag.add_provider("google", "oauth")
        assert ag.provider_count == 1

    def test_get_provider(self) -> None:
        ag = AuthenticationGenerator()
        ag.add_provider("g", "jwt")
        assert ag.get_provider("g") is not None

    def test_strategy_default(self) -> None:
        ag = AuthenticationGenerator()
        ag.add_provider("custom", "unknown")
        p = ag.get_provider("custom")
        assert p is not None
        assert p["strategy"] == "jwt"

    def test_generate_login_code(self) -> None:
        ag = AuthenticationGenerator()
        ag.add_provider("google", "oauth")
        code = ag.generate_login_code("google")
        assert "OAuth" in code

    def test_to_dict(self) -> None:
        ag = AuthenticationGenerator()
        ag.add_provider("g", "jwt")
        assert "providers" in ag.to_dict()


class TestWebSocketGenerator:
    def test_add_route(self) -> None:
        ws = WebSocketGenerator()
        ws.add_route("/ws", "ChatHandler")
        assert ws.route_count == 1

    def test_generate_code(self) -> None:
        ws = WebSocketGenerator()
        ws.add_route("/ws", "ChatHandler")
        code = ws.generate_handler_code("/ws")
        assert "class ChatHandler" in code

    def test_to_dict(self) -> None:
        ws = WebSocketGenerator()
        ws.add_route("/ws", "H")
        assert "routes" in ws.to_dict()


class TestAsyncOptimizer:
    def test_analyze_task(self) -> None:
        ao = AsyncOptimizer()
        results = ao.analyze_task("fetch from database")
        assert len(results) > 0

    def test_add_task(self) -> None:
        ao = AsyncOptimizer()
        ao.add_task("query", 100, True)
        assert ao.task_count == 1

    def test_estimate_speedup(self) -> None:
        ao = AsyncOptimizer()
        ao.add_task("a", 100, True)
        ao.add_task("b", 50, False)
        assert ao.estimate_speedup() > 1.0

    def test_to_dict(self) -> None:
        ao = AsyncOptimizer()
        ao.add_task("t", 10, True)
        assert "tasks" in ao.to_dict()


class TestPerformance:
    def test_profile_endpoint(self) -> None:
        p = Performance()
        r = p.profile_endpoint("/api/test", 50)
        assert "avg_ms" in r

    def test_add_metric(self) -> None:
        p = Performance()
        p.add_metric("latency", 42.5)
        assert p.metric_count == 1

    def test_suggest_optimizations(self) -> None:
        p = Performance()
        suggestions = p.suggest_optimizations()
        assert len(suggestions) > 0

    def test_to_dict(self) -> None:
        p = Performance()
        p.add_metric("m", 1.0)
        assert "metrics" in p.to_dict()


class TestSecurity:
    def test_add_rule(self) -> None:
        s = Security()
        s.add_rule("no_eval", "check for eval()", "critical")
        assert s.rule_count == 1

    def test_list_by_severity(self) -> None:
        s = Security()
        s.add_rule("r1", "check1", "high")
        s.add_rule("r2", "check2", "low")
        assert len(s.list_rules("high")) == 1

    def test_scan_code(self) -> None:
        s = Security()
        findings = s.scan_code("eval('danger')")
        assert len(findings) > 0

    def test_to_dict(self) -> None:
        s = Security()
        s.add_rule("r", "c", "high")
        assert "rules" in s.to_dict()


class TestDatabaseMapper:
    def test_map_table(self) -> None:
        dm = DatabaseMapper()
        dm.map_table("users", [{"name": "id", "type": "int"}])
        assert dm.table_count == 1

    def test_get_table(self) -> None:
        dm = DatabaseMapper()
        dm.map_table("t", [])
        assert dm.get_table("t") is not None

    def test_generate_mapping_code(self) -> None:
        dm = DatabaseMapper()
        dm.map_table("users", [{"name": "id", "type": "Integer"}])
        code = dm.generate_mapping_code("users")
        assert "class Users" in code

    def test_to_dict(self) -> None:
        dm = DatabaseMapper()
        dm.map_table("t", [])
        assert "tables" in dm.to_dict()


class TestBackendAgent:
    def test_engine_initializes(self) -> None:
        ba = BackendAgent()
        assert ba.api is not None
        assert ba.services is not None
        assert ba.repositories is not None
        assert ba.models is not None
        assert ba.middleware is not None
        assert ba.auth is not None
        assert ba.websocket is not None
        assert ba.async_optimizer is not None
        assert ba.performance is not None
        assert ba.security is not None
        assert ba.database_mapper is not None

    def test_generate_backend(self) -> None:
        ba = BackendAgent()
        result = ba.generate_backend(
            {
                "endpoints": [{"path": "/api", "method": "GET", "handler": "list"}],
                "services": [{"name": "Svc", "methods": ["exec"]}],
            }
        )
        assert result["status"] == "generated"
        assert result["endpoints"] == 1

    def test_get_status(self) -> None:
        ba = BackendAgent()
        status = ba.get_status()
        assert "endpoints" in status
        assert "services" in status

    def test_to_dict(self) -> None:
        ba = BackendAgent()
        d = ba.to_dict()
        assert d["agent"] == "backend_agent"
