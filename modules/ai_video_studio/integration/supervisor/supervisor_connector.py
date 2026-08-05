"""AI Supervisor Connector — facade over the supervisor components."""
from __future__ import annotations


from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.supervisor.ai_supervisor import (
    get_ai_supervisor,
)
from modules.ai_video_studio.integration.supervisor.anomaly_detection import (
    get_anomaly_detection,
)
from modules.ai_video_studio.integration.supervisor.automatic_optimizer import (
    get_automatic_optimizer,
)
from modules.ai_video_studio.integration.supervisor.predictive_analysis import (
    get_predictive_analysis,
)
from modules.ai_video_studio.integration.supervisor.self_healing import get_self_healing
from modules.ai_video_studio.integration.supervisor.workload_distribution import (
    get_workload_distribution,
)


class SupervisorConnector(DomainConnector):
    """Supervision, self-healing, optimization, prediction, anomalies and workload."""

    domain = "supervisor"
    description = "AI supervision, self-healing, optimization, prediction, anomaly detection and workload distribution"

    def __init__(self) -> None:
        super().__init__()
        self._register("report", lambda d: get_ai_supervisor().report())
        self._register("remediate", lambda d: get_self_healing().remediate(d.get("issue", "")))
        self._register("optimize", lambda d: get_automatic_optimizer().optimize(**d))
        self._register("forecast", lambda d: get_predictive_analysis().forecast(
            d.get("series", []), horizon=d.get("horizon", 1)))
        self._register("detect_anomalies", lambda d: get_anomaly_detection().detect(
            d.get("series", []), threshold=d.get("threshold", 2.0)))
        self._register("distribute", lambda d: get_workload_distribution().plan(
            d.get("jobs", []), d.get("workers", [])))


_supervisor_connector: SupervisorConnector | None = None


def get_supervisor_connector() -> SupervisorConnector:
    global _supervisor_connector
    if _supervisor_connector is None:
        _supervisor_connector = SupervisorConnector()
    return _supervisor_connector
