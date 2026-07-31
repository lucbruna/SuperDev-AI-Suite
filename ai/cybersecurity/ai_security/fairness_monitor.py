"""
AI Fairness & Bias Monitoring
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import statistics


class BiasType(Enum):
    DEMOGRAPHIC_PARITY = "demographic_parity"
    EQUAL_OPPORTUNITY = "equal_opportunity"
    EQUALIZED_ODDS = "equalized_odds"
    CALIBRATION = "calibration"
    INDIVIDUAL_FAIRNESS = "individual_fairness"


@dataclass
class FairnessMetric:
    metric_name: str
    value: float
    threshold: float = 0.8
    passed: bool = True
    protected_group: str = ""
    reference_group: str = ""


@dataclass
class BiasAssessment:
    assessment_id: str
    model_id: str
    metrics: List[FairnessMetric] = field(default_factory=list)
    overall_score: float = 0.0
    is_fair: bool = True
    assessed_at: datetime = field(default_factory=datetime.now)
    recommendations: List[str] = field(default_factory=list)


class FairnessMonitor:
    def __init__(self):
        self.assessments: List[BiasAssessment] = []
        self.thresholds: Dict[BiasType, float] = {
            BiasType.DEMOGRAPHIC_PARITY: 0.8,
            BiasType.EQUAL_OPPORTUNITY: 0.8,
            BiasType.EQUALIZED_ODDS: 0.8,
        }
        self.prediction_logs: List[Dict[str, Any]] = []

    def log_prediction(self, model_id: str, prediction: Any, protected_attribute: str, true_label: Any = None) -> None:
        self.prediction_logs.append({
            "model_id": model_id, "prediction": prediction,
            "protected_attribute": protected_attribute, "true_label": true_label,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_demographic_parity(self, model_id: str, protected_attr: str) -> FairnessMetric:
        logs = [l for l in self.prediction_logs if l["model_id"] == model_id and l["protected_attribute"] == protected_attr]
        if not logs:
            return FairnessMetric("demographic_parity", 1.0, self.thresholds[BiasType.DEMOGRAPHIC_PARITY])
        positive_rate = sum(1 for l in logs if l["prediction"] == 1) / max(len(logs), 1)
        return FairnessMetric("demographic_parity", positive_rate, self.thresholds[BiasType.DEMOGRAPHIC_PARITY], passed=0.8 <= positive_rate <= 1.2)

    def calculate_equal_opportunity(self, model_id: str, protected_attr: str) -> FairnessMetric:
        logs = [l for l in self.prediction_logs if l["model_id"] == model_id and l["protected_attribute"] == protected_attr and l["true_label"] == 1]
        if not logs:
            return FairnessMetric("equal_opportunity", 1.0, self.thresholds[BiasType.EQUAL_OPPORTUNITY])
        tpr = sum(1 for l in logs if l["prediction"] == 1) / max(len(logs), 1)
        return FairnessMetric("equal_opportunity", tpr, self.thresholds[BiasType.EQUAL_OPPORTUNITY], passed=tpr >= 0.8)

    def assess(self, model_id: str, protected_attrs: List[str]) -> BiasAssessment:
        metrics = []
        for attr in protected_attrs:
            metrics.append(self.calculate_demographic_parity(model_id, attr))
            metrics.append(self.calculate_equal_opportunity(model_id, attr))
        overall = statistics.mean([m.value for m in metrics]) if metrics else 1.0
        is_fair = all(m.passed for m in metrics)
        recs = ["Increase training data diversity", "Apply re-weighting"] if not is_fair else []
        assessment = BiasAssessment(assessment_id=f"assess_{model_id}", model_id=model_id, metrics=metrics, overall_score=overall, is_fair=is_fair, recommendations=recs)
        self.assessments.append(assessment)
        return assessment

    def get_assessments(self, model_id: str = None) -> List[BiasAssessment]:
        if model_id:
            return [a for a in self.assessments if a.model_id == model_id]
        return self.assessments

    def set_threshold(self, bias_type: BiasType, threshold: float) -> None:
        self.thresholds[bias_type] = threshold

    def get_recommendations(self, assessment_id: str) -> List[str]:
        for a in self.assessments:
            if a.assessment_id == assessment_id:
                return a.recommendations
        return []

    def count(self) -> int:
        return len(self.assessments)
