"""Object/face/planar tracking subsystem."""
from __future__ import annotations

from .tracking_engine import TrackingEngine, TrackerResult
from .object_tracking import TemplateTracker
from .planar_tracking import PlanarTracker
from .marker_tracking import MarkerTracker
from .motion_tracking import MotionTracker

__all__ = [
    "TrackingEngine",
    "TrackerResult",
    "TemplateTracker",
    "PlanarTracker",
    "MarkerTracker",
    "MotionTracker",
]

engine = TrackingEngine()

# Register the self-contained built-in trackers on the shared engine.
# (TemplateTracker and PlanarTracker need a user-supplied template, so
# they are constructed explicitly by callers, not auto-registered.)
engine.register("marker", MarkerTracker())
engine.register("motion", MotionTracker())
