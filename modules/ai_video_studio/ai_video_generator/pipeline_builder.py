"""Pipeline builder — assemble a generation pipeline from stages."""
from __future__ import annotations

class PipelineBuilder:
    """Builds ordered stage lists for a given generation mode."""

    _STAGES: dict[str, list[str]] = {
        "text_to_video": [
            "prompt_parse",
            "scene_build",
            "frame_generate",
            "interpolate",
            "render",
            "quality_check",
        ],
        "image_to_video": [
            "image_parse",
            "depth_estimate",
            "motion_predict",
            "frame_animate",
            "render",
            "quality_check",
        ],
        "video_to_video": [
            "video_parse",
            "style_transfer",
            "frame_enhance",
            "render",
            "quality_check",
        ],
    }

    def __init__(self) -> None:
        self._stages = {mode: list(stages) for mode, stages in self._STAGES.items()}

    def build(self, mode: str) -> list[str]:
        stages = self._stages.get(mode)
        if stages is None:
            raise ValueError(f"Unknown mode '{mode}'")
        return list(stages)

    def add_stage(self, mode: str, stage: str, *, before: str | None = None) -> None:
        stages = self._stages.setdefault(mode, [])
        if before is not None:
            idx = stages.index(before)
            stages.insert(idx, stage)
        else:
            stages.append(stage)

    def modes(self) -> list[str]:
        return list(self._stages.keys())


_pipeline_builder: PipelineBuilder | None = None


def get_pipeline_builder() -> PipelineBuilder:
    global _pipeline_builder
    if _pipeline_builder is None:
        _pipeline_builder = PipelineBuilder()
    return _pipeline_builder
