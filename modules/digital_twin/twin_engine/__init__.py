"""Digital Twin engine package: model, mapper, snapshots, validation."""
from __future__ import annotations

from modules.digital_twin.twin_engine.digital_twin_analyzer import (
    TwinAnalysis,
    TwinAnalyzer,
)
from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel
from modules.digital_twin.twin_engine.digital_twin_engine import BuildResult, TwinEngine
from modules.digital_twin.twin_engine.digital_twin_mapper import (
    MappedEntity,
    TwinMapper,
    TwinMapperError,
)
from modules.digital_twin.twin_engine.digital_twin_registry import TwinModelRegistry
from modules.digital_twin.twin_engine.digital_twin_serializer import TwinSerializer
from modules.digital_twin.twin_engine.digital_twin_snapshot import (
    SnapshotDiff,
    TwinSnapshot,
    TwinSnapshotter,
    diff_snapshots,
)
from modules.digital_twin.twin_engine.digital_twin_validator import (
    TwinValidator,
    ValidationIssue,
    ValidationReport,
)

__all__ = [
    "BuildResult",
    "MappedEntity",
    "SnapshotDiff",
    "TwinAnalysis",
    "TwinAnalyzer",
    "TwinEngine",
    "TwinMapper",
    "TwinMapperError",
    "TwinModel",
    "TwinModelRegistry",
    "TwinSerializer",
    "TwinSnapshot",
    "TwinSnapshotter",
    "TwinValidator",
    "ValidationIssue",
    "ValidationReport",
    "diff_snapshots",
]
