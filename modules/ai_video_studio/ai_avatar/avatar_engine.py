"""Avatar Engine — AI Avatar & Digital Human Engine (blueprint Volume 6).

Orchestrates the whole avatar pillar:

1. **Actor selection** — pick a virtual actor from the library (or generate
   one procedurally) for the scene.
2. **Emotion + gesture planning** — expression timeline from the script and
   automatic gesture plan.
3. **Body sync** — fuse everything into a per-frame animation timeline.
4. **Rendering** — the digital-human renderer produces a real MP4/PNG.
5. **Capture** — facial/body parameter extraction from external sources.

Also provides the standard cross-cutting components (scheduler, optimizer,
learning, statistics, memory, history) so the subsystem matches the
architectural pattern of every other studio pillar.
"""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.ai_avatar.actor_library import ActorLibrary, VirtualActor, get_actor_library
from modules.ai_video_studio.ai_avatar.avatar_history import get_avatar_history
from modules.ai_video_studio.ai_avatar.avatar_learning import get_avatar_learning
from modules.ai_video_studio.ai_avatar.avatar_memory import get_avatar_memory
from modules.ai_video_studio.ai_avatar.avatar_optimizer import get_avatar_optimizer
from modules.ai_video_studio.ai_avatar.avatar_scheduler import get_avatar_scheduler
from modules.ai_video_studio.ai_avatar.avatar_statistics import get_avatar_statistics
from modules.ai_video_studio.ai_avatar.body_sync import get_body_sync
from modules.ai_video_studio.ai_avatar.character_generator import get_character_generator
from modules.ai_video_studio.ai_avatar.digital_human import DigitalHumanRenderer, get_digital_human
from modules.ai_video_studio.ai_avatar.expression_engine import get_expression_engine
from modules.ai_video_studio.ai_avatar.facial_capture import get_facial_capture
from modules.ai_video_studio.ai_avatar.gesture_engine import get_gesture_engine
from modules.ai_video_studio.ai_avatar.wardrobe import get_wardrobe
from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("avatar_engine")


