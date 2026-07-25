from __future__ import annotations

import asyncio
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiofiles
import aiohttp

from pydantic import BaseModel, Field


class PluginType(str, Enum):
    TOOL = "tool"
    AGENT = "agent"
    PROVIDER = "provider"
    INTEGRATION = "integration"
    UI = "ui"
    COMMAND = "command"
    WORKFLOW = "workflow"


class PluginStatus(str, Enum):
    PENDING = "pending"
    INSTALLING = "installing"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"
    UNINSTALLING = "uninstalling"


@dataclass
class PluginManifest:
    name: str
    slug: str
    version: str
    description: str
    author: str
    author_email: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    plugin_type: PluginType = PluginType.TOOL
    tags: List[str] = field(default_factory=list)
    min_platform_version: str = "5.0.0"
    max_platform_version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    entrypoint: str = "plugin.py"
    icon_url: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginConfig:
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


class BasePlugin:
    def __init__(self, metadata: PluginManifest, config: PluginConfig = None):
        self.metadata = metadata
        self.config = config or PluginConfig()
        self._status = PluginStatus.INSTALLED
        self._hooks: Dict[str, List] = {}

    @property
    def status(self) -> PluginStatus:
        return self._status

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def slug(self) -> str:
        return self.metadata.slug

    @property
    def version(self) -> str:
        return self.metadata.version

    async def on_activate(self) -> None:
        pass

    async def on_deactivate(self) -> None:
        pass

    async def on_config_change(self, config: Dict[str, Any]) -> None:
        self.config.settings.update(config)

    def register_hook(self, hook_name: str, handler) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(handler)

    async def trigger_hook(self, hook_name: str, **kwargs) -> List[Any]:
        results = []
        for handler in self._hooks.get(hook_name, []):
            try:
                result = await handler(**kwargs) if asyncio.iscoroutinefunction(handler) else handler(**kwargs)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        return results

    def get_api(self) -> Dict[str, Any]:
        return {
            "name": self.metadata.name,
            "slug": self.metadata.slug,
            "version": self.metadata.version,
            "status": self._status.value,
            "config": self.config.settings,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": {
                "name": self.metadata.name,
                "slug": self.metadata.slug,
                "version": self.metadata.version,
                "description": self.metadata.description,
                "author": self.metadata.author,
                "plugin_type": self.metadata.plugin_type.value,
                "tags": self.metadata.tags,
                "dependencies": self.metadata.dependencies,
            },
            "status": self._status.value,
            "config": self.config.settings,
        }


