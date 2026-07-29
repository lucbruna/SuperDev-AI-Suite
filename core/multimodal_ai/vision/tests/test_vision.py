from __future__ import annotations

from typing import Any

import pytest

from ..image_analyzer import ImageAnalyzer
from ..object_detection import ObjectDetector
from ..quality_inspection import QualityInspector
from ..image_understanding import ImageUnderstanding
from ..vision_engine import EngineConfig, EngineMetrics, EngineState, VisionEngine


async def _describe_image(self: ImageAnalyzer, _image_data: bytes | str) -> dict[str, Any]:
    return {
        "brief": "An industrial manufacturing floor with conveyor belts, robotic arms, and workers conducting quality inspection.",
        "detailed": (
            "The image shows a well-lit manufacturing facility with a central conveyor system. "
            "Two robotic arms are working on the assembly line while a worker in safety gear "
            "inspects circuit boards at the quality control station."
        ),
        "tags": ["manufacturing", "factory", "automation", "quality_control"],
        "sentiment": "neutral",
        "complexity": "high",
    }


ImageAnalyzer.describe_image = _describe_image


@pytest.fixture
def sample_image() -> bytes:
    return b"FAKE_IMAGE_DATA_" * 100


@pytest.mark.asyncio
async def test_vision_engine_initialize_and_stop():
    engine = VisionEngine()
    assert engine.state == EngineState.UNINITIALIZED
    await engine.initialize()
    assert engine.state == EngineState.READY
    await engine.stop()
    assert engine.state == EngineState.STOPPED