class AvatarEngine:
    """End-to-end virtual presenter generation engine."""

    def __init__(
        self,
        *,
        library: ActorLibrary | None = None,
        renderer: DigitalHumanRenderer | None = None,
    ) -> None:
        self.library = library or get_actor_library()
        self.renderer = renderer or get_digital_human()
        self.body_sync = get_body_sync()
        self.expressions = get_expression_engine()
        self.gestures = get_gesture_engine()
        self.wardrobe = get_wardrobe()
        self.characters = get_character_generator()
        self.facial_capture = get_facial_capture()
        self.scheduler = get_avatar_scheduler()
        self.optimizer = get_avatar_optimizer()
        self.learning = get_avatar_learning()
        self.statistics = get_avatar_statistics()
        self.memory = get_avatar_memory()
        self.history = get_avatar_history()
        self._jobs: dict[str, dict[str, Any]] = {}

    # ── Actor management ──────────────────────────────────────────
    def list_actors(self, **filters: Any) -> list[dict[str, Any]]:
        return self.library.list(**filters)

    def get_actor(self, actor_id: str) -> VirtualActor:
        return self.library.get(actor_id)

    def generate_character(self, seed: int, **kw: Any) -> dict[str, Any]:
        """Procedurally generate a unique virtual presenter.

        The character is added to this engine's actor library (idempotent:
        repeated seeds don't duplicate the actor).
        """
        spec = self.characters.generate(seed, **kw)
        actor = spec.to_actor()
        self.library.add(actor)
        return actor.to_dict()

    def select_for_scene(self, scene_type: str = "content", **kw: Any) -> dict[str, Any]:
        return self.library.select_for_scene(scene_type, **kw).to_dict()

    # ── Presenter generation ───────────────────────────────────────
    def generate_presenter(
        self,
        script: str,
        *,
        actor_id: str | None = None,
        style: str | None = None,
        dimension: str | None = None,
        gender: str | None = None,
        scene_type: str = "content",
        expression: str = "neutral",
        outfit: str | None = None,
        duration: float = 5.0,
        fps: int = 24,
        quality: str = "high",
        seed: int | None = None,
        job_id: str | None = None,
        render_video: bool = True,
    ) -> dict[str, Any]:
        """Generate a complete virtual-presenter video (or still).

        Orchestrates actor selection → emotion/gesture plan → body sync →
        render, and records everything in statistics/memory/history.
        """
        started = time.time()
        if not script.strip():
            raise ValidationError("script must not be empty", field="script")
        if duration <= 0:
            raise ValidationError("duration must be positive", field="duration")

        rid = job_id or f"avatar_{len(self._jobs) + 1}"
        logger.info("generate_presenter job=%s actor=%s scene=%s", rid, actor_id, scene_type)

        # 1. Actor
        if actor_id:
            actor = self.library.get(actor_id)
        elif seed is not None:
            spec = self.characters.generate(seed, style=style, dimension=dimension, gender=gender)
            actor = spec.to_actor()
            self.library.add(actor)
        else:
            actor = self.library.select_for_scene(
                scene_type, style=style, gender=gender,
            )
        if style:
            actor = self._restyle(actor, style)

        # 2. Optimizer profile
        profile = self.optimizer.optimize(quality=quality, fps=fps)
        fps = profile["fps"]

        # 3. Emotion plan (scene-aware default → requested expression)
        expr_segments = self._emotion_segments(scene_type, expression, duration)
        expr_frames = self.expressions.timeline(expr_segments, duration=duration, fps=fps)

        # 4. Gesture plan
        gest_frames = self.gestures.plan_for_text(script, duration=duration, fps=fps)

        # 5. Body sync → final timeline
        synced = self.body_sync.sync(
            script, duration=duration, fps=fps,
            expressions=expr_frames, gestures=gest_frames, base_expression=expression,
        )
        timeline = synced["timeline"]

        # 6. Render
        result: dict[str, Any] = {
            "id": rid,
            "actor": actor.to_dict(),
            "script": script[:500],
            "scene_type": scene_type,
            "expression": expression,
            "outfit": outfit or actor.default_outfit,
            "duration": round(duration, 3),
            "fps": fps,
            "quality": quality,
            "total_frames": len(timeline),
            "elapsed_seconds": 0.0,
            "status": "ok",
        }
        if render_video:
            video = self.renderer.render_video(
                actor, timeline, fps=fps, outfit=outfit or actor.default_outfit,
            )
            result.update({
                "output_path": video["output_path"],
                "output_bytes": video["bytes"],
                "encode_engine": video["engine"],
                "video_frames": video["frames"],
            })
        else:
            still = self.renderer.render_still(actor, timeline[0] if timeline else {}, outfit=outfit or actor.default_outfit)
            result.update({"output_path": str(still), "output_bytes": still.stat().st_size, "encode_engine": "pillow-png"})

        result["elapsed_seconds"] = round(time.time() - started, 3)
        self._jobs[rid] = result

        # Cross-cutting records.
        self.statistics.record(actor_id=actor.id, scene_type=scene_type, duration_ms=result["elapsed_seconds"] * 1000)
        self.memory.remember(actor.id, {"expression": expression, "scene_type": scene_type, "outfit": outfit or actor.default_outfit})
        self.history.push(result)
        return result

    # ── Capture ───────────────────────────────────────────────────
    def capture_facial(self, landmarks: dict[str, Any] | None = None,
                       frame: Any | None = None) -> dict[str, Any]:
        if frame is not None:
            return self.facial_capture.capture_from_frame(frame)
        if landmarks is not None:
            return self.facial_capture.capture_from_landmarks(landmarks)
        raise ValidationError("provide either landmarks or frame", field="frame")

    def capture_body(self, keypoints: dict[str, Any] | None = None,
                     frame: Any | None = None) -> dict[str, Any]:
        from modules.ai_video_studio.ai_avatar.body_capture import get_body_capture

        capture = get_body_capture()
        if frame is not None:
            return capture.capture_from_frame(frame)
        if keypoints is not None:
            return capture.capture_from_keypoints(keypoints)
        raise ValidationError("provide either keypoints or frame", field="frame")

    # ── Jobs / metadata ───────────────────────────────────────────
    def get(self, job_id: str) -> dict[str, Any] | None:
        return dict(self._jobs[job_id]) if job_id in self._jobs else None

    def list_jobs(self) -> list[str]:
        return list(self._jobs)

    def stats(self) -> dict[str, Any]:
        return {
            "actors": len(self.library.list()),
            "jobs": len(self._jobs),
            "summary": self.statistics.summary(),
        }

    # ── Helpers ───────────────────────────────────────────────────
    @staticmethod
    def _emotion_segments(scene_type: str, expression: str, duration: float) -> list[dict[str, Any]]:
        """Scene-aware emotion flow: intro/excited → base → outro/calm."""
        if expression != "neutral":
            return [{"start": 0.0, "end": duration, "expression": expression}]
        flow = {
            "intro": [("neutral", 0.3), ("excited", 0.4), ("happy", 0.3)],
            "outro": [("happy", 0.5), ("calm", 0.5)],
            "title_card": [("neutral", 1.0)],
            "highlight": [("excited", 0.6), ("happy", 0.4)],
            "content": [("neutral", 0.7), ("happy", 0.3)],
            "credits": [("calm", 1.0)],
        }.get(scene_type, [("neutral", 1.0)])
        segments: list[dict[str, Any]] = []
        cursor = 0.0
        for name, weight in flow:
            length = duration * weight
            segments.append({"start": cursor, "end": min(cursor + length, duration), "expression": name})
            cursor += length
        return segments

    def _restyle(self, actor: VirtualActor, style: str) -> VirtualActor:
        """Return a copy of ``actor`` with an overridden style (2D/3D stays)."""
        from dataclasses import replace

        return replace(actor, style=style, id=f"{actor.id}_{style}")


_avatar_engine: AvatarEngine | None = None


def get_avatar_engine() -> AvatarEngine:
    """Return the shared avatar engine singleton."""
    global _avatar_engine
    if _avatar_engine is None:
        _avatar_engine = AvatarEngine()
    return _avatar_engine
