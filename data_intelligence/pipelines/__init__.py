"""Pipelines subsystem (Volume 22).

Composes extraction, cleaning, transformation, indicator and sink stages
into repeatable data pipelines.
"""

from __future__ import annotations

from data_intelligence.pipelines.base import (PipelineError, PipelineStage)
from data_intelligence.pipelines.cleaning import CleaningStage
from data_intelligence.pipelines.extraction import ExtractionStage
from data_intelligence.pipelines.indicator import IndicatorStage
from data_intelligence.pipelines.orchestrator import (PipelineOrchestrator,
                                                      STAGE_REGISTRY)
from data_intelligence.pipelines.sink import SinkStage
from data_intelligence.pipelines.transformation import TransformationStage

__all__ = [
    "PipelineOrchestrator", "PipelineStage", "PipelineError",
    "ExtractionStage", "CleaningStage", "TransformationStage",
    "IndicatorStage", "SinkStage", "STAGE_REGISTRY",
]
