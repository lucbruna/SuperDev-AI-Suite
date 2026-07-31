"""Tests for plugins module: base_plugin, plugin_manager."""

import pytest
from backend.plugins.base_plugin import (
    BasePlugin,
    PluginConfig,
    PluginMetadata,
    PluginStatus,
    PluginType,
)


# ── Enums ───────────────────────────────────────────────────────────


class TestPluginEnums:
    def test_plugin_status_values(self):
        assert PluginStatus.INSTALLED.value == "installed"
        assert PluginStatus.ENABLED.value == "enabled"
        assert PluginStatus.DISABLED.value == "disabled"
        assert PluginStatus.ERROR.value == "error"
        assert PluginStatus.UPDATING.value == "updating"

    def test_plugin_type_values(self):
        assert PluginType.EXTENSION.value == "extension"
        assert PluginType.INTEGRATION.value == "integration"
        assert PluginType.TOOL.value == "tool"
        assert PluginType.PROVIDER.value == "provider"
        assert PluginType.UI.value == "ui"
        assert PluginType.COMMAND.value == "command"


# ── PluginMetadata ──────────────────────────────────────────────────


class TestPluginMetadata:
    def test_defaults(self):
        meta = PluginMetadata(name="Test", slug="test", version="1.0.0")
        assert meta.description == ""
        assert meta.author == ""
        assert meta.license == "MIT"
        assert meta.plugin_type == PluginType.EXTENSION
        assert meta.tags == []
        assert meta.min_platform_version == "5.0.0"
        assert meta.max_platform_version is None
        assert meta.dependencies == []
        assert meta.config_schema == {}
        assert meta.icon_url is None

    def test_custom_values(self):
        meta = PluginMetadata(
            name="Custom",
            slug="custom",
            version="2.0.0",
            description="A custom plugin",
            author="Test Author",
            plugin_type=PluginType.TOOL,
            tags=["tool", "utility"],
        )
        assert meta.description == "A custom plugin"
        assert meta.plugin_type == PluginType.TOOL
        assert meta.tags == ["tool", "utility"]


# ── PluginConfig ────────────────────────────────────────────────────


class TestPluginConfig:
    def test_defaults(self):
        config = PluginConfig()
        assert config.enabled is True
        assert config.settings == {}

    def test_custom(self):
        config = PluginConfig(enabled=False, settings={"key": "value"})
        assert config.enabled is False
        assert config.settings["key"] == "value"


# ── BasePlugin (concrete implementation for testing) ────────────────


class ConcretePlugin(BasePlugin):
    async def on_activate(self):
        pass

    async def on_deactivate(self):
        pass


class TestBasePlugin:
    def _make_plugin(self, **kwargs):
        meta = PluginMetadata(name="Test", slug="test", version="1.0.0", **kwargs)
        return ConcretePlugin(metadata=meta)

    def test_initial_status(self):
        plugin = self._make_plugin()
        assert plugin.status == PluginStatus.INSTALLED

    def test_name_property(self):
        plugin = self._make_plugin()
        assert plugin.name == "Test"

    def test_slug_property(self):
        plugin = self._make_plugin()
        assert plugin.slug == "test"

    def test_version_property(self):
        plugin = self._make_plugin()
        assert plugin.version == "1.0.0"

    @pytest.mark.asyncio
    async def test_activate(self):
        plugin = self._make_plugin()
        await plugin.activate()
        assert plugin.status == PluginStatus.ENABLED

    @pytest.mark.asyncio
    async def test_deactivate(self):
        plugin = self._make_plugin()
        await plugin.activate()
        await plugin.deactivate()
        assert plugin.status == PluginStatus.DISABLED

    @pytest.mark.asyncio
    async def test_on_config_change(self):
        plugin = self._make_plugin()
        await plugin.on_config_change({"key": "value"})
        assert plugin.config.settings["key"] == "value"

    def test_register_hook(self):
        plugin = self._make_plugin()
        handler = lambda **kw: None
        plugin.register_hook("on_event", handler)
        assert "on_event" in plugin._hooks
        assert handler in plugin._hooks["on_event"]

    @pytest.mark.asyncio
    async def test_trigger_hook_empty(self):
        plugin = self._make_plugin()
        results = await plugin.trigger_hook("nonexistent")
        assert results == []

    @pytest.mark.asyncio
    async def test_trigger_hook_with_handler(self):
        plugin = self._make_plugin()

        async def handler(**kwargs):
            return kwargs.get("value", 0) * 2

        plugin.register_hook("on_event", handler)
        results = await plugin.trigger_hook("on_event", value=5)
        assert results == [10]

    @pytest.mark.asyncio
    async def test_trigger_hook_error_handling(self):
        plugin = self._make_plugin()

        async def bad_handler(**kwargs):
            raise RuntimeError("oops")

        plugin.register_hook("on_event", bad_handler)
        results = await plugin.trigger_hook("on_event")
        assert len(results) == 1
        assert "error" in results[0]

    def test_get_api(self):
        plugin = self._make_plugin()
        api = plugin.get_api()
        assert api["name"] == "Test"
        assert api["slug"] == "test"
        assert api["version"] == "1.0.0"
        assert api["status"] == "installed"

    def test_to_dict(self):
        plugin = self._make_plugin(description="desc", tags=["a"])
        d = plugin.to_dict()
        assert d["metadata"]["name"] == "Test"
        assert d["metadata"]["description"] == "desc"
        assert d["metadata"]["tags"] == ["a"]
        assert d["status"] == "installed"

    def test_config_default(self):
        plugin = self._make_plugin()
        assert plugin.config.enabled is True
        assert plugin.config.settings == {}

    def test_config_custom(self):
        meta = PluginMetadata(name="T", slug="t", version="1.0.0")
        config = PluginConfig(enabled=False, settings={"debug": True})
        plugin = ConcretePlugin(metadata=meta, config=config)
        assert plugin.config.enabled is False
        assert plugin.config.settings["debug"] is True
