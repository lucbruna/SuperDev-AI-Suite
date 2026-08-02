"""Unit tests for Pydantic schemas validation."""

import pytest
from pydantic import ValidationError

from backend.schemas.auth import (
    LoginRequest,
    MFAVerifyRequest,
    RegisterRequest,
    RefreshRequest,
)
from backend.schemas.user import UserCreate, UserUpdate
from backend.schemas.project import ProjectCreate, ProjectUpdate
from backend.schemas.workflow import WorkflowCreate, WorkflowUpdate
from backend.schemas.agent import AgentCreate, AgentUpdate, AgentExecuteRequest
from backend.schemas.plugin import PluginCreate
from backend.schemas.provider import ProviderCreate
from backend.schemas.knowledge import KnowledgeBaseCreate, KnowledgeEntryCreate
from backend.schemas.organization import OrganizationCreate, OrganizationMemberInvite
from backend.schemas.role import RoleCreate, UserRoleAssign


# ── Auth Schemas ─────────────────────────────────────────────────


class TestLoginRequest:
    def test_valid_login(self):
        req = LoginRequest(email="user@example.com", password="password123")
        assert req.email == "user@example.com"

    def test_email_normalized(self):
        req = LoginRequest(email="USER@EXAMPLE.COM", password="password123")
        assert req.email == "user@example.com"

    def test_invalid_email_no_at(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="invalid-email", password="password123")

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            LoginRequest(email="user@example.com", password="short")


class TestRegisterRequest:
    def test_valid_register(self):
        req = RegisterRequest(
            email="new@example.com",
            password="password123",
            username="newuser",
        )
        assert req.username == "newuser"

    def test_invalid_username_special_chars(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="new@example.com",
                password="password123",
                username="invalid user!",
            )

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="new@example.com",
                password="password123",
                username="ab",
            )

    def test_valid_username_with_underscores(self):
        req = RegisterRequest(
            email="new@example.com",
            password="password123",
            username="valid_user-123",
        )
        assert req.username == "valid_user-123"


class TestMFAVerifyRequest:
    def test_valid_code(self):
        req = MFAVerifyRequest(code="123456")
        assert req.code == "123456"

    def test_code_too_short(self):
        with pytest.raises(ValidationError):
            MFAVerifyRequest(code="12345")

    def test_code_too_long(self):
        with pytest.raises(ValidationError):
            MFAVerifyRequest(code="1234567")


class TestRefreshRequest:
    def test_valid_refresh(self):
        req = RefreshRequest(refresh_token="some.valid.token")
        assert req.refresh_token == "some.valid.token"

    def test_empty_refresh(self):
        with pytest.raises(ValidationError):
            RefreshRequest(refresh_token="")


# ── User Schemas ─────────────────────────────────────────────────


class TestUserCreate:
    def test_valid_user_create(self):
        user = UserCreate(
            email="test@example.com",
            password="password123",
            username="testuser",
        )
        assert user.email == "test@example.com"
        assert user.username == "testuser"

    def test_optional_full_name(self):
        user = UserCreate(
            email="test@example.com",
            password="password123",
            username="testuser",
            full_name="Test User",
        )
        assert user.full_name == "Test User"

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="short",
                username="testuser",
            )


class TestUserUpdate:
    def test_empty_update(self):
        update = UserUpdate()
        assert update.email is None
        assert update.username is None

    def test_partial_update(self):
        update = UserUpdate(email="new@example.com")
        assert update.email == "new@example.com"
        assert update.username is None


# ── Project Schemas ──────────────────────────────────────────────


class TestProjectCreate:
    def test_valid_project(self):
        project = ProjectCreate(
            organization_id="org-123",
            name="My Project",
            slug="my-project",
        )
        assert project.name == "My Project"
        assert project.visibility == "private"

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            ProjectCreate(
                organization_id="org-123",
                name="",
                slug="my-project",
            )


class TestProjectUpdate:
    def test_partial_update(self):
        update = ProjectUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.visibility is None


