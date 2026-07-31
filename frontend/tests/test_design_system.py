from __future__ import annotations

from frontend.design_system.design_engine import DesignEngine
from frontend.design_system.colors import ColorPalette
from frontend.themes.theme_manager import ThemeManager
from frontend.components.components_engine import ComponentsEngine
from frontend.components import create_engine


def test_design_engine_seed_defaults() -> None:
    engine = DesignEngine()
    engine.seed_defaults()
    assert len(engine.tokens()) > 0


def test_color_palette_modes() -> None:
    palette = ColorPalette()
    light = palette.get_colors()
    palette.set_mode("dark")
    dark = palette.get_colors()
    assert light != dark


def test_theme_manager_apply() -> None:
    manager = ThemeManager()
    manager.register("dark", {"colors.background": "#1e1e2e"})
    applied = manager.apply("dark")
    assert applied == "dark"
    assert manager.active == "dark"


def test_components_library() -> None:
    engine: ComponentsEngine = create_engine()
    components = engine.list()
    assert len(components) >= 10
    rendered = engine.render(components[0])
    assert rendered is not None
