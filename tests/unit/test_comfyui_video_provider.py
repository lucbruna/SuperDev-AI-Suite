from __future__ import annotations

import json
from pathlib import Path

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



def test_comfyui_multi_character_mapping_assigns_distinct_uploaded_references():
    workflow = {
        "10": {"inputs": {"image": "old-mia.png"}},
        "11": {"inputs": {"image": "old-leo.png"}},
        "20": {"inputs": {"text": "old prompt"}},
    }
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        mapping={
            "characters": {
                "mia": {"node_id": "10", "input": "image"},
                "leo": {"node_id": "11", "input": "image"},
            },
            "prompt": {"node_id": "20", "input": "text"},
        },
    )
    provider._apply_character_reference_mapping(
        workflow,
        {
            "mia": {"name": "mia-approved.png", "subfolder": "input"},
            "leo": {"name": "leo-approved.png"},
        },
        "Mia and Leo in the same felt-clay scene",
    )
    assert workflow["10"]["inputs"]["image"] == "input/mia-approved.png"
    assert workflow["11"]["inputs"]["image"] == "leo-approved.png"
    assert workflow["20"]["inputs"]["text"] == "Mia and Leo in the same felt-clay scene"


def test_comfyui_multi_character_mapping_rejects_missing_or_shared_inputs():
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        mapping={
            "characters": {
                "mia": {"node_id": "10", "input": "image"},
                "leo": {"node_id": "10", "input": "image"},
            },
            "prompt": {"node_id": "20", "input": "text"},
        },
    )
    workflow = {
        "10": {"inputs": {"image": "old.png"}},
        "20": {"inputs": {"text": "old"}},
    }
    with pytest.raises(ValidationError, match="mismatch"):
        provider._apply_character_reference_mapping(
            workflow, {"mia": {"name": "mia.png"}}, "prompt"
        )
    with pytest.raises(ValidationError, match="distinct"):
        provider._apply_character_reference_mapping(
            workflow,
            {"mia": {"name": "mia.png"}, "leo": {"name": "leo.png"}},
            "prompt",
        )


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


def test_image_to_video_api_exposes_explicit_comfyui_opt_in():
    from modules.ai_video_studio.api.routes.generation import ImageToVideoRequest

    default = ImageToVideoRequest(image_ref="scene.png")
    assert default.motion_provider == "camera"
    request = ImageToVideoRequest(
        image_ref="scene.png",
        duration_seconds=10,
        motion_provider="comfyui",
        motion_prompt="Slow orbit, preserve the subject",
    )
    assert request.motion_provider == "comfyui"
    assert request.duration_seconds == 10
    with pytest.raises(Exception):
        ImageToVideoRequest(image_ref="scene.png", motion_provider="wan_direct")


def test_image_to_video_engine_conforms_comfyui_output_to_exact_clip(tmp_path, monkeypatch):
    from types import SimpleNamespace

    from modules.ai_video_studio.ai_video_generator.image_to_video import (
        image_to_video_engine as engine_module,
    )
    from modules.ai_video_studio.ai_video_generator.image_to_video.comfyui_video_provider import (
        ComfyUIVideoProvider as Provider,
    )

    image = tmp_path / "source.png"
    image.write_bytes(b"image")
    monkeypatch.setattr(engine_module.shutil, "which", lambda _name: "/usr/bin/ffmpeg")
    monkeypatch.setattr(engine_module, "get_subsystem_dir", lambda _kind: tmp_path)
    monkeypatch.setattr(engine_module, "unique_filename", lambda *_args: tmp_path / "final.mp4")

    def fake_generate(self, *, image_path, prompt, negative_prompt, output_path):
        output_path.write_bytes(b"0000ftypisom0000")
        return {"provider": "comfyui_workflow", "prompt_id": "abc", "video_metadata": {"filename": "wan.mp4"}}

    monkeypatch.setattr(Provider, "generate", fake_generate)

    def fake_ffmpeg(command, **_kwargs):
        Path(command[-1]).write_bytes(b"normalized-mp4")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(engine_module.subprocess, "run", fake_ffmpeg)
    result = engine_module.ImageToVideoEngine().generate({
        "id": "comfyui-engine-test",
        "prompt": str(image),
        "params": {
            "motion_provider": "comfyui",
            "motion_prompt": "Slow orbit",
            "duration": 10,
            "fps": 24,
            "width": 1080,
            "height": 1920,
        },
    })
    assert result["provider"] == "comfyui_workflow"
    assert result["frames"] == 240
    assert result["duration"] == 10
    assert result["encode_engine"] == "ffmpeg_comfyui_normalized"
    assert (tmp_path / "final.mp4").read_bytes() == b"normalized-mp4"


def test_comfyui_engine_rejects_odd_h264_dimensions(tmp_path):
    from modules.ai_video_studio.ai_video_generator.image_to_video.image_to_video_engine import (
        ImageToVideoEngine,
    )

    image = tmp_path / "source.png"
    image.write_bytes(b"image")
    with pytest.raises(ValidationError, match="even width and height"):
        ImageToVideoEngine().generate({
            "id": "odd-dimensions",
            "prompt": str(image),
            "params": {"motion_provider": "comfyui", "width": 641, "height": 480},
        })



def test_comfyui_multi_character_mapping_rejects_prompt_input_collision():
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        mapping={
            "characters": {"mia": {"node_id": "10", "input": "image"}},
            "prompt": {"node_id": "10", "input": "image"},
        },
    )
    workflow = {"10": {"inputs": {"image": "old.png"}}}
    with pytest.raises(ValidationError, match="separate from prompt inputs"):
        provider._apply_character_reference_mapping(
            workflow, {"mia": {"name": "mia.png"}}, "Mia in the forest"
        )


def test_comfyui_multi_character_mapping_rejects_blank_character_ids():
    provider = ComfyUIVideoProvider(
        base_url="http://127.0.0.1:8188",
        mapping={
            "characters": {"": {"node_id": "10", "input": "image"}},
            "prompt": {"node_id": "20", "input": "text"},
        },
    )
    workflow = {
        "10": {"inputs": {"image": "old.png"}},
        "20": {"inputs": {"text": "old"}},
    }
    with pytest.raises(ValidationError, match="non-empty strings"):
        provider._apply_character_reference_mapping(
            workflow, {"": {"name": "unknown.png"}}, "prompt"
        )
