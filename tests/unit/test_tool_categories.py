"""Tests for all AI tool categories."""

from __future__ import annotations

import pytest
from typing import Any

from ai.tools.github.github_tool import GitHubTool
from ai.tools.github.repository import GitHubRepository
from ai.tools.github.issues import GitHubIssues
from ai.tools.github.pull_requests import GitHubPullRequests
from ai.tools.github.actions import GitHubActions
from ai.tools.github.releases import GitHubReleases

from ai.tools.docker.docker_tool import DockerTool
from ai.tools.docker.container import DockerContainer
from ai.tools.docker.image import DockerImage
from ai.tools.docker.volume import DockerVolume
from ai.tools.docker.network import DockerNetwork
from ai.tools.docker.compose import DockerCompose

from ai.tools.kubernetes.kubernetes_tool import KubernetesTool
from ai.tools.kubernetes.pod import KubernetesPod
from ai.tools.kubernetes.service import KubernetesService
from ai.tools.kubernetes.deployment import KubernetesDeployment
from ai.tools.kubernetes.namespace import KubernetesNamespace
from ai.tools.kubernetes.configmap import KubernetesConfigMap

from ai.tools.browser.browser_tool import BrowserTool
from ai.tools.browser.page import BrowserPage
from ai.tools.browser.navigation import BrowserNavigation
from ai.tools.browser.form import BrowserForm
from ai.tools.browser.screenshot import BrowserScreenshot
from ai.tools.browser.cookies import BrowserCookies

from ai.tools.database.database_tool import DatabaseTool
from ai.tools.database.connection import DatabaseConnection
from ai.tools.database.query import DatabaseQuery
from ai.tools.database.migration import DatabaseMigration
from ai.tools.database.schema import DatabaseSchema
from ai.tools.database.backup import DatabaseBackup

from ai.tools.api.api_tool import ApiTool
from ai.tools.api.client import ApiClient
from ai.tools.api.request import ApiRequest
from ai.tools.api.response import ApiResponse
from ai.tools.api.auth import ApiAuth
from ai.tools.api.webhook import ApiWebhook

from ai.tools.llm.llm_tool import LlmTool
from ai.tools.llm.completion import LlmCompletion
from ai.tools.llm.chat import LlmChat
from ai.tools.llm.embedding import LlmEmbedding
from ai.tools.llm.tokenizer import LlmTokenizer
from ai.tools.llm.model import LlmModel

from ai.tools.rag.rag_tool import RagTool
from ai.tools.rag.document import RagDocument
from ai.tools.rag.chunk import RagChunk
from ai.tools.rag.vector_store import RagVectorStore
from ai.tools.rag.retriever import RagRetriever
from ai.tools.rag.index import RagIndex


# ---------------------------------------------------------------------------
# GitHub Tool Tests
# ---------------------------------------------------------------------------

class TestGitHubTool:
    """Tests for the GitHub tool category."""

    @pytest.fixture
    def tool(self):
        return GitHubTool()

    async def test_name(self, tool):
        assert tool.name() == "github"

    async def test_description(self, tool):
        assert "GitHub" in tool.description()

    async def test_permissions(self, tool):
        perms = tool.permissions()
        assert "read" in perms
        assert "write" in perms

    async def test_validate(self, tool):
        assert await tool.validate({"action": "list"})
        assert not await tool.validate({})

    async def test_repository_list(self, tool):
        result = await tool.execute({"action": "list"})
        assert result["success"] is True
        assert "repositories" in result

    async def test_repository_create_and_delete(self, tool):
        create = await tool.execute({"action": "create", "name": "test-repo"})
        assert create["success"] is True

        delete = await tool.execute({"action": "delete", "name": "test-repo"})
        assert delete["success"] is True

    async def test_issues_create_and_list(self, tool):
        result = await tool.execute({"action": "create", "title": "Bug report", "sub_tool": "issues"})
        assert result["success"] is True

    async def test_rollback(self, tool):
        await tool.rollback()  # should not raise

    async def test_cleanup(self, tool):
        await tool.cleanup()  # should not raise


