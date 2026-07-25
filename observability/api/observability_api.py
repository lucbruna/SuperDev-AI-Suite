import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, HTTPException

from ..logging.log_manager import LogManager
from ..logging.structured_logger import StructuredLogger
from ..metrics.metrics_manager import MetricsManager
from ..tracing.tracing_manager import TracingManager
from ..monitoring.health import HealthMonitor
from ..alerts.alert_manager import AlertManager
from ..status.status_page import StatusPage
from ..status.incidents import IncidentManager
from ..audit.audit_manager import AuditManager

router = APIRouter(prefix="", tags=["observability"])


def _get_managers():
    from ..logging.log_manager import LogManager as _LM
    from ..metrics.metrics_manager import MetricsManager as _MM
    from ..tracing.tracing_manager import TracingManager as _TM
    from ..monitoring.health import HealthMonitor as _HM
    from ..alerts.alert_manager import AlertManager as _AM
    from ..status.status_page import StatusPage as _SP
    from ..status.incidents import IncidentManager as _IM
    from ..audit.audit_manager import AuditManager as _AUM

    class _Managers:
        log_manager = _LM()
        metrics_manager = _MM()
        tracing_manager = _TM()
        health_monitor = _HM()
        alert_manager = _AM()
        incident_manager = _IM()
        audit_manager = _AUM()
        status_page = _SP(_IM())

    return _Managers()


_managers = _get_managers()


@router.get("/health")
async def get_health() -> Dict[str, Any]:
    results = _managers.health_monitor.check_all()
    overall = "healthy"
    for r in results.values():
        if r.status == "unhealthy":
            overall = "unhealthy"
            break
        if r.status == "degraded":
            overall = "degraded"
    return {
        "status": overall,
        "services": {k: {"status": v.status, "latency_ms": v.latency_ms, "last_check": v.last_check} for k, v in results.items()},
        "timestamp": time.time(),
    }


@router.get("/metrics")
async def get_metrics() -> str:
    from ..metrics.prometheus_metrics import Counter, Gauge, Histogram
    all_metrics = _managers.metrics_manager.get_all()
    lines: list[str] = []
    for metric_type, items in all_metrics.items():
        for name, export_str in items.items():
            lines.append(export_str)
    return "\n".join(lines)


@router.get("/logs")
async def get_logs(
    level: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    logger = _managers.log_manager.get_logger("api")
    return [
        {
            "timestamp": time.time(),
            "level": level or "INFO",
            "logger": "api",
            "message": f"Log query: level={level}, limit={limit}, search={search}",
            "context": {},
        }
    ]


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str) -> Dict[str, Any]:
    trace = _managers.tracing_manager.get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace.to_dict()


@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    filters: Dict[str, Any] = {}
    if status:
        filters["status"] = status
    if severity:
        filters["severity"] = severity
    alerts = _managers.alert_manager.get_all(filters or None)
    return [
        {
            "id": a.id,
            "name": a.name,
            "severity": a.severity,
            "message": a.message,
            "status": a.status,
            "timestamp": a.timestamp,
            "acknowledged_at": a.acknowledged_at,
            "resolved_at": a.resolved_at,
        }
        for a in alerts
    ]


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
    alert = _managers.alert_manager.acknowledge(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"id": alert.id, "status": alert.status, "acknowledged_at": alert.acknowledged_at}


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    return _managers.status_page.generate()


@router.get("/audit")
async def get_audit(
    actor: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> List[Dict[str, Any]]:
    filters: Dict[str, Any] = {}
    if actor:
        filters["actor_id"] = actor
    if resource:
        filters["resource_type"] = resource
    if action:
        filters["action"] = action
    entries = _managers.audit_manager.query(filters or None)
    entries = entries[offset:offset + limit]
    return [
        {
            "id": e.id,
            "action": e.action,
            "actor_id": e.actor_id,
            "resource_type": e.resource_type,
            "resource_id": e.resource_id,
            "details": e.details,
            "timestamp": e.timestamp,
        }
        for e in entries
    ]
