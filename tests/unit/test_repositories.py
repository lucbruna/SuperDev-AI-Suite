"""Unit tests for repositories.base_repository pattern."""

import pytest


class TestBaseRepositoryPattern:
    """Tests to verify BaseRepository API contract."""

    def test_base_repository_has_required_methods(self):
        from backend.repositories.base_repository import BaseRepository

        required_methods = [
            "get_by_id",
            "create",
            "update",
            "delete",
            "list",
            "count",
            "exists",
        ]
        for method in required_methods:
            assert hasattr(BaseRepository, method), f"Missing method: {method}"

    def test_user_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.user_repository import UserRepository

        assert issubclass(UserRepository, BaseRepository)

    def test_project_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.project_repository import ProjectRepository

        assert issubclass(ProjectRepository, BaseRepository)

    def test_workflow_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.workflow_repository import WorkflowRepository

        assert issubclass(WorkflowRepository, BaseRepository)

    def test_agent_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.agent_repository import AgentRepository

        assert issubclass(AgentRepository, BaseRepository)

    def test_plugin_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.plugin_repository import PluginRepository

        assert issubclass(PluginRepository, BaseRepository)

    def test_provider_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.provider_repository import ProviderRepository

        assert issubclass(ProviderRepository, BaseRepository)

    def test_knowledge_base_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.knowledge_repository import KnowledgeBaseRepository

        assert issubclass(KnowledgeBaseRepository, BaseRepository)

    def test_notification_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.notification_repository import NotificationRepository

        assert issubclass(NotificationRepository, BaseRepository)

    def test_audit_log_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.audit_repository import AuditLogRepository

        assert issubclass(AuditLogRepository, BaseRepository)

    def test_organization_repository_extends_base(self):
        from backend.repositories.base_repository import BaseRepository
        from backend.repositories.organization_repository import OrganizationRepository

        assert issubclass(OrganizationRepository, BaseRepository)