class TestGitHubSubTools:
    """Tests for individual GitHub sub-tools."""

    async def test_repository_actions(self):
        repo = GitHubRepository()
        result = await repo.execute({"action": "search", "query": "test"})
        assert result["success"] is True

    async def test_issues_actions(self):
        issues = GitHubIssues()
        result = await issues.execute({"action": "list"})
        assert result["success"] is True
        assert "issues" in result

    async def test_pull_requests_actions(self):
        prs = GitHubPullRequests()
        result = await prs.execute({"action": "list"})
        assert result["success"] is True

    async def test_actions_actions(self):
        actions = GitHubActions()
        result = await actions.execute({"action": "list_workflows"})
        assert result["success"] is True

    async def test_releases_actions(self):
        releases = GitHubReleases()
        result = await releases.execute({"action": "create", "tag": "v1.0", "name": "v1.0"})
        assert result["success"] is True


# ---------------------------------------------------------------------------
# Docker Tool Tests
# ---------------------------------------------------------------------------

class TestDockerTool:
    """Tests for the Docker tool category."""

    @pytest.fixture
    def tool(self):
        return DockerTool()

    async def test_name(self, tool):
        assert tool.name() == "docker"

    async def test_containers_list(self, tool):
        result = await tool.execute({"action": "list", "sub_tool": "container"})
        assert result["success"] is True

    async def test_images_pull(self, tool):
        result = await tool.execute({"action": "pull", "name": "nginx", "sub_tool": "image"})
        assert result["success"] is True

    async def test_compose_up(self, tool):
        result = await tool.execute({"action": "up", "sub_tool": "compose"})
        assert result["success"] is True

    async def test_unknown_action(self, tool):
        result = await tool.execute({"action": "nonexistent"})
        assert result["success"] is False


class TestDockerSubTools:
    async def test_container(self):
        c = DockerContainer()
        r = await c.execute({"action": "start", "container_id": "abc"})
        assert r["success"] is True

    async def test_image(self):
        i = DockerImage()
        r = await i.execute({"action": "list"})
        assert r["success"] is True

    async def test_volume(self):
        v = DockerVolume()
        r = await v.execute({"action": "create", "name": "data"})
        assert r["success"] is True

    async def test_network(self):
        n = DockerNetwork()
        r = await n.execute({"action": "list"})
        assert r["success"] is True

    async def test_compose(self):
        c = DockerCompose()
        r = await c.execute({"action": "ps"})
        assert r["success"] is True

    async def test_rollback_cleanup(self):
        c = DockerContainer()
        await c.execute({"action": "start", "container_id": "x"})
        await c.rollback()
        await c.cleanup()


# ---------------------------------------------------------------------------
# Kubernetes Tool Tests
# ---------------------------------------------------------------------------

class TestKubernetesTool:
    @pytest.fixture
    def tool(self):
        return KubernetesTool()

    async def test_name(self, tool):
        assert tool.name() == "kubernetes"

    async def test_pod_list(self, tool):
        r = await tool.execute({"action": "list", "sub_tool": "pod"})
        assert r["success"] is True

    async def test_deployment_create(self, tool):
        r = await tool.execute({"action": "create", "name": "web", "sub_tool": "deployment"})
        assert r["success"] is True


class TestKubernetesSubTools:
    async def test_pod(self):
        p = KubernetesPod()
        r = await p.execute({"action": "logs", "name": "pod-1"})
        assert r["success"] is True

    async def test_service(self):
        s = KubernetesService()
        r = await s.execute({"action": "create", "name": "web-svc", "port": 80})
        assert r["success"] is True

    async def test_deployment(self):
        d = KubernetesDeployment()
        create = await d.execute({"action": "create", "name": "web", "image": "nginx:latest"})
        assert create["success"] is True
        scale = await d.execute({"action": "scale", "name": "web", "replicas": 3})
        assert scale["success"] is True
        assert scale["replicas"] == 3

    async def test_namespace(self):
        n = KubernetesNamespace()
        r = await n.execute({"action": "list"})
        assert r["success"] is True

    async def test_configmap(self):
        c = KubernetesConfigMap()
        r = await c.execute({"action": "create", "name": "app-config", "data": {"key": "val"}})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# Browser Tool Tests
