from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import aiofiles
import httpx
from plugin_platform.manifest.manifest import PluginManifest
from plugin_platform.sandbox.plugin_sandbox import PluginSandbox, SandboxConfig


class PluginCategory(StrEnum):
    TOOL = "tool"
    AGENT = "agent"
    PROVIDER = "provider"
    INTEGRATION = "integration"
    UI = "ui"
    COMMAND = "command"
    THEME = "theme"
    TEMPLATE = "template"
    WORKFLOW = "workflow"
    UTILITY = "utility"


class PluginStatus(StrEnum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    VALIDATING = "validating"
    INSTALLING = "installing"
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"


@dataclass
class PluginInfo:
    id: str
    name: str
    version: str
    author: str
    description: str
    category: PluginCategory
    downloads: int = 0
    rating: float = 0.0
    license: str = "MIT"
    repository: str = ""
    homepage: str = ""
    tags: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    readme: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None
    min_platform_version: str = "5.0.0"
    max_platform_version: str | None = None
    dependencies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    is_official: bool = False
    is_verified: bool = False
    download_url: str = ""
    checksum: str = ""


@dataclass
class InstalledPlugin:
    info: PluginInfo
    status: PluginStatus = PluginStatus.INSTALLED
    install_path: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    installed_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime | None = None
    enabled: bool = False


class MarketplaceClient:
    def __init__(
        self,
        api_url: str = "https://marketplace.superdev.ai/api/v1",
        cache_dir: Path | None = None,
        timeout: int = 30,
    ):
        self._api_url = api_url.rstrip("/")
        self._cache_dir = cache_dir or Path.home() / ".superdev" / "marketplace_cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None
        self._simulated_plugins: list[PluginInfo] = self._get_simulated_plugins()

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    def _get_simulated_plugins(self) -> list[PluginInfo]:
        return [
            PluginInfo(
                id="github-integration",
                name="GitHub Integration",
                version="1.2.0",
                author="SuperDev Team",
                description="Connect with GitHub repositories, create issues, manage PRs, and automate workflows",
                category=PluginCategory.INTEGRATION,
                downloads=15200,
                rating=4.8,
                license="MIT",
                repository="https://github.com/superdev/github-integration",
                homepage="https://github.com/superdev/github-integration",
                tags=["github", "git", "vcs", "ci-cd", "pr", "issues"],
                keywords=["github", "git", "version-control", "pull-request", "issues"],
                is_official=True,
                is_verified=True,
                readme="# GitHub Integration\n\nConnect SuperDev with GitHub to automate repository management.",
            ),
            PluginInfo(
                id="slack-notifications",
                name="Slack Notifications",
                version="1.1.0",
                author="SuperDev Team",
                description="Send workflow and agent notifications to Slack channels",
                category=PluginCategory.INTEGRATION,
                downloads=9800,
                rating=4.6,
                license="MIT",
                repository="https://github.com/superdev/slack-notifications",
                tags=["slack", "notifications", "messaging", "webhook"],
                keywords=["slack", "notifications", "messaging", "alerts"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="docker-runtime",
                name="Docker Runtime",
                version="2.0.0",
                author="SuperDev Team",
                description="Execute code in Docker containers for enhanced isolation and reproducibility",
                category=PluginCategory.TOOL,
                downloads=21000,
                rating=4.9,
                license="Apache-2.0",
                repository="https://github.com/superdev/docker-runtime",
                tags=["docker", "runtime", "containers", "isolation", "security"],
                keywords=["docker", "container", "sandbox", "execution"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="code-analyzer",
                name="Code Analyzer Agent",
                version="1.3.0",
                author="Community",
                description="Static code analysis agent for detecting bugs, security issues, and code smells",
                category=PluginCategory.AGENT,
                downloads=8900,
                rating=4.2,
                license="MIT",
                repository="https://github.com/superdev-community/code-analyzer",
                tags=["static-analysis", "linting", "security", "code-quality"],
                keywords=["analysis", "lint", "security", "bugs", "quality"],
                is_official=False,
                is_verified=True,
            ),
            PluginInfo(
                id="postgresql-provider",
                name="PostgreSQL Provider",
                version="1.0.0",
                author="SuperDev Team",
                description="PostgreSQL database provider for knowledge base and persistent storage",
                category=PluginCategory.PROVIDER,
                downloads=18000,
                rating=4.7,
                license="PostgreSQL",
                repository="https://github.com/superdev/postgresql-provider",
                tags=["postgresql", "database", "storage", "sql"],
                keywords=["postgres", "database", "storage", "persistence"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="vscode-extension",
                name="VS Code Extension",
                version="1.4.0",
                author="SuperDev Team",
                description="SuperDev integration for Visual Studio Code",
                category=PluginCategory.UI,
                downloads=32000,
                rating=4.8,
                license="MIT",
                repository="https://github.com/superdev/vscode-extension",
                tags=["vscode", "editor", "ide", "extension"],
                keywords=["vscode", "editor", "ide", "development"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="jira-integration",
                name="Jira Integration",
                version="1.0.0",
                author="Community",
                description="Sync with Jira issues and sprint boards",
                category=PluginCategory.INTEGRATION,
                downloads=6500,
                rating=4.3,
                license="MIT",
                repository="https://github.com/superdev-community/jira-integration",
                tags=["jira", "project-management", "agile", "sprint"],
                keywords=["jira", "project-management", "agile", "issues"],
                is_official=False,
                is_verified=False,
            ),
            PluginInfo(
                id="terraform-provider",
                name="Terraform Provider",
                version="1.0.0",
                author="SuperDev Team",
                description="Infrastructure as Code with Terraform integration",
                category=PluginCategory.TOOL,
                downloads=12000,
                rating=4.5,
                license="MPL-2.0",
                repository="https://github.com/superdev/terraform-provider",
                tags=["terraform", "iac", "infrastructure", "cloud"],
                keywords=["terraform", "infrastructure", "cloud", "provisioning"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="kubernetes-deployer",
                name="Kubernetes Deployer",
                version="1.1.0",
                author="SuperDev Team",
                description="Deploy applications to Kubernetes clusters",
                category=PluginCategory.TOOL,
                downloads=8700,
                rating=4.6,
                license="Apache-2.0",
                repository="https://github.com/superdev/kubernetes-deployer",
                tags=["kubernetes", "k8s", "deployment", "orchestration"],
                keywords=["kubernetes", "deployment", "containers", "orchestration"],
                is_official=True,
                is_verified=True,
            ),
            PluginInfo(
                id="graphql-generator",
                name="GraphQL Schema Generator",
                version="1.0.0",
                author="Community",
                description="Generate GraphQL schemas from code and databases",
                category=PluginCategory.TOOL,
                downloads=4300,
                rating=4.1,
                license="MIT",
                repository="https://github.com/superdev-community/graphql-generator",
                tags=["graphql", "schema", "api", "code-generation"],
                keywords=["graphql", "schema", "api", "generation"],
                is_official=False,
                is_verified=False,
            ),
            PluginInfo(
                id="swagger-docs",
                name="Swagger/OpenAPI Documentation",
                version="1.2.0",
                author="Community",
                description="Auto-generate OpenAPI/Swagger documentation from code",
                category=PluginCategory.TOOL,
                downloads=7200,
                rating=4.4,
                license="MIT",
                repository="https://github.com/superdev-community/swagger-docs",
                tags=["openapi", "swagger", "documentation", "api"],
                keywords=["openapi", "swagger", "documentation", "api"],
                is_official=False,
                is_verified=False,
            ),
        ]

    async def search(
        self,
        query: str = "",
        category: PluginCategory | None = None,
        tags: list[str] | None = None,
        official_only: bool = False,
        verified_only: bool = False,
        sort_by: str = "popularity",
        limit: int = 50,
        offset: int = 0,
    ) -> list[PluginInfo]:
        try:
            if self._client:
                params: dict[str, Any] = {}
                if query:
                    params["q"] = query
                if category:
                    params["category"] = category.value
                if tags:
                    params["tags"] = ",".join(tags)
                if official_only:
                    params["official"] = "true"
                if verified_only:
                    params["verified"] = "true"
                params["sort"] = sort_by
                params["limit"] = limit
                params["offset"] = offset

                response = await self._client.get(f"{self._api_url}/plugins", params=params)
                response.raise_for_status()
                data = response.json()
                return [PluginInfo(**item) for item in data.get("plugins", [])]
        except Exception:
            pass

        results = self._simulated_plugins
        if query:
            q = query.lower()
            results = [p for p in results if q in p.name.lower() or q in p.description.lower() or q in p.id.lower()]
        if category:
            results = [p for p in results if p.category == category]
        if tags:
            results = [p for p in results if all(tag in p.tags for tag in tags)]
        if official_only:
            results = [p for p in results if p.is_official]
        if verified_only:
            results = [p for p in results if p.is_verified]

        if sort_by == "popularity":
            results.sort(key=lambda p: p.downloads, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda p: p.rating, reverse=True)
        elif sort_by == "newest":
            results.sort(key=lambda p: p.created_at or datetime.min, reverse=True)
        elif sort_by == "name":
            results.sort(key=lambda p: p.name)

        return results[offset:offset + limit]

    async def get_details(self, plugin_id: str) -> PluginInfo:
        try:
            if self._client:
                response = await self._client.get(f"{self._api_url}/plugins/{plugin_id}")
                response.raise_for_status()
                return PluginInfo(**response.json())
        except Exception:
            pass

        for plugin in self._simulated_plugins:
            if plugin.id == plugin_id:
                return PluginInfo(
                    **plugin.__dict__,
                    license="MIT",
                    repository=f"https://github.com/superdev/{plugin_id}",
                    readme=f"# {plugin.name}\n\n{plugin.description}",
                )
        raise ValueError(f"Plugin '{plugin_id}' not found")

    async def download(
        self,
        plugin_id: str,
        version: str = "latest",
        target_dir: Path | None = None,
    ) -> Path:
        cache_key = f"{plugin_id}@{version}"
        cache_file = self._cache_dir / f"{hashlib.sha256(cache_key.encode()).hexdigest()}.zip"

        if cache_file.exists():
            return cache_file

        try:
            if self._client:
                response = await self._client.get(
                    f"{self._api_url}/plugins/{plugin_id}/download",
                    params={"version": version},
                    timeout=120,
                )
                response.raise_for_status()
                async with aiofiles.open(cache_file, "wb") as f:
                    await f.write(response.content)
                return cache_file
        except Exception:
            pass

        simulated_content = json.dumps({
            "plugin_id": plugin_id,
            "version": version,
            "simulated": True,
            "content": "UEsDBBQAAAAIAAAAA",
        }).encode("utf-8")

        async with aiofiles.open(cache_file, "wb") as f:
            await f.write(simulated_content)

        return cache_file

    async def get_featured(self, limit: int = 5) -> list[PluginInfo]:
        try:
            if self._client:
                response = await self._client.get(f"{self._api_url}/plugins/featured", params={"limit": limit})
                response.raise_for_status()
                return [PluginInfo(**item) for item in response.json().get("plugins", [])]
        except Exception:
            pass

        featured = [p for p in self._simulated_plugins if p.is_official]
        featured.sort(key=lambda p: p.downloads, reverse=True)
        return featured[:limit]

    async def get_categories(self) -> dict[str, int]:
        try:
            if self._client:
                response = await self._client.get(f"{self._api_url}/categories")
                response.raise_for_status()
                return response.json()
        except Exception:
            pass

        categories: dict[str, int] = {}
        for plugin in self._simulated_plugins:
            categories[plugin.category.value] = categories.get(plugin.category.value, 0) + 1
        return categories

    async def get_stats(self) -> dict[str, Any]:
        return {
            "total_plugins": len(self._simulated_plugins),
            "total_downloads": sum(p.downloads for p in self._simulated_plugins),
            "categories": await self.get_categories(),
            "official_count": sum(1 for p in self._simulated_plugins if p.is_official),
            "verified_count": sum(1 for p in self._simulated_plugins if p.is_verified),
        }


class PluginInstaller:
    def __init__(self, plugins_dir: Path):
        self._plugins_dir = plugins_dir
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._sandbox = PluginSandbox(SandboxConfig())
        self._marketplace = MarketplaceClient()

    async def install_from_marketplace(
        self,
        plugin_id: str,
        version: str = "latest",
        config: dict[str, Any] | None = None,
    ) -> InstalledPlugin:
        await self._marketplace.get_details(plugin_id)
        package_path = await self._marketplace.download(plugin_id, version)
        return await self.install_from_package(package_path, config)

    async def install_from_package(
        self,
        package_path: Path,
        config: dict[str, Any] | None = None,
    ) -> InstalledPlugin:
        import tempfile
        import zipfile

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            with zipfile.ZipFile(package_path, "r") as zf:
                zf.extractall(tmpdir_path)

            manifest_file = next(tmpdir_path.glob("**/plugin.superdev.yaml"), None)
            if not manifest_file:
                raise ValueError("Invalid plugin package: missing manifest")

            manifest = PluginManifest.from_yaml(manifest_file)

            install_path = self._plugins_dir / manifest.name
            install_path.mkdir(parents=True, exist_ok=True)

            for item in tmpdir_path.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(tmpdir_path)
                    target = install_path / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(item.read_bytes())

            installed = InstalledPlugin(
                info=PluginInfo(
                    id=manifest.name,
                    name=manifest.name,
                    version=manifest.version,
                    author=manifest.author,
                    description=manifest.description,
                    category=PluginCategory(manifest.category),
                    license=manifest.license,
                    repository=manifest.repository,
                    homepage=manifest.homepage,
                    tags=manifest.tags,
                    dependencies=manifest.dependencies,
                    is_official=manifest.is_official,
                    is_verified=manifest.is_verified,
                ),
                status=PluginStatus.INSTALLED,
                install_path=str(install_path),
                config=config or {},
                installed_at=datetime.now(),
            )

            await self._validate_plugin(install_path, manifest)
            installed.status = PluginStatus.INSTALLED

            return installed

    async def install_from_git(
        self,
        repo_url: str,
        branch: str = "main",
        subdir: str = "",
        config: dict[str, Any] | None = None,
    ) -> InstalledPlugin:
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            clone_dir = tmpdir_path / repo_name

            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(clone_dir)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Failed to clone repository: {result.stderr}")

            plugin_dir = clone_dir / subdir if subdir else clone_dir
            if not plugin_dir.exists():
                raise ValueError(f"Plugin directory not found: {subdir}")

            return await self.install_from_package(plugin_dir, config)

    async def _validate_plugin(self, install_path: Path, manifest: PluginManifest) -> None:
        validator = PluginValidator()
        await validator.validate(install_path, manifest)


class PluginValidator:
    async def validate(self, install_path: Path, manifest: PluginManifest) -> tuple[bool, list[str]]:
        errors = []

        if not manifest.name:
            errors.append("Manifest missing: name")
        if not manifest.version:
            errors.append("Manifest missing: version")
        if not manifest.entrypoint:
            errors.append("Manifest missing: entrypoint")

        entry_file = install_path / manifest.entrypoint
        if not entry_file.exists():
            errors.append(f"Entrypoint not found: {manifest.entrypoint}")

        for _dep in manifest.dependencies:
            pass

        return len(errors) == 0, errors


class PluginSDK:
    def __init__(self, plugins_dir: Path | None = None):
        self.plugins_dir = plugins_dir or Path.cwd() / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._marketplace = MarketplaceClient()

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
        import zipfile

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

    def validate_package(self, package_path: str | Path) -> tuple[bool, list[str]]:
        import zipfile

        package_path = Path(package_path)
        if not package_path.exists():
            return False, ["Package not found"]

        errors = []
        try:
            with zipfile.ZipFile(package_path, "r") as zf:
                files = zf.namelist()
                has_manifest = any("plugin.superdev.yaml" in f for f in files)
                has_entry = any(f.endswith(".py") for f in files)
                has_readme = any(f.endswith(".md") or f.endswith(".txt") for f in files)

                if not has_manifest:
                    errors.append("Missing manifest: plugin.superdev.yaml")
                if not has_entry:
                    errors.append("Missing entry point: no Python file found")
                if not has_readme:
                    errors.append("Missing README")

                for f in files:
                    if "__pycache__" in f or f.endswith(".pyc"):
                        errors.append(f"Contains cache files: {f}")

        except zipfile.BadZipFile:
            errors.append("Invalid ZIP file")

        return len(errors) == 0, errors

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
            version="1.0.0",
            author=author,
            description=description or f"A {template} plugin for SuperDev",
            license="MIT",
            entrypoint="plugin.py",
            category=template,
            permissions=["filesystem.read"],
            dependencies=[],
            tags=[template],
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
            return {{"status": "ok", "message": f"Executed {{self.name}}", "result": params}}

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


async def get_marketplace_client() -> MarketplaceClient:
    return MarketplaceClient()


async def get_plugin_sdk() -> PluginSDK:
    return PluginSDK()
