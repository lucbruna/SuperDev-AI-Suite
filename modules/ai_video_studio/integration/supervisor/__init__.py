"""Supervisor — AI supervision, self-healing, optimization, prediction, anomalies and workload distribution."""
from modules.ai_video_studio.integration.supervisor.anomaly_detection import (
    AnomalyDetection,
    get_anomaly_detection,
)
from modules.ai_video_studio.integration.supervisor.self_healing import (
    SelfHealing,
    get_self_healing,
)
from modules.ai_video_studio.integration.supervisor.supervisor_connector import (
    SupervisorConnector,
    get_supervisor_connector,
)

__all__ = [
    "AnomalyDetection",
    "get_anomaly_detection",
    "SelfHealing",
    "get_self_healing",
    "SupervisorConnector",
    "get_supervisor_connector",
]