class PluginSDK:
    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or Path.cwd() / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def create_plugin(
        self,
        name: str,
        template: str = "tool",
        author: str = "SuperDev User",
        description: str = "",
    ) -> Path:
        plugin_path = self.plugins_dir / name
        plugin_path.mkdir(parents=True, exist_ok=True)

        manifest = self._generate_manifest(name, template, author, description)
        manifest_path = plugin_path / "plugin.superdev.yaml"
        manifest_path.write_text(manifest.to_yaml())

        (plugin_path / "plugin.py").write_text(self._generate_plugin_code(name, template))
        (plugin_path / "__init__.py").write_text(f"from .plugin import {name.capitalize()}Plugin\n")
        (plugin_path / "README.md").write_text(f"# {name}\n\n{description or f'A {template} plugin for SuperDev'}\n")
        (plugin_path / "LICENSE").write_text("MIT License\n\nCopyright (c) 2024 SuperDev User\n")
        (plugin_path / ".gitignore").write_text("__pycache__/\n*.pyc\n.env\n*.superdev-plugin\n")

        return plugin_path

    def build_package(self, plugin_path: str | Path) -> Path:
        plugin_path = Path(plugin_path)
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin not found: {plugin_path}")

        package_path = plugin_path.parent / f"{plugin_path.name}.superdev-plugin"
        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(plugin_path):
                for file in files:
                    file_path = Path(root) / file
                    arcname = str(file_path.relative_to(plugin_path.parent))
                    zf.write(file_path, arcname)

        return package_path

    def validate_package(self, package_path: str | Path) -> bool:
        package_path = Path(package_path)
        if not package_path.exists():
            return False
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                files = zf.namelist()
                has_manifest = any("plugin.superdev.yaml" in f for f in files)
                has_entry = any(f.endswith(".py") for f in files)
                return has_manifest and has_entry
        except zipfile.BadZipFile:
            return False

    def publish_package(
        self,
        package_path: str | Path,
        api_key: str,
        registry_url: str = "https://marketplace.superdev.ai",
    ) -> bool:
        package_path = Path(package_path)
        with open(package_path, "rb") as f:
            response = httpx.post(
                f"{registry_url}/api/plugins/publish",
                files={"package": f},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60,
            )
        return response.status_code == 200

    def _generate_manifest(
        self,
        name: str,
        template: str,
        author: str,
        description: str,
    ) -> PluginManifest:
        return PluginManifest(
            name=name,
            slug=name.lower().replace(" ", "-"),
            version="1.0.0",
            author=author,
            description=description or f"A {template} plugin for SuperDev",
            license="MIT",
            entrypoint="plugin.py",
            category=template,
            permissions=["filesystem.read"],
            dependencies=[],
        )

    def _generate_plugin_code(self, name: str, template: str) -> str:
        class_name = f"{name.capitalize()}Plugin"

        templates = {
            "tool": self._tool_template,
            "agent": self._agent_template,
            "integration": self._integration_template,
            "provider": self._provider_template,
            "command": self._command_template,
            "ui": self._ui_template,
        }

        generator = templates.get(template, self._tool_template)
        return generator(name, class_name)

    def _tool_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI

api = PluginAPI()

class {class_name}:
    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.api = api
        self._initialized = False

    async def initialize(self, config: dict = None):
        """Initialize the plugin with configuration"""
        self.config = config or {{}}
        self._initialized = True
        api.register_hook("startup", self.on_startup)
        api.register_command("{name}", self.execute)
        print(f"Plugin {{self.name}} initialized")

    async def on_startup(self, context):
        """Called when platform starts"""
        print(f"Plugin {{self.name}} started")

    async def execute(self, params: dict) -> dict:
        """Main execution method"""
        action = params.get("action", "default")
        
        if action == "default":
            return {{"status": "ok", "message": f"Executed {{self.name}} with {{params}}"}}
        
        return {{"status": "error", "message": f"Unknown action: {{action}}"}}

    async def cleanup(self):
        """Cleanup resources"""
        print(f"Plugin {{self.name}} cleaned up")
'''

    def _agent_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI
from backend.agents.base.base_agent import BaseAgent, AgentConfig, AgentResult

api = PluginAPI()

class {class_name}(BaseAgent):
    def __init__(self, config: AgentConfig = None):
        super().__init__(config or AgentConfig(name="{name}"))
        self.api = api

    async def execute(self, task: str, context: dict = None) -> AgentResult:
        """Execute agent task"""
        context = context or {{}}
        
        try:
            result = await self._process_task(task, context)
            return AgentResult(success=True, output=result)
        except Exception as e:
            return AgentResult(success=False, error=str(e))

    async def _process_task(self, task: str, context: dict) -> dict:
        """Process the agent task"""
        return {{"task": task, "processed": True, "agent": "{name}"}}

    async def on_startup(self):
        api.register_hook("agent_task", self.execute)
        print(f"Agent {{self.config.name}} started")

    async def on_shutdown(self):
        print(f"Agent {{self.config.name}} stopped")
'''

    def _integration_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI
import httpx

api = PluginAPI()

