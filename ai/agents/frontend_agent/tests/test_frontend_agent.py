from __future__ import annotations

from ..accessibility import Accessibility
from ..charts import Charts
from ..component_generator import ComponentGenerator
from ..forms import Forms
from ..frontend_agent import FrontendAgent
from ..page_generator import PageGenerator
from ..responsive import Responsive
from ..router_generator import RouterGenerator
from ..state_manager import StateManager
from ..theme_manager import ThemeManager
from ..validation import Validation


class TestComponentGenerator:
    def test_add_component(self) -> None:
        cg = ComponentGenerator()
        cg.add_component("Button", ["label", "onClick"])
        assert cg.component_count == 1

    def test_get_component(self) -> None:
        cg = ComponentGenerator()
        cg.add_component("B", ["p"])
        assert cg.get_component("B") is not None

    def test_remove_component(self) -> None:
        cg = ComponentGenerator()
        cg.add_component("C", [])
        assert cg.remove_component("C") is True

    def test_generate_code(self) -> None:
        cg = ComponentGenerator()
        cg.add_component("Button", ["label"])
        code = cg.generate_component_code("Button")
        assert "const Button" in code

    def test_to_dict(self) -> None:
        cg = ComponentGenerator()
        cg.add_component("B", [])
        assert "components" in cg.to_dict()


class TestPageGenerator:
    def test_add_page(self) -> None:
        pg = PageGenerator()
        pg.add_page("/", "Home")
        assert pg.page_count == 1

    def test_remove_page(self) -> None:
        pg = PageGenerator()
        pg.add_page("/", "H")
        assert pg.remove_page("/") is True

    def test_generate_code(self) -> None:
        pg = PageGenerator()
        pg.add_page("/about", "About")
        code = pg.generate_page_code("/about")
        assert "AboutPage" in code

    def test_to_dict(self) -> None:
        pg = PageGenerator()
        pg.add_page("/", "H")
        assert "pages" in pg.to_dict()


class TestRouterGenerator:
    def test_add_route(self) -> None:
        rg = RouterGenerator()
        rg.add_route("/", "Home")
        assert rg.route_count == 1

    def test_generate_code(self) -> None:
        rg = RouterGenerator()
        rg.add_route("/", "Home")
        code = rg.generate_router_code()
        assert "react-router-dom" in code

    def test_to_dict(self) -> None:
        rg = RouterGenerator()
        rg.add_route("/", "H")
        assert "routes" in rg.to_dict()


class TestStateManager:
    def test_add_store(self) -> None:
        sm = StateManager()
        sm.add_store("auth", {"user": None})
        assert sm.store_count == 1

    def test_generate_code(self) -> None:
        sm = StateManager()
        sm.add_store("auth", {"user": None})
        code = sm.generate_store_code("auth")
        assert "useAuthStore" in code

    def test_to_dict(self) -> None:
        sm = StateManager()
        sm.add_store("s", {})
        assert "stores" in sm.to_dict()


class TestThemeManager:
    def test_set_colors(self) -> None:
        tm = ThemeManager()
        tm.set_primary_color("#fff")
        theme = tm.get_theme()
        assert theme["primary_color"] == "#fff"

    def test_generate_css(self) -> None:
        tm = ThemeManager()
        css = tm.generate_css_variables()
        assert "--color-primary" in css

    def test_save_load_theme(self) -> None:
        tm = ThemeManager()
        tm.set_primary_color("#000")
        tm.save_theme("dark")
        tm.set_primary_color("#fff")
        assert tm.load_theme("dark") is True
        assert tm.get_theme()["primary_color"] == "#000"

    def test_to_dict(self) -> None:
        tm = ThemeManager()
        d = tm.to_dict()
        assert "current" in d


class TestForms:
    def test_add_field(self) -> None:
        f = Forms()
        f.add_field("email", "email", "Email", True)
        assert f.field_count == 1

    def test_generate_code(self) -> None:
        f = Forms()
        f.add_field("name", "text", "Name", True)
        code = f.generate_form_code()
        assert "AppForm" in code

    def test_to_dict(self) -> None:
        f = Forms()
        f.add_field("e", "text", "E")
        assert "fields" in f.to_dict()


class TestValidation:
    def test_add_rule(self) -> None:
        v = Validation()
        v.add_rule("custom", r"^\d{3}$", "Must be 3 digits")
        assert v.rule_count > 7  # builtins + custom

    def test_validate_email(self) -> None:
        v = Validation()
        results = v.validate("test@example.com", ["email"])
        assert results[0]["valid"] is True

    def test_validate_fail(self) -> None:
        v = Validation()
        results = v.validate("notanemail", ["email"])
        assert results[0]["valid"] is False

    def test_to_dict(self) -> None:
        v = Validation()
        assert "rules" in v.to_dict()


class TestAccessibility:
    def test_analyze_component(self) -> None:
        a = Accessibility()
        issues = a.analyze_component("<div></div>")
        assert len(issues) > 0

    def test_generate_fixes(self) -> None:
        a = Accessibility()
        fixes = a.generate_a11y_fixes([{"rule": "aria-label"}])
        assert len(fixes) > 0

    def test_to_dict(self) -> None:
        a = Accessibility()
        assert "rules" in a.to_dict()


class TestResponsive:
    def test_add_breakpoint(self) -> None:
        r = Responsive()
        r.add_breakpoint("watch", 200)
        assert r.breakpoint_count == 5  # 4 default + 1

    def test_generate_media_queries(self) -> None:
        r = Responsive()
        css = r.generate_media_queries()
        assert "@media" in css

    def test_to_dict(self) -> None:
        r = Responsive()
        assert "breakpoints" in r.to_dict()


class TestCharts:
    def test_add_chart(self) -> None:
        c = Charts()
        c.add_chart("Sales", "bar", ["revenue"])
        assert c.chart_count == 1

    def test_generate_code(self) -> None:
        c = Charts()
        c.add_chart("Sales", "line", ["revenue"])
        code = c.generate_chart_code("Sales")
        assert "react-chartjs-2" in code

    def test_to_dict(self) -> None:
        c = Charts()
        c.add_chart("S", "bar", ["f"])
        assert "charts" in c.to_dict()


class TestFrontendAgent:
    def test_engine_initializes(self) -> None:
        fa = FrontendAgent()
        assert fa.components is not None
        assert fa.pages is not None
        assert fa.routers is not None
        assert fa.state is not None
        assert fa.theme is not None
        assert fa.forms is not None
        assert fa.validation is not None
        assert fa.accessibility is not None
        assert fa.responsive is not None
        assert fa.charts is not None

    def test_generate_frontend(self) -> None:
        fa = FrontendAgent()
        result = fa.generate_frontend({"pages": [{"path": "/", "component": "Home"}]})
        assert result["status"] == "generated"

    def test_get_status(self) -> None:
        fa = FrontendAgent()
        s = fa.get_status()
        assert "components" in s

    def test_to_dict(self) -> None:
        fa = FrontendAgent()
        d = fa.to_dict()
        assert d["agent"] == "frontend_agent"
