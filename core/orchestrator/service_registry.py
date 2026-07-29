"""Service Registry — central register of all platform services.

Manages service registration, dependency resolution, lifecycle status
tracking, and health-report collection for every component running
in the SuperDev platform.
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timezone
from typing import Any

from .exceptions import (
    ServiceAlreadyRegisteredError,
    ServiceDependencyError,
    ServiceNotFoundError,
)
from .types import HealthReport, ServiceCategory, ServiceInfo, ServiceStatus, now_iso


class ServiceRegistry:
    """Central registry for all services in the platform.

    Each service is registered with metadata (name, category, version,
    dependencies) and its lifecycle status is tracked over time.
    """

    def __init__(self) -> None:
        self._services: dict[str, ServiceInfo] = {}
        self._health_reports: dict[str, list[HealthReport]] = {}
        self._start_order: list[str] = []

    # ─── Registration ─────────────────────────────────────────────────────

    def register(
        self,
        name: str,
        category: ServiceCategory,
        version: str = "1.0.0",
        description: str = "",
        dependencies: list[str] | None = None,
        health_endpoint: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ServiceInfo:
        """Register a new service. Raises if already registered."""
        if name in self._services:
            raise ServiceAlreadyRegisteredError(name)

        info = ServiceInfo(
            name=name,
            category=category,
            version=version,
            description=description,
            dependencies=dependencies or [],
            health_endpoint=health_endpoint,
            metadata=metadata or {},
            status=ServiceStatus.CREATED,
        )
        self._services[name] = info
        self._health_reports[name] = []
        return info

    def unregister(self, name: str) -> None:
        """Remove a service from the registry."""
        self._services.pop(name, None)
        self._health_reports.pop(name, None)

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered."""
        return name in self._services

    # ─── Status / Lifecycle ───────────────────────────────────────────────

    def set_status(self, name: str, status: ServiceStatus) -> None:
        """Update the lifecycle status of a registered service."""
        service = self._services.get(name)
        if service:
            service.status = status
            if status == ServiceStatus.RUNNING and not service.started_at:
                service.started_at = now_iso()

    def get_status(self, name: str) -> ServiceStatus:
        """Get the current status of a service."""
        service = self._services.get(name)
        return service.status if service else ServiceStatus.UNKNOWN

    def get_service(self, name: str) -> ServiceInfo:
        """Get service info. Raises if not found."""
        service = self._services.get(name)
        if not service:
            raise ServiceNotFoundError(name)
        return service

    # ─── Dependency Resolution ────────────────────────────────────────────

    def get_start_order(self) -> list[str]:
        """Resolve start order using topological sort on dependencies.

        Returns a list of service names ordered such that all dependencies
        of a service appear before the service itself.
        """
        visited: set[str] = set()
        result: list[str] = []
        temp: set[str] = set()

        def visit(name: str) -> None:
            if name in temp:
                return  # Cycle detected, skip
            if name in visited or name not in self._services:
                return
            temp.add(name)
            for dep in self._services[name].dependencies:
                visit(dep)
            temp.remove(name)
            visited.add(name)
            result.append(name)

        for service_name in self._services:
            visit(service_name)

        self._start_order = result
        return result

    def validate_dependencies(self, name: str) -> list[str]:
        """Check if all dependencies of a service are registered.

        Returns a list of missing dependency names (empty if all satisfied).
        """
        service = self._services.get(name)
        if not service:
            raise ServiceNotFoundError(name)
        missing = [dep for dep in service.dependencies if dep not in self._services]
        if missing:
            raise ServiceDependencyError(name, missing)
        return missing

    def get_dependents(self, name: str) -> list[str]:
        """Get all services that depend on the given service."""
        return [
            sname for sname, sinfo in self._services.items()
            if name in sinfo.dependencies
        ]

    # ─── Health ───────────────────────────────────────────────────────────

    def record_health(self, name: str, report: HealthReport) -> None:
        """Record a health check result for a service."""
        if name in self._health_reports:
            reports = self._health_reports[name]
            reports.append(report)
            if len(reports) > 100:
                reports.pop(0)

    def get_health_history(self, name: str, limit: int = 10) -> list[HealthReport]:
        """Get recent health reports for a service."""
        reports = self._health_reports.get(name, [])
        return reports[-limit:]

    def get_latest_health(self, name: str) -> HealthReport | None:
        """Get the most recent health report for a service."""
        reports = self._health_reports.get(name, [])
        return reports[-1] if reports else None

    # ─── Query ────────────────────────────────────────────────────────────

    def list_services(
        self,
        category: ServiceCategory | None = None,
        status: ServiceStatus | None = None,
    ) -> list[dict[str, Any]]:
        """List all registered services, optionally filtered."""
        result = []
        for name, info in self._services.items():
            if category and info.category != category:
                continue
            if status and info.status != status:
                continue
            result.append(self._to_dict(name, info))
        return result

    def count_by_category(self) -> dict[str, int]:
        """Count services grouped by category."""
        counts: dict[str, int] = {}
        for info in self._services.values():
            cat = info.category.name.lower()
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of all registered services."""
        by_status: dict[str, int] = {}
        for info in self._services.values():
            by_status[info.status.value] = by_status.get(info.status.value, 0) + 1
        return {
            "total_services": len(self._services),
            "by_category": self.count_by_category(),
            "by_status": by_status,
            "start_order": self._start_order,
        }

    def _to_dict(self, name: str, info: ServiceInfo) -> dict[str, Any]:
        """Convert service info to a serializable dict."""
        return {
            "name": name,
            "category": info.category.name.lower(),
            "version": info.version,
            "description": info.description,
            "status": info.status.value,
            "dependencies": info.dependencies,
            "dependents": self.get_dependents(name),
            "started_at": info.started_at,
            "error_count": info.error_count,
        }
