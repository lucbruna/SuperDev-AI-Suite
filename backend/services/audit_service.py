from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.audit_log import AuditLog
from backend.repositories.audit_repository import AuditLogRepository


class AuditService:
    """Service layer for AuditLog business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = AuditLogRepository(db)

    async def log(
        self,
        organization_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        user_id: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ) -> AuditLog:
        """Create an audit log entry."""
        return await self.repository.create(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_metadata=metadata or {},
        )

    async def get_audit_log(self, log_id: str) -> AuditLog:
        """Get an audit log entry by ID."""
        log = await self.repository.get_by_id(log_id)
        if not log:
            from backend.exceptions import AppException

            raise AppException(message="Audit log not found", code="AUDIT_LOG_NOT_FOUND", status_code=404)
        return log

    async def list_logs(
        self,
        organization_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for an organization."""
        return await self.repository.get_by_organization(organization_id, page, page_size)

    async def list_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for a specific user."""
        return await self.repository.get_by_user(user_id, page, page_size)

    async def list_by_action(
        self,
        action: str,
        organization_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs filtered by action type."""
        return await self.repository.get_by_action(action, organization_id, page, page_size)

    async def list_by_resource(
        self,
        resource_type: str,
        resource_id: str,
    ) -> list[AuditLog]:
        """Get all audit logs for a specific resource."""
        return await self.repository.get_by_resource(resource_type, resource_id)

    async def list_by_date_range(
        self,
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs within a date range."""
        return await self.repository.get_by_date_range(organization_id, start_date, end_date, page, page_size)
