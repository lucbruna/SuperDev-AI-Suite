"""Unit tests for services — pattern and interface verification."""

import pytest


class TestServicePatterns:
    """Verify all services follow the BaseService pattern."""

    def test_base_service_has_required_methods(self):
        from backend.services.base_service import BaseService

        required = ["get", "create", "update", "delete", "list", "count", "exists"]
        for method in required:
            assert hasattr(BaseService, method), f"Missing method: {method}"

    def test_user_service_interface(self):
        from backend.services.user_service import UserService

        required = [
            "get_user",
            "get_user_by_email",
            "get_user_by_username",
            "create_user",
            "update_user",
            "authenticate",
            "list_users",
            "search_users",
            "delete_user",
        ]
        for method in required:
            assert hasattr(UserService, method), f"Missing method: {method}"

    def test_project_service_interface(self):
        from backend.services.project_service import ProjectService

        required = [
            "get_project",
            "get_project_by_slug",
            "create_project",
            "update_project",
            "list_projects",
            "search_projects",
            "delete_project",
        ]
        for method in required:
            assert hasattr(ProjectService, method), f"Missing method: {method}"

    def test_workflow_service_interface(self):
        from backend.services.workflow_service import WorkflowService

        required = [
            "get_workflow",
            "create_workflow",
            "update_workflow",
            "list_workflows",
            "get_templates",
            "search_workflows",
            "delete_workflow",
            "create_run",
            "get_run",
            "list_runs",
        ]
        for method in required:
            assert hasattr(WorkflowService, method), f"Missing method: {method}"

    def test_agent_service_interface(self):
        from backend.services.agent_service import AgentService

        required = [
            "get_agent",
            "create_agent",
            "update_agent",
            "list_agents",
            "search_agents",
            "delete_agent",
            "execute_agent",
            "complete_execution",
            "list_executions",
            "get_execution_stats",
        ]
        for method in required:
            assert hasattr(AgentService, method), f"Missing method: {method}"

    def test_plugin_service_interface(self):
        from backend.services.plugin_service import PluginService

        required = [
            "get_plugin",
            "install_plugin",
            "update_plugin",
            "enable_plugin",
            "disable_plugin",
            "uninstall_plugin",
            "list_plugins",
            "get_enabled_plugins",
        ]
        for method in required:
            assert hasattr(PluginService, method), f"Missing method: {method}"

    def test_provider_service_interface(self):
        from backend.services.provider_service import ProviderService

        required = [
            "get_provider",
            "create_provider",
            "update_provider",
            "set_default",
            "list_providers",
            "get_active_providers",
            "get_provider_by_type",
            "delete_provider",
        ]
        for method in required:
            assert hasattr(ProviderService, method), f"Missing method: {method}"

    def test_knowledge_service_interface(self):
        from backend.services.knowledge_service import KnowledgeService

        required = [
            "get_knowledge_base",
            "create_knowledge_base",
            "update_knowledge_base",
            "list_knowledge_bases",
            "delete_knowledge_base",
            "get_entry",
            "create_entry",
            "update_entry",
            "list_entries",
            "search_entries",
            "delete_entry",
        ]
        for method in required:
            assert hasattr(KnowledgeService, method), f"Missing method: {method}"

    def test_notification_service_interface(self):
        from backend.services.notification_service import NotificationService

        required = [
            "get_notification",
            "create_notification",
            "list_notifications",
            "get_unread_count",
            "mark_read",
            "mark_all_read",
            "delete_notification",
        ]
        for method in required:
            assert hasattr(NotificationService, method), f"Missing method: {method}"

    def test_audit_service_interface(self):
        from backend.services.audit_service import AuditService

        required = [
            "log",
            "get_audit_log",
            "list_logs",
            "list_by_user",
            "list_by_action",
            "list_by_resource",
            "list_by_date_range",
        ]
        for method in required:
            assert hasattr(AuditService, method), f"Missing method: {method}"

    def test_organization_service_interface(self):
        from backend.services.organization_service import OrganizationService

        required = [
            "get_organization",
            "get_organization_by_slug",
            "create_organization",
            "update_organization",
            "list_organizations",
            "get_user_organizations",
            "delete_organization",
            "add_member",
            "remove_member",
            "list_members",
            "get_membership",
            "count_members",
            "update_member_role",
        ]
        for method in required:
            assert hasattr(OrganizationService, method), f"Missing method: {method}"