# ---------------------------------------------------------------------------

class TestBrowserTool:
    @pytest.fixture
    def tool(self):
        return BrowserTool()

    async def test_name(self, tool):
        assert tool.name() == "browser"

    async def test_page_open(self, tool):
        r = await tool.execute({"action": "open", "url": "https://example.com", "sub_tool": "page"})
        assert r["success"] is True

    async def test_screenshot(self, tool):
        r = await tool.execute({"action": "capture", "sub_tool": "screenshot"})
        assert r["success"] is True

    async def test_form_fill(self, tool):
        r = await tool.execute({"action": "fill", "selector": "#name", "value": "test", "sub_tool": "form"})
        assert r["success"] is True


class TestBrowserSubTools:
    async def test_page(self):
        p = BrowserPage()
        await p.execute({"action": "open", "url": "https://test.com"})
        r = await p.execute({"action": "get_title"})
        assert r["success"] is True

    async def test_navigation(self):
        n = BrowserNavigation()
        r = await n.execute({"action": "click", "selector": "#btn"})
        assert r["success"] is True

    async def test_cookies(self):
        c = BrowserCookies()
        await c.execute({"action": "set", "name": "session", "value": "abc123"})
        r = await c.execute({"action": "list"})
        assert r["success"] is True

    async def test_screenshot(self):
        s = BrowserScreenshot()
        r = await s.execute({"action": "capture_full_page"})
        assert r["success"] is True

    async def test_form(self):
        f = BrowserForm()
        r = await f.execute({"action": "submit", "selector": "#form"})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# Database Tool Tests
# ---------------------------------------------------------------------------

class TestDatabaseTool:
    @pytest.fixture
    def tool(self):
        return DatabaseTool()

    async def test_name(self, tool):
        assert tool.name() == "database"

    async def test_connection_flow(self, tool):
        r = await tool.execute({"action": "connect", "sub_tool": "connection", "host": "localhost"})
        assert r["success"] is True

    async def test_query(self, tool):
        r = await tool.execute({"action": "select", "sub_tool": "query", "query": "SELECT 1"})
        assert r["success"] is True


class TestDatabaseSubTools:
    async def test_connection(self):
        c = DatabaseConnection()
        await c.execute({"action": "connect"})
        r = await c.execute({"action": "ping"})
        assert r["success"] is True

    async def test_query(self):
        q = DatabaseQuery()
        r = await q.execute({"action": "execute_raw", "query": "SELECT 1"})
        assert r["success"] is True

    async def test_migration(self):
        m = DatabaseMigration()
        r = await m.execute({"action": "create", "name": "add_users"})
        assert r["success"] is True

    async def test_schema(self):
        s = DatabaseSchema()
        r = await s.execute({"action": "list"})
        assert r["success"] is True

    async def test_backup(self):
        b = DatabaseBackup()
        r = await b.execute({"action": "create", "database": "mydb"})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# API Tool Tests
# ---------------------------------------------------------------------------

class TestApiTool:
    @pytest.fixture
    def tool(self):
        return ApiTool()

    async def test_name(self, tool):
        assert tool.name() == "api"

    async def test_request_get(self, tool):
        r = await tool.execute({"action": "get", "url": "https://api.example.com/data", "sub_tool": "request"})
        assert r["success"] is True

    async def test_auth(self, tool):
        r = await tool.execute({"action": "bearer", "sub_tool": "auth"})
        assert r["success"] is True


class TestApiSubTools:
    async def test_client(self):
        c = ApiClient()
        r = await c.execute({"action": "create", "base_url": "https://api.example.com"})
        assert r["success"] is True

    async def test_request(self):
        r = ApiRequest()
        result = await r.execute({"action": "post", "url": "https://api.example.com/data", "body": {"key": "val"}})
        assert result["success"] is True

    async def test_response(self):
        r = ApiResponse()
        result = await r.execute({"action": "parse", "data": {"foo": "bar"}})
        assert result["success"] is True

    async def test_auth(self):
        a = ApiAuth()
        r = await a.execute({"action": "oauth", "client_id": "abc"})
        assert r["success"] is True

    async def test_webhook(self):
        w = ApiWebhook()
        r = await w.execute({"action": "register", "url": "https://hooks.example.com", "events": ["push"]})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# LLM Tool Tests
