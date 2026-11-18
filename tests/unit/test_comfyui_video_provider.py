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


def test_comfyui_generate_uploads_image_and_downloads_mp4(tmp_path, monkeypatch):
    image = tmp_path / "reference.png"
    image.write_bytes(b"fake-image")
    workflow = tmp_path / "workflow.json"
    workflow.write_text(json.dumps({
        "1": {"inputs": {"image": "input.png"}},
        "2": {"inputs": {"text": "prompt"}},
    }), encoding="utf-8")
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        workflow_path=workflow,
        mapping={
            "image": {"node_id": "1", "input": "image"},
            "prompt": {"node_id": "2", "input": "text"},
        },
        timeout=10,
        poll_interval=0.2,
    )
    monkeypatch.setattr(provider, "_upload_image", lambda _path: {"name": "uploaded.png"})
    submitted = {}

    def fake_json(method, path, payload=None):
        submitted["workflow"] = payload["prompt"] if payload else None
        if path == "/prompt":
            return {"prompt_id": "job-123"}
        return {}

    monkeypatch.setattr(provider, "_json_request", fake_json)
    monkeypatch.setattr(provider, "_wait_for_history", lambda _prompt_id: {
        "outputs": {"9": {"videos": [{"filename": "result.mp4", "type": "output"}]}}
    })

    def fake_download(_entry, target):
        target.write_bytes(b"0000ftypisom0000")

    monkeypatch.setattr(provider, "_download_output", fake_download)
    output = tmp_path / "final.mp4"
    result = provider.generate(
        image_path=image,
        prompt="The camera circles the subject",
        output_path=output,
    )
    assert result["prompt_id"] == "job-123"
    assert result["provider"] == "comfyui_workflow"
    assert output.read_bytes()[4:8] == b"ftyp"
    assert submitted["workflow"]["1"]["inputs"]["image"] == "uploaded.png"
    assert submitted["workflow"]["2"]["inputs"]["text"] == "The camera circles the subject"
