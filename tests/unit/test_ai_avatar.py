"""Unit tests for the AI Avatar & Digital Human Engine (Volume 6)."""
import numpy as np
import pytest

from modules.ai_video_studio.ai_avatar import (
    ActorLibrary,
    AvatarEngine,
    BodySync,
    CharacterGenerator,
    DigitalHumanRenderer,
    ExpressionEngine,
    FacialCapture,
    GestureEngine,
    VirtualActor,
    Wardrobe,
    get_actor_library,
    get_avatar_engine,
)
from modules.ai_video_studio.ai_avatar.actor_library import ACTOR_LIBRARY
from modules.ai_video_studio.ai_avatar.body_capture import BodyCapture
from modules.ai_video_studio.core.constants import AvatarStyle


class TestActorLibrary:
    def test_library_has_2d_and_3d_actors(self):
        actors = ActorLibrary().list()
        dimensions = {a["dimension"] for a in actors}
        assert "2d" in dimensions and "3d" in dimensions

    def test_filter_by_style(self):
        actors = ActorLibrary().list(style=AvatarStyle.ANIME.value)
        assert actors and all(a["style"] == AvatarStyle.ANIME.value for a in actors)

    def test_filter_by_scene_returns_preferred(self):
        actor = ActorLibrary().select_for_scene("title_card")
        assert actor.id == "nova"

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError):
            ActorLibrary().get("does_not_exist")


class TestCharacterGenerator:
    def test_deterministic_seed(self):
        gen = CharacterGenerator()
        a = gen.generate(42).to_dict()
        b = gen.generate(42).to_dict()
        assert a == b

    def test_different_seeds_differ(self):
        gen = CharacterGenerator()
        a = gen.generate(1).to_dict()
        b = gen.generate(2).to_dict()
        assert a["name"] != b["name"]

    def test_spec_to_actor(self):
        spec = CharacterGenerator().generate(7)
        actor = spec.to_actor()
        assert isinstance(actor, VirtualActor)
        assert actor.style == spec.style


class TestWardrobe:
    def test_select_occasion(self):
        outfit = Wardrobe().select("business")
        assert outfit["name"] == "Business"
        assert "top_color" in outfit

    def test_style_nudges_palette(self):
        playful = Wardrobe().select("business", style=AvatarStyle.CARTOON.value)
        assert playful["style_hint"] == "playful"

    def test_accessories_for(self):
        acc = Wardrobe().accessories_for("tech", count=2)
        assert len(acc) == 2


class TestExpressionEngine:
    def test_names(self):
        names = ExpressionEngine().names()
        assert "happy" in names and "sad" in names and "angry" in names

    def test_apply(self):
        params = ExpressionEngine().apply("surprised", intensity=0.8)
        assert params["mouth_open"] > 0.5

    def test_interpolate(self):
        params = ExpressionEngine().interpolate("neutral", "happy", 0.5)
        assert -1 <= params["mouth_curve"] <= 1

    def test_timeline(self):
        frames = ExpressionEngine().timeline(
            [{"start": 0.0, "end": 1.0, "expression": "neutral"},
             {"start": 1.0, "end": 2.0, "expression": "happy"}],
            duration=2.0, fps=10,
        )
        assert len(frames) == 20
        assert all("mouth_open" in f for f in frames)


class TestGestureEngine:
    def test_names(self):
        assert "point" in GestureEngine().names()

    def test_plan_for_text(self):
        frames = GestureEngine().plan_for_text("This is the key point!", duration=2.0, fps=10)
        assert len(frames) == 20
        assert all("gesture" in f for f in frames)

    def test_plan_for_scene(self):
        frames = GestureEngine().plan_for_scene("intro", duration=1.0, fps=10)
        assert frames[0]["gesture"] == "wave"


class TestBodySync:
    def test_sync_produces_full_timeline(self):
        sync = BodySync().sync("Hello and welcome to this video.", duration=3.0, fps=12)
        assert sync["frames"] == 36
        frame = sync["timeline"][0]
        for key in ("mouth_open", "arm_left", "arm_right", "lean", "head_tilt", "emotion", "gesture"):
            assert key in frame


