"""Reporting subsystem generator."""
import os
BASE = r'C:\Users\tomga\OneDrive\Desktop\super_dev_suite\SuperDev\ai\observability\reporting'

def w(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(content)

w('report_engine.py', '''"""Report engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class ReportEngine:
    def __init__(self) -> None:
        self._reports: Dict[str, Dict[str, Any]] = {}
        self._generated: List[Dict[str, Any]] = []
    def generate(self, report_type: str, data: Dict[str, Any], title: str = "") -> Dict[str, Any]:
        import uuid
        report_id = str(uuid.uuid4())[:8]
        report = {"id": report_id, "type": report_type, "title": title or f"{report_type} Report", "data": data, "created_at": time.time(), "status": "completed"}
        self._reports[report_id] = report
        self._generated.append({"id": report_id, "type": report_type, "timestamp": time.time()})
        return report
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        return self._reports.get(report_id)
    def list_reports(self, report_type: str = "") -> List[Dict[str, Any]]:
        reports = list(self._reports.values())
        if report_type:
            reports = [r for r in reports if r["type"] == report_type]
        return reports
    def export_json(self, report_id: str) -> str:
        import json
        report = self._reports.get(report_id)
        if report:
            return json.dumps(report, indent=2)
        return "{}"
    def export_csv(self, report_id: str) -> str:
        report = self._reports.get(report_id)
        if not report:
            return ""
        lines = ["key,value"]
        for k, v in report.get("data", {}).items():
            lines.append(f"{k},{v}")
        return "\\n".join(lines)
    def delete_report(self, report_id: str) -> bool:
        if report_id in self._reports:
            del self._reports[report_id]
            return True
        return False
''')

w('uptime_report.py', '''"""Uptime report."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class UptimeReport:
    def __init__(self) -> None:
        self._checks: Dict[str, List[Dict[str, Any]]] = {}
    def record_check(self, service: str, status: str) -> None:
        self._checks.setdefault(service, []).append({"status": status, "timestamp": time.time()})
    def get_uptime(self, service: str) -> float:
        checks = self._checks.get(service, [])
        if not checks:
            return 0.0
        total = len(checks)
        up = sum(1 for c in checks if c["status"] == "healthy")
        return (up / total) * 100
    def get_all_uptime(self) -> Dict[str, float]:
        return {service: self.get_uptime(service) for service in self._checks}
    def generate_report(self) -> Dict[str, Any]:
        return {"services": self.get_all_uptime(), "total_services": len(self._checks), "timestamp": time.time()}
    def list_services(self) -> List[str]:
        return list(self._checks.keys())
    def get_service_history(self, service: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._checks.get(service, [])[-limit:]
''')

w('performance_report.py', '''"""Performance report."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PerformanceReport:
    def __init__(self) -> None:
        self._metrics: Dict[str, List[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._metrics.setdefault(metric_name, []).append(value)
    def get_summary(self, metric_name: str) -> Dict[str, float]:
        values = self._metrics.get(metric_name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": sum(values)/len(values), "count": len(values)}
    def generate_report(self) -> Dict[str, Any]:
        summaries = {name: self.get_summary(name) for name in self._metrics}
        return {"metrics": summaries, "total_metrics": len(self._metrics), "timestamp": time.time()}
    def list_metrics(self) -> List[str]:
        return list(self._metrics.keys())
    def clear(self, metric_name: str = "") -> int:
        if metric_name:
            n = len(self._metrics.get(metric_name, []))
            self._metrics.pop(metric_name, None)
            return n
        n = sum(len(v) for v in self._metrics.values())
        self._metrics.clear()
        return n
''')

w('incident_report.py', '''"""Incident report."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class IncidentReport:
    def __init__(self) -> None:
        self._incidents: List[Dict[str, Any]] = []
    def add_incident(self, incident: Dict[str, Any]) -> None:
        self._incidents.append(incident)
    def get_summary(self) -> Dict[str, Any]:
        total = len(self._incidents)
        by_severity: Dict[str, int] = {}
        for inc in self._incidents:
            sev = inc.get("severity", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {"total": total, "by_severity": by_severity, "timestamp": time.time()}
    def generate_report(self, period: str = "all") -> Dict[str, Any]:
        return {"period": period, "summary": self.get_summary(), "incidents": self._incidents[-50:]}
    def list_incidents(self, severity: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        results = self._incidents
        if severity:
            results = [i for i in results if i.get("severity") == severity]
        return results[-limit:]
    def count(self) -> int:
        return len(self._incidents)
    def clear(self) -> int:
        n = len(self._incidents)
        self._incidents.clear()
        return n
''')

w('cost_report.py', '''"""Cost report."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class CostReport:
    def __init__(self) -> None:
        self._costs: Dict[str, List[Dict[str, Any]]] = {}
    def record_cost(self, service: str, amount: float, category: str = "general") -> None:
        self._costs.setdefault(service, []).append({"amount": amount, "category": category, "timestamp": time.time()})
    def get_total(self, service: str = "") -> float:
        if service:
            return sum(c["amount"] for c in self._costs.get(service, []))
        return sum(sum(c["amount"] for c in costs) for costs in self._costs.values())
    def get_by_category(self) -> Dict[str, float]:
        categories: Dict[str, float] = {}
        for costs in self._costs.values():
            for c in costs:
                cat = c.get("category", "general")
                categories[cat] = categories.get(cat, 0) + c["amount"]
        return categories
    def generate_report(self) -> Dict[str, Any]:
        return {"total": self.get_total(), "by_category": self.get_by_category(), "services": list(self._costs.keys()), "timestamp": time.time()}
    def list_services(self) -> List[str]:
        return list(self._costs.keys())
    def get_service_costs(self, service: str) -> List[Dict[str, Any]]:
        return self._costs.get(service, [])
    def clear(self, service: str = "") -> int:
        if service:
            n = len(self._costs.get(service, []))
            self._costs.pop(service, None)
            return n
        n = sum(len(v) for v in self._costs.values())
        self._costs.clear()
        return n
''')

w('export.py', '''"""Report export."""
from __future__ import annotations
from typing import Any, Dict
import json

class ReportExporter:
    def __init__(self) -> None:
        self._exports: list = []
    def export_json(self, data: Dict[str, Any]) -> str:
        result = json.dumps(data, indent=2)
        self._exports.append({"format": "json", "size": len(result)})
        return result
    def export_csv(self, data: Dict[str, Any]) -> str:
        lines = ["key,value"]
        for k, v in data.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    lines.append(f"{k}.{sk},{sv}")
            else:
                lines.append(f"{k},{v}")
        result = "\\n".join(lines)
        self._exports.append({"format": "csv", "size": len(result)})
        return result
    def export_markdown(self, data: Dict[str, Any], title: str = "Report") -> str:
        lines = [f"# {title}", ""]
        for k, v in data.items():
            lines.append(f"## {k}")
            if isinstance(v, dict):
                for sk, sv in v.items():
                    lines.append(f"- **{sk}**: {sv}")
            else:
                lines.append(f"- {v}")
            lines.append("")
        result = "\\n".join(lines)
        self._exports.append({"format": "markdown", "size": len(result)})
        return result
    def get_export_history(self) -> list:
        return list(self._exports)
''')

w('__init__.py', '''"""Reporting subsystem."""
from .report_engine import ReportEngine
from .uptime_report import UptimeReport
from .performance_report import PerformanceReport
from .incident_report import IncidentReport
from .cost_report import CostReport
from .export import ReportExporter

__all__ = [
    "ReportEngine", "UptimeReport", "PerformanceReport",
    "IncidentReport", "CostReport", "ReportExporter"
]
''')

print("reporting/: 7 files created")