# ── Workflow Schemas ─────────────────────────────────────────────


class TestWorkflowCreate:
    def test_valid_workflow(self):
        wf = WorkflowCreate(
            project_id="proj-123",
            name="CI Pipeline",
            definition={"nodes": [{"id": "step1", "type": "action"}]},
        )
        assert wf.name == "CI Pipeline"
        assert wf.is_template is False

    def test_empty_definition_not_validated_at_schema_level(self):
        """Empty dict passes Pydantic validation — business validation happens in service layer."""
        wf = WorkflowCreate(
            project_id="proj-123",
            name="CI Pipeline",
            definition={},
        )
        assert wf.definition == {}

    def test_valid_definition_with_nodes(self):
        wf = WorkflowCreate(
            project_id="proj-123",
            name="CI Pipeline",
            definition={"nodes": [{"id": "s1", "type": "action"}], "edges": []},
        )
        assert len(wf.definition["nodes"]) == 1


class TestAgentSchemas:
    def test_agent_create(self):
        agent = AgentCreate(
            name="Code Reviewer",
            agent_type="reviewer",
        )
        assert agent.agent_type == "reviewer"
        assert agent.tools_enabled is None

    def test_agent_execute_request(self):
        req = AgentExecuteRequest(task="Review this PR")
        assert req.task == "Review this PR"
        assert req.context == {}

    def test_agent_execute_empty_task(self):
        with pytest.raises(ValidationError):
            AgentExecuteRequest(task="")


# ── Plugin Schemas ───────────────────────────────────────────────


class TestPluginCreate:
    def test_valid_plugin(self):
        plugin = PluginCreate(
            project_id="proj-123",
            slug="github-integration",
            name="GitHub Integration",
            version="1.0.0",
            manifest={"name": "GitHub", "version": "1.0.0"},
        )
        assert plugin.version == "1.0.0"


# ── Provider Schemas ─────────────────────────────────────────────


class TestProviderCreate:
    def test_valid_provider(self):
        provider = ProviderCreate(
            project_id="proj-123",
            name="OpenAI",
            type="openai",
            config={"api_key": "sk-xxx"},
            models=["gpt-4", "gpt-3.5-turbo"],
        )
        assert provider.type == "openai"
        assert len(provider.models) == 2


# ── Knowledge Schemas ────────────────────────────────────────────


class TestKnowledgeBaseCreate:
    def test_valid_kb(self):
        kb = KnowledgeBaseCreate(
            project_id="proj-123",
            name="Documentation",
        )
        assert kb.type == "documentation"
        assert kb.chunk_size == 1000

    def test_invalid_chunk_size(self):
        with pytest.raises(ValidationError):
            KnowledgeBaseCreate(
                project_id="proj-123",
                name="Doc",
                chunk_size=10,  # Below minimum of 100
            )


class TestKnowledgeEntryCreate:
    def test_valid_entry(self):
        entry = KnowledgeEntryCreate(
            knowledge_base_id="kb-123",
            title="Getting Started",
            content="Welcome to the platform...",
        )
        assert entry.title == "Getting Started"


# ── Organization Schemas ─────────────────────────────────────────


class TestOrganizationCreate:
    def test_valid_org(self):
        org = OrganizationCreate(name="Acme Inc", slug="acme")
        assert org.plan == "free"

    def test_empty_name(self):
        with pytest.raises(ValidationError):
            OrganizationCreate(name="", slug="acme")


class TestOrganizationMemberInvite:
    def test_valid_invite(self):
        invite = OrganizationMemberInvite(email="user@example.com")
        assert invite.role == "member"


# ── Role Schemas ─────────────────────────────────────────────────


class TestRoleCreate:
    def test_valid_role(self):
        role = RoleCreate(name="admin", description="Admin role")
        assert role.permission_ids == []


class TestUserRoleAssign:
    def test_valid_assignment(self):
        assign = UserRoleAssign(user_id="u-1", role_id="r-1")
        assert assign.organization_id is None
        assert assign.project_id is None
