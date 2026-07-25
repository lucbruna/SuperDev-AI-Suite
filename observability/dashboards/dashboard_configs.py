from typing import Any, Dict, List

DEFAULT_DASHBOARDS: Dict[str, Dict[str, Any]] = {
    "system_overview": {
        "title": "System Overview",
        "panels": [
            {
                "title": "CPU Usage",
                "metric": "cpu_percent",
                "chart_type": "line",
                "refresh_interval": 10,
            },
            {
                "title": "Memory Usage",
                "metric": "memory_percent",
                "chart_type": "line",
                "refresh_interval": 10,
            },
            {
                "title": "Disk Usage",
                "metric": "disk_percent",
                "chart_type": "gauge",
                "refresh_interval": 30,
            },
            {
                "title": "Network I/O",
                "metric": "network_bytes",
                "chart_type": "area",
                "refresh_interval": 15,
            },
            {
                "title": "Uptime",
                "metric": "uptime_seconds",
                "chart_type": "stat",
                "refresh_interval": 60,
            },
        ],
    },
    "api_performance": {
        "title": "API Performance",
        "panels": [
            {
                "title": "Request Rate",
                "metric": "requests_per_second",
                "chart_type": "line",
                "refresh_interval": 10,
            },
            {
                "title": "Latency (p95)",
                "metric": "latency_p95_ms",
                "chart_type": "line",
                "refresh_interval": 10,
            },
            {
                "title": "Error Rate",
                "metric": "error_rate_percent",
                "chart_type": "line",
                "refresh_interval": 10,
            },
        ],
    },
    "agent_metrics": {
        "title": "Agent Metrics",
        "panels": [
            {
                "title": "Executions",
                "metric": "agent_executions_total",
                "chart_type": "bar",
                "refresh_interval": 15,
            },
            {
                "title": "Success Rate",
                "metric": "agent_success_rate",
                "chart_type": "gauge",
                "refresh_interval": 15,
            },
            {
                "title": "Avg Duration",
                "metric": "agent_avg_duration_ms",
                "chart_type": "line",
                "refresh_interval": 15,
            },
        ],
    },
}


def get_dashboard(name: str) -> Dict[str, Any]:
    return DEFAULT_DASHBOARDS[name]


def list_dashboards() -> List[str]:
    return list(DEFAULT_DASHBOARDS.keys())


def get_all_dashboards() -> Dict[str, Dict[str, Any]]:
    return DEFAULT_DASHBOARDS
