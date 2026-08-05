"""Unit tests for the AI Avatar & Digital Human Engine (Volume 6)."""
import pytest

from modules.ai_video_studio.ai_avatar_engine import (
    AvatarCache,
    AvatarEngine,
    AvatarLearning,
    AvatarLogger,
    AvatarManager,
    AvatarOptimizer,
    AvatarPermissions,
    AvatarProfile,
    AvatarScheduler,
    AvatarStatistics,
    profile_from_dict,
)
from modules.ai_video_studio.ai_avatar_engine.avatar_registry import get_avatar_registry
from modules.ai_video_studio.ai_avatar_engine.clothing import get_clothing_engine
from modules.ai_video_studio.ai_avatar_engine.digital_humans import get_digital_human_engine
from modules.ai_video_studio.ai_avatar_engine.emotions import get_emotion_engine
from modules.ai_video_studio.ai_avatar_engine.facial_animation import get_facial_engine
from modules.ai_video_studio.ai_avatar_engine.gestures import get_gesture_engine
from modules.ai_video_studio.ai_avatar_engine.hairstyles import get_hairstyle_engine
from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library
from modules.ai_video_studio.ai_avatar_engine.motion_capture import get_mocap_engine
from modules.ai_video_studio.ai_avatar_engine.training import get_training_engine


PROFILE = AvatarProfile(
    id="test_host", name="Test Host", style="realistic", dimension="3d",
    gender="female", age_group="adult", default_outfit="business",
    tags=["test"],
)


class TestAvatarProfile:
    def test_validation(self):
        with pytest.raises(ValueError):
            AvatarProfile(id="", name="X")
        with pytest.raises(ValueError):
            AvatarProfile(id="x", name="X", style="bogus")

    def test_roundtrip(self):
        data = PROFILE.to_dict()
        restored = profile_from_dict(data)
        assert restored == PROFILE

    def test_dict_shape(self):
        d = PROFILE.to_dict()
        for key in ("id", "name", "style", "dimension", "gender", "age_group"):
            assert key in d


class TestAvatarLibrary:
    def test_domain_catalogs(self):
        assert get_avatar_library().count() >= 40

    def test_filters(self):
        profiles = get_avatar_library().list(dimension="2d")
        assert profiles and all(p.dimension == "2d" for p in profiles)

    def test_get(self):
        profile = get_avatar_library().get("biz_maya")
        assert profile.style == "realistic"


class TestDigitalHumanEngine:
    def test_generate(self):
        result = get_digital_human_engine().generate(PROFILE, seed=7)
        for section in ("body", "face", "skin", "eyes", "hair", "clothing", "accessories"):
            assert section in result

    def test_summary(self):
        summary = get_digital_human_engine().summary(PROFILE)
        assert summary["profile"] == "test_host"
        assert summary["dimension"] == "3d"


class TestEmotions:
    def test_names(self):
        names = get_emotion_engine().names()
        assert len(names) == 12
        assert "happy" in names and "angry" in names

    def test_preset_fields(self):
        preset = get_emotion_engine().get("surprise")
        assert preset.facial["mouth_open"] > 0.5

    def test_timeline(self):
        frames = get_emotion_engine().timeline(
            [{"start": 0.0, "end": 1.0, "emotion": "neutral"},
             {"start": 1.0, "end": 2.0, "emotion": "happy"}],
            duration=2.0, fps=10)
        assert len(frames) == 20


class TestGestures:
    def test_plan(self):
        frames = get_gesture_engine().plan_for_text("This is the key point!", duration=2.0, fps=10)
        assert len(frames) == 20
        assert frames[0]["gesture"] == "point"

    def test_context(self):
        assert get_gesture_engine().for_context("teaching")


