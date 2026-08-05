"""Editor engine — core orchestration for the professional video editor.

The engine owns the timeline plus the editing tools (trim/ripple/slip/slide,
transitions, effects, markers, subtitles), an undo/redo stack, a clipboard and
a renderer. It is deliberately dependency-light: every operation is pure data
manipulation on the timeline, and rendering delegates to the timeline renderer
(which encodes through FFmpeg).
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import StatTracker, UndoStack, make_logger
from modules.ai_video_studio.ai_editor.clipboard_manager import ClipboardManager
from modules.ai_video_studio.ai_editor.undo_redo import UndoRedoManager
from modules.ai_video_studio.ai_editor.timeline.timeline_engine import ProfessionalTimeline
from modules.ai_video_studio.ai_editor.timeline.ripple_edit import RippleEdit
from modules.ai_video_studio.ai_editor.timeline.slip_edit import SlipEdit
from modules.ai_video_studio.ai_editor.timeline.slide_edit import SlideEdit
from modules.ai_video_studio.ai_editor.timeline.trim_engine import TrimEngine
from modules.ai_video_studio.ai_editor.timeline.snap_engine import SnapEngine
from modules.ai_video_studio.ai_editor.timeline.magnetic_timeline import MagneticTimeline

logger = make_logger("editor.engine")


class EditorEngine:
    """Professional editing engine: timeline + tools + render.

    Example::

        engine = EditorEngine()
        clip = engine.add_clip({"source": "intro.mp4", "start": 0.0, "end": 5.0})
        engine.ripple_delete(clip["id"])
        engine.undo()
    """

    def __init__(self) -> None:
        self.timeline = ProfessionalTimeline()
        self.undo_manager = UndoRedoManager()
        self.clipboard = ClipboardManager()
        self.snap = SnapEngine(self.timeline)
        self.ripple = RippleEdit(self.timeline)
        self.slip = SlipEdit(self.timeline)
        self.slide = SlideEdit(self.timeline)
        self.trim = TrimEngine(self.timeline)
        self.magnetic = MagneticTimeline(self.timeline)
        self._op_stats = StatTracker()

    # ── Snapshot / undo ──────────────────────────────────────────
    def _snapshot(self) -> None:
        self.undo_manager.push(self.timeline.to_dict())

    def undo(self) -> bool:
        restored = self.undo_manager.undo()
        if restored is not None:
            self.timeline.load_dict(restored)
            return True
        return False

    def redo(self) -> bool:
        restored = self.undo_manager.redo()
        if restored is not None:
            self.timeline.load_dict(restored)
            return True
        return False

    # ── Clip operations (each is undoable) ───────────────────────
    def add_clip(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        self._snapshot()
        result = self.timeline.add_clip(clip, track=track)
        self._op_stats.push(1.0)
        return result

    def remove_clip(self, clip_id: str) -> dict[str, Any] | None:
        self._snapshot()
        removed = self.timeline.remove_clip(clip_id)
        if removed is not None:
            self._op_stats.push(1.0)
        return removed

    def move_clip(self, clip_id: str, start: float, track: str | None = None) -> dict[str, Any]:
        self._snapshot()
        moved = self.timeline.move_clip(clip_id, start, track=track)
        self._op_stats.push(1.0)
        return moved

    def trim_clip(self, clip_id: str, new_start: float, new_end: float) -> dict[str, Any]:
        self._snapshot()
        return self.trim.trim(clip_id, new_start, new_end)

    def roll_edit(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Trim edit that adjusts a clip's boundary by ``delta`` seconds."""
        self._snapshot()
        return self.trim.roll(clip_id, delta)

    def ripple_delete(self, clip_id: str) -> dict[str, Any] | None:
        """Delete a clip and ripple the following clips left."""
        self._snapshot()
        removed = self.ripple.delete(clip_id)
        self._op_stats.push(1.0)
        return removed

    def ripple_slice(self, clip_id: str, at: float) -> list[dict[str, Any]]:
        """Split a clip at ``at`` (timeline time) with ripple."""
        self._snapshot()
        return self.ripple.slice(clip_id, at)

    def slip_clip(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Change a clip's source in/out without moving its timeline position."""
        self._snapshot()
        return self.slip.slip(clip_id, delta)

    def slide_clip(self, clip_id: str, delta: float) -> dict[str, Any]:
        """Move a clip while adjusting the neighbours to preserve the gap."""
        self._snapshot()
        return self.slide.slide(clip_id, delta)

    def apply_transition(self, clip_a_id: str, clip_b_id: str, transition: str, duration: float) -> dict[str, Any]:
        self._snapshot()
        return self.timeline.set_transition(clip_a_id, clip_b_id, transition, duration)

    def apply_effect(self, clip_id: str, effect: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._snapshot()
        return self.timeline.add_clip_effect(clip_id, effect, params or {})

    def set_volume(self, clip_id: str, volume: float, t: float = 0.0) -> dict[str, Any]:
        """Set an audio clip's volume (optionally at a keyframe time)."""
        self._snapshot()
        return self.timeline.set_clip_volume(clip_id, volume, t)

    def add_marker(self, time: float, label: str = "", color: str = "yellow") -> dict[str, Any]:
        return self.timeline.add_marker(time, label=label, color=color)

    def add_subtitle(self, start: float, end: float, text: str) -> dict[str, Any]:
        if end <= start:
            raise ValidationError("Subtitle end must be after start", field="subtitle")
        return self.timeline.add_subtitle(start, end, text)

    def snap_time(self, time: float, radius: float = 0.5) -> float:
        """Snap ``time`` to nearby clip edges / markers (or return unchanged)."""
        return self.snap.snap(time, radius=radius)

    def copy_clip(self, clip_id: str) -> int:
        return self.clipboard.copy_clip(self.timeline.get_clip(clip_id))

    def paste_clip(self, time: float, track: str = "video") -> dict[str, Any]:
        return self.timeline.add_clip(self.clipboard.paste_clip(time), track=track)

    # ── Render ───────────────────────────────────────────────────
    def render(
        self,
        output_path: str,
        *,
        fps: int = 24,
        width: int | None = None,
        height: int | None = None,
        progress: bool = True,
    ) -> dict[str, Any]:
        """Render the whole timeline to a real video file."""
        from modules.ai_video_studio.ai_editor.timeline.timeline_renderer import TimelineRenderer

        if not self.timeline.clips:
            raise ValidationError("Timeline is empty — nothing to render", field="timeline")
        renderer = TimelineRenderer(self.timeline)
        return renderer.render(output_path, fps=fps, width=width, height=height, progress=progress)

    def preview_frame(self, time: float, width: int = 320, height: int = 180) -> Any:
        """Return a small preview frame at ``time`` (real composited pixels)."""
        from modules.ai_video_studio.ai_editor.timeline.timeline_renderer import TimelineRenderer

        return TimelineRenderer(self.timeline).frame_at(time, width=width, height=height)

    # ── Introspection ────────────────────────────────────────────
    def stats(self) -> dict[str, float]:
        return {
            **self._op_stats.stats(),
            "duration": self.timeline.duration(),
            "clip_count": self.timeline.clip_count(),
        }

    def to_dict(self) -> dict[str, Any]:
        return self.timeline.to_dict()


_editor_engine: EditorEngine | None = None


def get_editor_engine() -> EditorEngine:
    """Cached singleton editor engine."""
    global _editor_engine
    if _editor_engine is None:
        _editor_engine = EditorEngine()
    return _editor_engine