class TestFacialCapture:
    def test_landmarks_open_mouth(self):
        capture = FacialCapture()
        landmarks = {
            "mouth_top": [0.5, 0.40], "mouth_bottom": [0.5, 0.50],
            "mouth_left": [0.45, 0.45], "mouth_right": [0.55, 0.45],
            "left_eye": [0.40, 0.30], "right_eye": [0.60, 0.30],
            "left_brow": [0.40, 0.20], "right_brow": [0.60, 0.20],
        }
        params = capture.capture_from_landmarks(landmarks)
        assert params["mouth_open"] > 0.3

    def test_frame_fallback(self):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        frame[30:45, 20:44] = 255  # bright mouth zone
        params = FacialCapture().capture_from_frame(frame)
        assert "mouth_open" in params


class TestBodyCapture:
    def test_keypoints(self):
        capture = BodyCapture()
        params = capture.capture_from_keypoints({
            "left_shoulder": [0.4, 0.3], "right_shoulder": [0.6, 0.3],
            "left_hip": [0.4, 0.6], "right_hip": [0.6, 0.6],
            "left_wrist": [0.3, 0.1], "right_wrist": [0.7, 0.1],
        })
        assert params["arm_left"] > 0.5
        assert params["arm_right"] > 0.5


class TestDigitalHuman:
    def test_render_still(self, tmp_path):
        renderer = DigitalHumanRenderer(width=320, height=180)
        actor = ACTOR_LIBRARY[0]
        out = renderer.render_still(actor, {"emotion": "happy", "mouth_open": 0.5},
                                    output_path=tmp_path / "still.png")
        assert out.exists() and out.stat().st_size > 0

    def test_render_video(self, tmp_path):
        renderer = DigitalHumanRenderer(width=160, height=90)
        actor = ACTOR_LIBRARY[0]
        frames = [{"emotion": "neutral", "mouth_open": 0.3, "arm_left": 0.5} for _ in range(8)]
        result = renderer.render_video(actor, frames, fps=8, output_path=tmp_path / "clip.mp4")
        assert result["output_path"] and result["frames"] == 8


class TestAvatarEngine:
    def test_list_actors(self):
        engine = AvatarEngine(library=ActorLibrary())
        assert len(engine.list_actors()) == len(ACTOR_LIBRARY)

    def test_generate_character_is_idempotent(self):
        engine = AvatarEngine(library=ActorLibrary())
        engine.generate_character(123)
        engine.generate_character(123)
        assert len(engine.list_actors()) == len(ACTOR_LIBRARY) + 1

    def test_generate_character(self):
        engine = AvatarEngine()
        actor = engine.generate_character(123)
        assert actor["id"] == "gen_123"

    def test_generate_presenter_still(self):
        engine = AvatarEngine()
        result = engine.generate_presenter(
            "This is a test presentation.", actor_id="maya",
            scene_type="intro", expression="happy", duration=1.0, fps=8,
            render_video=False,
        )
        assert result["status"] == "ok"
        assert result["actor"]["id"] == "maya"
        assert "output_path" in result

    def test_generate_presenter_video(self):
        engine = AvatarEngine()
        result = engine.generate_presenter(
            "Welcome everyone to this demo.", actor_id="nova",
            duration=1.0, fps=8,
        )
        assert result["status"] == "ok"
        assert result["output_bytes"] > 0

    def test_capture_facial(self):
        engine = AvatarEngine()
        params = engine.capture_facial(landmarks={"mouth_top": [0.5, 0.4], "mouth_bottom": [0.5, 0.55]})
        assert params["source"] == "landmarks"

    def test_stats(self):
        engine = AvatarEngine()
        stats = engine.stats()
        assert stats["actors"] >= 1


class TestSingleton:
    def test_get_actor_library(self):
        assert get_actor_library() is get_actor_library()

    def test_get_avatar_engine(self):
        assert get_avatar_engine() is get_avatar_engine()
