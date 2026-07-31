"""Forecasting models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ForecastMethod(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    MOVING_AVG = "moving_avg"
    ARIMA = "arima"
    PROPHET = "prophet"
    ENSEMBLE = "ensemble"


class SeasonalityType(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class TimeSeriesData:
    timestamps: List[datetime]
    values: List[float]
    labels: List[str] = field(default_factory=list)


@dataclass
class ForecastRequest:
    request_id: str
    data: TimeSeriesData
    method: ForecastMethod = ForecastMethod.LINEAR
    horizon: int = 10
    confidence_level: float = 0.95
    seasonality: SeasonalityType = SeasonalityType.NONE
    include_history: bool = True


@dataclass
class ForecastPoint:
    timestamp: datetime
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float


@dataclass
class ForecastResult:
    request_id: str
    method: ForecastMethod
    points: List[ForecastPoint] = field(default_factory=list)
    accuracy_metrics: Dict[str, float] = field(default_factory=dict)
    model_params: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None


@dataclass
class ForecastModel:
    model_id: str
    method: ForecastMethod
    trained: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    accuracy: float = 0.0
    trained_at: Optional[datetime] = None
