from __future__ import annotations

import json

import pytest

from modules.ai_video_studio.ai_video_generator.image_to_video.comfyui_video_provider import (
    ComfyUIVideoProvider,
)
from modules.ai_video_studio.core.exceptions import ValidationError


def test_comfyui_mapping_updates_only_configured_inputs():
    workflow = {
        "10": {"inputs": {"image": "old.png"}},
        "20": {"inputs": {"text": "old prompt"}},
        "30": {"inputs": {"text": "old negative"}},
    }
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        workflow_path="unused.json",
        mapping={
            "image": {"node_id": "10", "input": "image"},
            "prompt": {"node_id": "20", "input": "text"},
            "negative_prompt": {"node_id": "30", "input": "text"},
        },
    )
    provider._apply_mapping(
        workflow,
        {"name": "uploaded.png"},
        "Animate the scene",
        "blurry, artifacts",
    )
    assert workflow["10"]["inputs"]["image"] == "uploaded.png"
    assert workflow["20"]["inputs"]["text"] == "Animate the scene"
    assert workflow["30"]["inputs"]["text"] == "blurry, artifacts"


def test_comfyui_mapping_rejects_unknown_node_or_input():
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        workflow_path="unused.json",
        mapping={},
    )
    with pytest.raises(ValidationError, match="not found"):
        provider._set_node_input({"1": {"inputs": {}}}, {"node_id": "1", "input": "image"}, "x")


def test_comfyui_video_output_requires_mp4_entry():
    history = {"outputs": {"42": {"videos": [
        {"filename": "clip.mp4", "subfolder": "darkstudio", "type": "output"}
    ]}}}
    result = ComfyUIVideoProvider._find_video_output(history)
    assert result["filename"] == "clip.mp4"
    assert result["node_id"] == "42"
    with pytest.raises(RuntimeError, match="produced no MP4"):
        ComfyUIVideoProvider._find_video_output({"outputs": {"42": {"images": [{"filename": "still.png"}]}}})


def test_comfyui_mapping_environment_must_be_json(monkeypatch):
    monkeypatch.setenv("DARKSTUDIO_COMFYUI_MAPPING", "{broken")
    with pytest.raises(ValidationError, match="valid JSON"):
        ComfyUIVideoProvider(base_url="http://127.0.0.1:8188")