# ---------------------------------------------------------------------------

class TestLlmTool:
    @pytest.fixture
    def tool(self):
        return LlmTool()

    async def test_name(self, tool):
        assert tool.name() == "llm"

    async def test_completion(self, tool):
        r = await tool.execute({"action": "complete", "prompt": "Hello", "sub_tool": "completion"})
        assert r["success"] is True

    async def test_chat(self, tool):
        r = await tool.execute({"action": "send", "message": "Hi!", "sub_tool": "chat"})
        assert r["success"] is True


class TestLlmSubTools:
    async def test_completion(self):
        c = LlmCompletion()
        r = await c.execute({"action": "complete", "prompt": "Hello world"})
        assert r["success"] is True

    async def test_chat(self):
        c = LlmChat()
        r = await c.execute({"action": "send", "message": "Hello"})
        assert r["success"] is True

    async def test_embedding(self):
        e = LlmEmbedding()
        r = await e.execute({"action": "embed", "texts": ["hello world"]})
        assert r["success"] is True

    async def test_tokenizer(self):
        t = LlmTokenizer()
        r = await t.execute({"action": "count", "text": "Hello world"})
        assert r["success"] is True

    async def test_model(self):
        m = LlmModel()
        r = await m.execute({"action": "list"})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# RAG Tool Tests
# ---------------------------------------------------------------------------

class TestRagTool:
    @pytest.fixture
    def tool(self):
        return RagTool()

    async def test_name(self, tool):
        assert tool.name() == "rag"

    async def test_document_add(self, tool):
        r = await tool.execute({"action": "add", "title": "doc1", "content": "text", "sub_tool": "document"})
        assert r["success"] is True

    async def test_retrieve(self, tool):
        r = await tool.execute({"action": "retrieve", "query": "test", "sub_tool": "retriever"})
        assert r["success"] is True


class TestRagSubTools:
    async def test_document(self):
        d = RagDocument()
        r = await d.execute({"action": "add", "title": "Test", "content": "Hello world"})
        assert r["success"] is True

    async def test_chunk(self):
        c = RagChunk()
        r = await c.execute({"action": "split", "content": "A" * 1000, "chunk_size": 200})
        assert r["success"] is True

    async def test_vector_store(self):
        v = RagVectorStore()
        r = await v.execute({"action": "create", "store_name": "my_store", "dimension": 128})
        assert r["success"] is True

    async def test_retriever(self):
        r = RagRetriever()
        result = await r.execute({"action": "retrieve", "query": "test query"})
        assert result["success"] is True
        assert "results" in result

    async def test_index(self):
        idx = RagIndex()
        r = await idx.execute({"action": "create", "index_name": "my_index"})
        assert r["success"] is True


# ---------------------------------------------------------------------------
# Interface Tests
# ---------------------------------------------------------------------------

class TestInterfaces:
    """Verify all composite tools implement the BaseTool interface correctly."""

    @pytest.fixture(params=[
        GitHubTool, DockerTool, KubernetesTool,
        BrowserTool, DatabaseTool, ApiTool,
        LlmTool, RagTool,
    ])
    def composite_tool(self, request):
        return request.param()

    async def test_all_tools_have_name(self, composite_tool):
        name = composite_tool.name()
        assert isinstance(name, str)
        assert len(name) > 0

    async def test_all_tools_have_description(self, composite_tool):
        desc = composite_tool.description()
        assert isinstance(desc, str)
        assert len(desc) > 0

    async def test_all_tools_have_permissions(self, composite_tool):
        perms = composite_tool.permissions()
        assert isinstance(perms, list)

    async def test_all_tools_validate_with_action(self, composite_tool):
        assert await composite_tool.validate({"action": "test"})

    async def test_all_tools_reject_empty_params(self, composite_tool):
        assert not await composite_tool.validate({})