class {class_name}:
    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.api = api
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self, config: dict = None):
        self.config = config or {{}}
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url", ""),
            headers=self.config.get("headers", {{}}),
            timeout=self.config.get("timeout", 30),
        )
        api.register_hook("integration_request", self.handle_request)
        api.register_command("{name}", self.execute)
        print(f"Integration {{self.name}} initialized")

    async def handle_request(self, request: dict) -> dict:
        """Handle incoming integration requests"""
        action = request.get("action")
        return await self.execute({{"action": action, **request.get("params", {{}})}})

    async def execute(self, params: dict) -> dict:
        action = params.get("action", "test")
        
        if action == "test":
            return await self.test_connection()
        
        return {{"status": "error", "message": f"Unknown action: {{action}}"}}

    async def test_connection(self) -> dict:
        if not self.client:
            return {{"status": "error", "message": "Not initialized"}}
        try:
            resp = await self.client.get("/health")
            return {{"status": "ok", "connected": resp.status_code == 200}}
        except Exception as e:
            return {{"status": "error", "message": str(e)}}

    async def cleanup(self):
        if self.client:
            await self.client.aclose()
        print(f"Integration {{self.name}} cleaned up")
'''

    def _provider_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI
from backend.ai_platform.providers.base_provider import BaseProvider, ModelInfo, ChatResponse, Choice, Usage

api = PluginAPI()

class {class_name}(BaseProvider):
    def __init__(self, config):
        super().__init__(config)
        self._client = None

    async def authenticate(self) -> str:
        return "authenticated"

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(id="{name}-model", name="{name} Model", provider="{name}", capabilities=["chat"])
        ]

    async def chat(self, messages: list[dict], config: dict) -> ChatResponse:
        return ChatResponse(
            id=f"{{name}}-{{int(time.time())}}",
            model=config.get("model", "{name}-model"),
            choices=[Choice(index=0, message={{"role": "assistant", "content": f"Response from {{self.name}}"}})],
            usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            provider="{name}",
        )

    async def stream(self, messages: list[dict], config: dict):
        yield StreamChunk(delta="Response from {name}", finish_reason="stop")

    async def health(self):
        from backend.ai_platform.providers.base_provider import HealthStatus
        from datetime import datetime, timezone
        return HealthStatus(status="healthy", last_check=datetime.now(timezone.utc))
'''

    def _command_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI

api = PluginAPI()

class {class_name}:
    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.api = api

    async def initialize(self, config: dict = None):
        self.config = config or {{}}
        api.register_command("{name}", self.execute)
        print(f"Command {{self.name}} registered")

    async def execute(self, params: dict) -> dict:
        subcommand = params.get("subcommand", "help")
        
        if subcommand == "help":
            return {{
                "status": "ok",
                "help": f"{{self.name}} - A CLI command plugin",
                "usage": f"superdev {{self.name}} <subcommand> [options]",
                "subcommands": ["help", "run", "config"]
            }}
        
        elif subcommand == "run":
            return {{"status": "ok", "message": f"Running {{self.name}}", "params": params}}
        
        elif subcommand == "config":
            return {{"status": "ok", "config": self.config}}
        
        return {{"status": "error", "message": f"Unknown subcommand: {{subcommand}}"}}
'''

    def _ui_template(self, name: str, class_name: str) -> str:
        return f'''from backend.plugin_platform.sdk.plugin_api import PluginAPI

api = PluginAPI()

class {class_name}:
    def __init__(self):
        self.name = "{name}"
        self.version = "1.0.0"
        self.api = api

    async def initialize(self, config: dict = None):
        self.config = config or {{}}
        api.register_hook("ui_render", self.render)
        api.register_hook("ui_actions", self.get_actions)
        print(f"UI Plugin {{self.name}} initialized")

    async def render(self, context: dict) -> dict:
        return {{
            "component": "{name}",
            "props": context,
            "template": f"<div class='plugin-{{self.name}}'>{{{{title}}}}</div>"
        }}

    async def get_actions(self) -> list[dict]:
        return [
            {{"id": "action1", "label": "Action 1", "handler": "handle_action1"}},
            {{"id": "action2", "label": "Action 2", "handler": "handle_action2"}},
        ]

    async def handle_action1(self, payload: dict) -> dict:
        return {{"status": "ok", "action": "action1", "payload": payload}}

    async def handle_action2(self, payload: dict) -> dict:
        return {{"status": "ok", "action": "action2", "payload": payload}}
'''


# Export
__all__ = [
    "PluginType",
    "PluginStatus",
    "PluginManifest",
    "PluginConfig",
    "BasePlugin",
    "PluginSDK",
]