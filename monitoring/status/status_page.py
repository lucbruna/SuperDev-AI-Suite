import time
from typing import Any, Dict, List, Optional
from .incidents import IncidentManager


class StatusPage:
    def __init__(self, incident_manager: Optional[IncidentManager] = None) -> None:
        self._services: Dict[str, str] = {}
        self._incident_manager = incident_manager or IncidentManager()

    def register_service(self, name: str, status: str = "healthy") -> None:
        self._services[name] = status

    def set_service_status(self, name: str, status: str) -> None:
        self._services[name] = status

    def generate(self) -> Dict[str, Any]:
        services_list = [
            {"name": name, "status": status}
            for name, status in self._services.items()
        ]
        red = sum(1 for s in self._services.values() if s == "unhealthy")
        yellow = sum(1 for s in self._services.values() if s == "degraded")
        total = len(self._services) or 1
        uptime_pct = ((total - red - yellow) / total) * 100.0

        all_incidents = self._incident_manager.list()
        active_incidents = [i for i in all_incidents if i.status != "resolved"]

        return {
            "overall_status": "healthy" if red == 0 else "degraded" if red == 0 else "unhealthy",
            "services": services_list,
            "incidents": [i.to_dict() for i in active_incidents],
            "uptime_percentage": round(uptime_pct, 2),
            "last_updated": time.time(),
        }

    def generate_html(self) -> str:
        data = self.generate()
        status_color = {"healthy": "green", "degraded": "yellow", "unhealthy": "red"}
        overall = data["overall_status"]
        color = status_color.get(overall, "gray")

        rows = ""
        for svc in data["services"]:
            sc = status_color.get(svc["status"], "gray")
            rows += f"<tr><td>{svc['name']}</td><td style='color:{sc};font-weight:bold'>{svc['status']}</td></tr>\n"

        incidents_html = ""
        for inc in data.get("incidents", []):
            incidents_html += f"<li>{inc['title']} - {inc['status']} ({inc['severity']})</li>\n"

        return f"""<!DOCTYPE html>
<html>
<head><title>System Status</title></head>
<body>
<h1>System Status</h1>
<div style="padding:20px;background:{color};color:white;text-align:center;font-size:24px;border-radius:8px">
{overall.upper()}
</div>
<h2>Uptime: {data['uptime_percentage']}%</h2>
<h3>Services</h3>
<table border="1" cellpadding="8">
<tr><th>Service</th><th>Status</th></tr>
{rows}
</table>
<h3>Active Incidents</h3>
<ul>{incidents_html or '<li>No active incidents</li>'}</ul>
<p><em>Last updated: {data['last_updated']}</em></p>
</body>
</html>"""