@pytest.mark.asyncio
async def test_vision_engine_process_image(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    result = await engine.process_image(sample_image)
    assert result["status"] == "processed"
    assert "analysis" in result
    assert "objects" in result
    assert engine.metrics.total_images_processed == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_vision_engine_analyze(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    result = await engine.analyze(sample_image)
    assert "description" in result
    assert "colors" in result
    assert "text" in result
    assert "classification" in result
    await engine.stop()


@pytest.mark.asyncio
async def test_vision_engine_detect_objects(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    objects = await engine.detect_objects(sample_image)
    assert len(objects) == 7
    assert objects[0]["type"] == "machine"
    assert engine.metrics.total_objects_detected == 7
    await engine.stop()


@pytest.mark.asyncio
async def test_vision_engine_inspect_quality(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    result = await engine.inspect_quality(sample_image)
    assert result["passed"] is True
    assert "defects" in result
    assert "measurements" in result
    assert engine.metrics.total_inspections == 1
    await engine.stop()


@pytest.mark.asyncio
async def test_vision_engine_get_metrics(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    await engine.process_image(sample_image)
    metrics = await engine.get_metrics()
    assert metrics.total_images_processed == 1
    assert metrics.average_processing_time_ms >= 0
    await engine.stop()


def test_engine_config_defaults():
    config = EngineConfig()
    assert config.device == "cpu"
    assert config.confidence_threshold == 0.5
    assert config.enable_gpu is False


def test_engine_metrics():
    metrics = EngineMetrics()
    assert metrics.total_images_processed == 0
    assert metrics.average_processing_time_ms == 0.0


@pytest.mark.asyncio
async def test_image_analyzer_analyze_image(sample_image: bytes):
    analyzer = ImageAnalyzer()
    result = await analyzer.analyze_image(sample_image)
    assert len(result["colors"]) == 5
    assert len(result["text"]) == 4
    assert "industrial_equipment" in result["classification"]["category"]


@pytest.mark.asyncio
async def test_image_analyzer_extract_colors(sample_image: bytes):
    analyzer = ImageAnalyzer()
    colors = await analyzer.extract_colors(sample_image)
    assert colors[0]["name"] == "crimson"
    assert colors[0]["hex"] == "#DC143C"


@pytest.mark.asyncio
async def test_image_analyzer_detect_text(sample_image: bytes):
    analyzer = ImageAnalyzer()
    text = await analyzer.detect_text(sample_image)
    assert text[0]["text"] == "WARNING"
    assert text[0]["confidence"] > 0.9


@pytest.mark.asyncio
async def test_image_analyzer_classify_image(sample_image: bytes):
    analyzer = ImageAnalyzer()
    classification = await analyzer.classify_image(sample_image)
    assert classification["confidence"] > 0.9


@pytest.mark.asyncio
async def test_image_analyzer_get_metadata(sample_image: bytes):
    analyzer = ImageAnalyzer()
    meta = await analyzer.get_metadata(sample_image)
    assert meta["format"] == "JPEG"
    assert meta["width"] == 1920
    assert meta["height"] == 1080


@pytest.mark.asyncio
async def test_object_detector_detect_objects(sample_image: bytes):
    detector = ObjectDetector()
    objects = await detector.detect_objects(sample_image)
    object_types = {o["type"] for o in objects}
    assert "machine" in object_types
    assert "person" in object_types
    assert "product" in object_types


@pytest.mark.asyncio
async def test_object_detector_count_objects(sample_image: bytes):
    detector = ObjectDetector()
    counts = await detector.count_objects(sample_image)
    assert counts["machine"] == 2
    assert counts["person"] == 1


@pytest.mark.asyncio
async def test_object_detector_track_object(sample_image: bytes):
    detector = ObjectDetector()
    result = await detector.track_object(sample_image, "machine_01")
    assert result["tracking_active"] is True
    assert "trajectory" in result


@pytest.mark.asyncio
async def test_object_detector_get_detection_map(sample_image: bytes):
    detector = ObjectDetector()
    dmap = await detector.get_detection_map(sample_image)
    assert dmap["width"] == 1920
    assert len(dmap["zones"]) == 3


@pytest.mark.asyncio
async def test_quality_inspector_inspect_product(sample_image: bytes):
    inspector = QualityInspector()
    result = await inspector.inspect_product(sample_image)
    assert result["passed"] is True
    assert result["overall_score"] > 90


@pytest.mark.asyncio
async def test_quality_inspector_detect_defects(sample_image: bytes):
    inspector = QualityInspector()
    defects = await inspector.detect_defects(sample_image)
    assert len(defects) == 2
    assert defects[0]["passes"] is True


@pytest.mark.asyncio
async def test_quality_inspector_measure_dimensions(sample_image: bytes):
    inspector = QualityInspector()
    dims = await inspector.measure_dimensions(sample_image)
    assert 140 < dims["width_mm"] < 160
    assert dims["measurement_confidence"] > 0.9


@pytest.mark.asyncio
async def test_quality_inspector_compare_to_standard(sample_image: bytes):
    inspector = QualityInspector()
    comparison = await inspector.compare_to_standard(sample_image)
    assert "deviations" in comparison
    assert "within_tolerance" in comparison


@pytest.mark.asyncio
async def test_quality_inspector_generate_report(sample_image: bytes):
    inspector = QualityInspector()
    report = await inspector.generate_inspection_report(sample_image)
    assert "report_id" in report
    assert len(report["recommendations"]) == 2


@pytest.mark.asyncio
async def test_image_understanding_understand_scene(sample_image: bytes):
    understanding = ImageUnderstanding()
    scene = await understanding.understand_scene(sample_image)
    assert scene["scene_type"] == "industrial_manufacturing"
    assert scene["confidence"] > 0.9


@pytest.mark.asyncio
async def test_image_understanding_describe_image(sample_image: bytes):
    understanding = ImageUnderstanding()
    desc = await understanding.describe_image(sample_image)
    assert "brief" in desc
    assert "detailed" in desc
    assert "tags" in desc


@pytest.mark.asyncio
async def test_image_understanding_answer_about_image(sample_image: bytes):
    understanding = ImageUnderstanding()
    answer = await understanding.answer_about_image(sample_image, "how many machines?")
    assert answer["confidence"] > 0.9


@pytest.mark.asyncio
async def test_image_understanding_extract_information(sample_image: bytes):
    understanding = ImageUnderstanding()
    info = await understanding.extract_information(sample_image, fields=["barcodes", "signage"])
    assert "barcodes" in info
    assert "signage" in info
    assert "faces" not in info


@pytest.mark.asyncio
async def test_image_understanding_identify_relationships(sample_image: bytes):
    understanding = ImageUnderstanding()
    rels = await understanding.identify_relationships(sample_image)
    assert len(rels) == 5
    assert rels[0]["predicate"] == "transports"


@pytest.mark.asyncio
async def test_vision_engine_process_image_with_options(sample_image: bytes):
    engine = VisionEngine()
    await engine.initialize()
    opts = {"detect_objects": True, "inspect_quality": True}
    result = await engine.process_image(sample_image, options=opts)
    assert result["status"] == "processed"
    assert "quality" in result
    await engine.stop()
