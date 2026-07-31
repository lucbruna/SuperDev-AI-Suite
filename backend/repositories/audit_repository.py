from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.audit_log import AuditLog
from backend.repositories.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for AuditLog entity with domain-specific queries."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, AuditLog)

    async def get_by_organization(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for an organization, newest first."""
        base_query = select(self.model).where(self.model.organization_id == org_id)
        count_query = select(func.count()).select_from(self.model).where(self.model.organization_id == org_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = base_query.order_by(self.model.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs for a specific user, newest first."""
        base_query = select(self.model).where(self.model.user_id == user_id)
        count_query = select(func.count()).select_from(self.model).where(self.model.user_id == user_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = base_query.order_by(self.model.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_resource(self, resource_type: str, resource_id: str) -> list[AuditLog]:
        """Get all audit logs for a specific resource."""
        query = (
            select(self.model)
            .where(
                self.model.resource_type == resource_type,
                self.model.resource_id == resource_id,
            )
            .order_by(self.model.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_action(
        self,
        action: str,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs with a specific action for an organization."""
        base_query = select(self.model).where(
            self.model.organization_id == org_id,
            self.model.action == action,
        )
        count_query = (
            select(func.count())
            .select_from(self.model)
            .where(
                self.model.organization_id == org_id,
                self.model.action == action,
            )
        )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = base_query.order_by(self.model.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_date_range(
        self,
        org_id: str,
        start_date: datetime,
        end_date: datetime,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs within a date range for an organization."""
        where_clause = (
            self.model.organization_id == org_id,
            self.model.created_at >= start_date,
            self.model.created_at <= end_date,
        )
        base_query = select(self.model).where(*where_clause)
        count_query = select(func.count()).select_from(self.model).where(*where_clause)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        offset = (page - 1) * page_size
        query = base_query.order_by(self.model.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total
