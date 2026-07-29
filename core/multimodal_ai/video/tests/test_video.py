from __future__ import annotations

import pytest

from ..frame_analyzer import FrameAnalyzer
from ..activity_detection import ActivityDetector
from ..event_recognition import EventRecognizer
from ..video_summary import VideoSummarizer
from ..video_engine import VideoEngine, VideoEngineConfig, VideoEngineMetrics, VideoEngineState


@pytest.fixture
def sample_video() -> bytes:
    return b"FAKE_VIDEO_DATA_" * 1000


@pytest.mark.asyncio
async def test_video_engine_initialize_and_stop():
    engine = VideoEngine()
    assert engine.state == VideoEngineState.UNINITIALIZED
    await engine.initialize()
    assert engine.state == VideoEngineState.READY
    await engine.stop()
    assert engine.state == VideoEngineState.STOPPED


@pytest.mark.asyncio
async def test_video_engine_process_video(sample_video: bytes):
    engine = VideoEngine()
    await engine.initialize()
    result = await engine.process_video(sample_video)
    assert result["status"] == "processed"
    assert "frames" in result
    assert "activities" in result
    assert "events" in result
    assert engine.metrics.total_videos_processed == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_video_engine_analyze_frames(sample_video: bytes):
    engine = VideoEngine()
    await engine.initialize()
    frames = await engine.analyze_frames(sample_video, frame_count=5)
    assert len(frames) == 5
    assert "analysis" in frames[0]
    assert engine.metrics.total_frames_analyzed == 5
    await engine.stop()


@pytest.mark.asyncio
async def test_video_engine_detect_activity(sample_video: bytes):
    engine = VideoEngine()
    await engine.initialize()
    activities = await engine.detect_activity(sample_video)
    assert len(activities) == 6
    assert activities[0]["type"] == "walking"
    assert engine.metrics.total_activities_detected == 6
    await engine.stop()


@pytest.mark.asyncio
async def test_video_engine_recognize_event(sample_video: bytes):
    engine = VideoEngine()
    await engine.initialize()
    events = await engine.recognize_event(sample_video)
    assert len(events) == 6
    assert events[0]["type"] == "safety_violation"
    assert engine.metrics.total_events_recognized == 6
    await engine.stop()


@pytest.mark.asyncio
async def test_video_engine_get_metrics(sample_video: bytes):
    engine = VideoEngine()
    await engine.initialize()
    await engine.process_video(sample_video)
    metrics = await engine.get_metrics()
    assert metrics.total_videos_processed == 1
    assert metrics.average_processing_time_ms >= 0
    await engine.stop()


def test_video_engine_config_defaults():
    config = VideoEngineConfig()
    assert config.device == "cpu"
    assert config.frame_sample_rate == 30
    assert config.max_duration_seconds == 3600


def test_video_engine_metrics():
    metrics = VideoEngineMetrics()
    assert metrics.total_videos_processed == 0
    assert metrics.fps_processing == 0.0


@pytest.mark.asyncio
async def test_frame_analyzer_extract_frames(sample_video: bytes):
    analyzer = FrameAnalyzer()
    frames = await analyzer.extract_frames(sample_video, count=3)
    assert len(frames) == 3
    assert frames[0]["timestamp_sec"] == 0
    assert frames[1]["timestamp_sec"] == 2


@pytest.mark.asyncio
async def test_frame_analyzer_analyze_frame(sample_video: bytes):
    analyzer = FrameAnalyzer()
    analysis = await analyzer.analyze_frame(sample_video, frame_index=0)
    assert "sharpness" in analysis
    assert "brightness" in analysis
    assert "motion_score" in analysis


@pytest.mark.asyncio
async def test_frame_analyzer_detect_changes(sample_video: bytes):
    analyzer = FrameAnalyzer()
    changes = await analyzer.detect_changes(sample_video, frame_indices=[0, 2, 4, 6])
    assert len(changes) == 3
    assert "change_score" in changes[0]


@pytest.mark.asyncio
async def test_frame_analyzer_get_frame_metadata(sample_video: bytes):
    analyzer = FrameAnalyzer()
    meta = await analyzer.get_frame_metadata(sample_video, frame_index=5)
    assert meta["codec"] == "h264"
    assert meta["key_frame"] is False


@pytest.mark.asyncio
async def test_frame_analyzer_compare_frames(sample_video: bytes):
    analyzer = FrameAnalyzer()
    comparison = await analyzer.compare_frames(sample_video, 0, 10)
    assert comparison["frame_a"] == 0
    assert comparison["frame_b"] == 10
    assert "difference_score" in comparison