class TestFacialAnimation:
    def test_compose(self):
        params = get_facial_engine().compose(t=0.0, smile=0.9, mouth_open=0.5)
        assert params["smile"] > 0.5
        assert params["mouth_open"] > 0.4

    def test_mesh(self):
        params = get_facial_engine().compose()
        mesh = get_facial_engine().mesh(params)
        assert "mouth_left" in mesh and "left_eye" in mesh


class TestClothing:
    def test_dress(self):
        outfit = get_clothing_engine().dress(occasion="business", gender="female")
        assert outfit["occasion"] == "business"
        assert outfit["shirt"]["type"] == "dress_shirt"


class TestHairstyles:
    def test_catalogs(self):
        engine = get_hairstyle_engine()
        assert len(engine.catalogs()) == 9

    def test_select(self):
        style = get_hairstyle_engine().select("short", color="black")
        assert style["color"]["name"] == "black"


class TestMotionCapture:
    def test_process(self):
        keyframes = [
            {"left_wrist": [0.4, 0.2], "right_wrist": [0.6, 0.2],
             "left_shoulder": [0.4, 0.3], "right_shoulder": [0.6, 0.3]} for _ in range(5)
        ]
        result = get_mocap_engine().process(keyframes, fps=10)
        assert result["frames"] == 5
        assert "motion" in result and "label" in result


class TestTraining:
    def test_feedback_and_summary(self):
        training = get_training_engine()
        training.record_feedback(profile_id="test_host", gesture="point",
                                 emotion="happy", score=0.9)
        summary = training.summary()
        assert summary["identity"] and summary["gestures"] and summary["facial"]

    def test_quality(self):
        result = training_quality()
        assert "score" in result


def training_quality():
    from modules.ai_video_studio.ai_avatar_engine.training import get_training_engine

    return get_training_engine().validate({"identity": {"id": "x"}, "body": {}, "face": {},
                                           "skin": {}, "hair": {}, "clothing": {}})


class TestCore:
    def test_engine_generate(self):
        engine = AvatarEngine()
        engine.register_profile(PROFILE)
        result = engine.generate_avatar(PROFILE, quality="high", seed=3)
        assert result["status"] == "generated"
        assert result["profile"]["id"] == "test_host"

    def test_engine_jobs_and_stats(self):
        engine = AvatarEngine()
        engine.register_profile(PROFILE)
        engine.generate_avatar(PROFILE, quality="draft")
        assert len(engine.list_jobs()) == 1
        assert engine.stats()["profiles"] >= 1

    def test_optimizer(self):
        settings = AvatarOptimizer().optimize(quality="final", fps=24)
        assert settings["fps"] == 36

    def test_scheduler(self):
        scheduler = AvatarScheduler()
        task_id = scheduler.enqueue({"kind": "render"}, priority=1)
        assert scheduler.next()["id"] == task_id

    def test_learning(self):
        learning = AvatarLearning()
        learning.record("style:realistic", 0.9)
        assert learning.preferred("style:") == "realistic"

    def test_statistics(self):
        stats = AvatarStatistics()
        stats.record(style="realistic", dimension="3d", duration_ms=100)
        assert stats.summary()["total"] == 1

    def test_cache(self):
        cache = AvatarCache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get("a") is None
        assert cache.get("c") == 3

    def test_permissions(self):
        perms = AvatarPermissions()
        assert perms.check("admin", "delete")
        assert not perms.check("viewer", "publish")

    def test_logger(self):
        logger = AvatarLogger(capacity=5)
        logger.info("test_event", profile="x")
        assert logger.recent()[-1]["event"] == "test_event"

    def test_manager_sessions(self):
        manager = AvatarManager()
        manager.register(PROFILE)
        session = manager.start_session("test_host")
        assert session["profile_id"] == "test_host"
        assert manager.end_session(session["id"])["frames"] == 0

    def test_registry_singleton(self):
        assert get_avatar_registry() is get_avatar_registry()


class TestApi:
    def test_router_imports(self):
        from modules.ai_video_studio.api.routes.avatar_engine import router

        assert router is not None
