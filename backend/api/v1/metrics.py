"""Prometheus-compatible metrics endpoint.

Exposes /metrics in Prometheus text exposition format so that
Prometheus, Grafana, Datadog, etc. can scrape application metrics.
"""

from __future__ import annotations

from fastapi import APIRouter, Response

from backend.observability.metrics import get_metrics_collector

router = APIRouter(tags=["metrics"])


def _prometheus_text(collector) -> str:
    """Render collector state as Prometheus text exposition format."""
    lines: list[str] = []
    metrics = collector.get_metrics()
    uptime = metrics.get("uptime_seconds", 0)
    total_requests = metrics.get("total_requests", 0)
    total_errors = metrics.get("total_errors", 0)
    error_rate = metrics.get("error_rate_pct", 0)

    # Uptime
    lines.append("# HELP superdev_uptime_seconds Application uptime in seconds.")
    lines.append("# TYPE superdev_uptime_seconds gauge")
    lines.append(f"superdev_uptime_seconds {uptime}")

    # Total requests
    lines.append("# HELP superdev_http_requests_total Total HTTP requests.")
    lines.append("# TYPE superdev_http_requests_total counter")
    lines.append(f"superdev_http_requests_total {total_requests}")

    # Total errors
    lines.append("# HELP superdev_http_errors_total Total HTTP errors (4xx+5xx).")
    lines.append("# TYPE superdev_http_errors_total counter")
    lines.append(f"superdev_http_errors_total {total_errors}")

    # Error rate
    lines.append("# HELP superdev_error_rate_percent Current error rate percentage.")
    lines.append("# TYPE superdev_error_rate_percent gauge")
    lines.append(f"superdev_error_rate_percent {error_rate}")

    # Per-endpoint request counts
    lines.append("# HELP superdev_endpoint_requests_total Requests per endpoint.")
    lines.append("# TYPE superdev_endpoint_requests_total counter")
    for endpoint, count in metrics.get("requests_by_endpoint", {}).items():
        method, path = endpoint.split(" ", 1) if " " in endpoint else ("unknown", endpoint)
        lines.append(f'superdev_endpoint_requests_total{{method="{method}",path="{path}"}} {count}')

    # Per-endpoint durations
    lines.append("# HELP superdev_endpoint_duration_ms Average endpoint duration.")
    lines.append("# TYPE superdev_endpoint_duration_ms gauge")
    for endpoint, dur in metrics.get("durations", {}).items():
        method, path = endpoint.split(" ", 1) if " " in endpoint else ("unknown", endpoint)
        lines.append(f'superdev_endpoint_duration_ms{{method="{method}",path="{path}"}} {dur["avg_ms"]}')

    # Per-endpoint error counts
    lines.append("# HELP superdev_endpoint_errors_total Errors per endpoint+status.")
    lines.append("# TYPE superdev_endpoint_errors_total counter")
    for key, count in metrics.get("errors", {}).items():
        parts = key.rsplit(" ", 1)
        if len(parts) == 2 and parts[1].isdigit():
            endpoint, status = parts
            method, path = endpoint.split(" ", 1) if " " in endpoint else ("unknown", endpoint)
            lines.append(f'superdev_endpoint_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}')
        else:
            lines.append(f'superdev_endpoint_errors_total{{error="{key}"}} {count}')

    # Custom counters
    lines.append("# HELP superdev_custom_counters Custom application counters.")
    lines.append("# TYPE superdev_custom_counters counter")
    for name, count in metrics.get("custom_counters", {}).items():
        lines.append(f'superdev_custom_counters{{name="{name}"}} {count}')

    # Process info
    lines.append("# HELP superdev_info Application metadata.")
    lines.append("# TYPE superdev_info gauge")
    lines.append('superdev_info{version="6.0.0",name="SuperDev"} 1')

    lines.append("")
    return "\n".join(lines)


@router.get("/metrics", include_in_schema=False)
async def prometheus_metrics() -> Response:
    """Return application metrics in Prometheus text exposition format."""
    collector = get_metrics_collector()
    body = _prometheus_text(collector)
    return Response(content=body, media_type="text/plain; version=0.0.4; charset=utf-8")


@router.get("/metrics/json")
async def metrics_json() -> dict:
    """Return metrics as JSON (for dashboards that prefer JSON over Prometheus format)."""
    collector = get_metrics_collector()
    return {"success": True, "data": collector.get_metrics()}