@pytest.mark.asyncio
async def test_activity_detector_detect_activity(sample_video: bytes):
    detector = ActivityDetector()
    activities = await detector.detect_activity(sample_video)
    activity_types = {a["type"] for a in activities}
    assert "walking" in activity_types
    assert "assembling" in activity_types


@pytest.mark.asyncio
async def test_activity_detector_classify_activity(sample_video: bytes):
    detector = ActivityDetector()
    classification = await detector.classify_activity(sample_video, {"motion": 0.8})
    assert classification["primary_type"] == "operating"
    assert classification["primary_confidence"] > 0.8


@pytest.mark.asyncio
async def test_activity_detector_track_activity(sample_video: bytes):
    detector = ActivityDetector()
    tracking = await detector.track_activity(sample_video, "act_001")
    assert tracking.get("found", True)
    assert tracking["status"] == "in_progress"


@pytest.mark.asyncio
async def test_activity_detector_get_activity_timeline(sample_video: bytes):
    detector = ActivityDetector()
    timeline = await detector.get_activity_timeline(sample_video)
    assert len(timeline) == 6


@pytest.mark.asyncio
async def test_activity_detector_set_threshold(sample_video: bytes):
    detector = ActivityDetector()
    await detector.set_activity_threshold(0.95)
    activities = await detector.detect_activity(sample_video)
    for a in activities:
        assert a["confidence"] >= 0.95


@pytest.mark.asyncio
async def test_event_recognizer_recognize_event(sample_video: bytes):
    recognizer = EventRecognizer()
    events = await recognizer.recognize_event(sample_video)
    assert len(events) == 6
    assert events[0]["severity"] == "high"


@pytest.mark.asyncio
async def test_event_recognizer_classify_event(sample_video: bytes):
    recognizer = EventRecognizer()
    classification = await recognizer.classify_event(sample_video, {"motion_spike": True})
    assert "primary_event_type" in classification
    assert len(classification["all_possible_types"]) == 4


@pytest.mark.asyncio
async def test_event_recognizer_get_event_timestamp(sample_video: bytes):
    recognizer = EventRecognizer()
    ts = await recognizer.get_event_timestamp(sample_video, "evt_001")
    assert ts is not None
    assert ts["timestamp_sec"] == 15.2


@pytest.mark.asyncio
async def test_event_recognizer_get_event_details(sample_video: bytes):
    recognizer = EventRecognizer()
    details = await recognizer.get_event_details(sample_video, "evt_003")
    assert details is not None
    assert "root_cause_analysis" in details
    assert details["event_id"] == "evt_003"


@pytest.mark.asyncio
async def test_event_recognizer_get_event_details_not_found(sample_video: bytes):
    recognizer = EventRecognizer()
    details = await recognizer.get_event_details(sample_video, "nonexistent")
    assert details is None


@pytest.mark.asyncio
async def test_event_recognizer_subscribe_to_events(sample_video: bytes):
    recognizer = EventRecognizer()
    received: list[dict[str, Any]] = []

    def callback(event: dict[str, Any]) -> None:
        received.append(event)

    await recognizer.subscribe_to_events(callback)
    await recognizer.recognize_event(sample_video)
    assert len(received) == 6


@pytest.mark.asyncio
async def test_video_summarizer_generate_summary(sample_video: bytes):
    summarizer = VideoSummarizer()
    summary = await summarizer.generate_summary(sample_video)
    assert "summary_id" in summary
    assert "key_frames" in summary
    assert "timeline" in summary


@pytest.mark.asyncio
async def test_video_summarizer_extract_key_frames(sample_video: bytes):
    summarizer = VideoSummarizer()
    frames = await summarizer.extract_key_frames(sample_video, max_frames=3)
    assert len(frames) == 3
    assert frames[0]["frame_index"] == 0


@pytest.mark.asyncio
async def test_video_summarizer_generate_timeline(sample_video: bytes):
    summarizer = VideoSummarizer()
    timeline = await summarizer.generate_timeline(sample_video)
    assert len(timeline) == 13
    assert timeline[0]["type"] == "milestone"
    assert timeline[0]["label"] == "Start"


@pytest.mark.asyncio
async def test_video_summarizer_create_clip(sample_video: bytes):
    summarizer = VideoSummarizer()
    clip = await summarizer.create_clip(sample_video, 10.0, 30.0)
    assert clip["duration_sec"] == 20.0
    assert "clip_id" in clip


@pytest.mark.asyncio
async def test_video_summarizer_get_summary_text(sample_video: bytes):
    summarizer = VideoSummarizer()
    text = await summarizer.get_summary_text(sample_video)
    assert "Production Floor A" in text
    assert len(text) > 100
