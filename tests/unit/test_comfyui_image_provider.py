from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from modules.ai_video_studio.ai_image_generator.providers.comfyui_image_provider import (
    ComfyUIImageProvider,
)
from modules.ai_video_studio.core.exceptions import ValidationError


def _provider(tmp_path: Path, mapping: dict | None = None) -> ComfyUIImageProvider:
    workflow = tmp_path / "image-workflow.json"
    workflow.write_text(json.dumps({
        "10": {"inputs": {"image": "mia-old.png"}},
        "11": {"inputs": {"image": "leo-old.png"}},
        "20": {"inputs": {"text": "old prompt"}},
        "21": {"inputs": {"text": "old negative"}},
    }), encoding="utf-8")
    return ComfyUIImageProvider(
        base_url="http://127.0.0.1:8188",
        workflow_path=workflow,
        mapping=mapping or {
            "characters": {
                "mia": {"node_id": "10", "input": "image"},
                "leo": {"node_id": "11", "input": "image"},
            },
            "prompt": {"node_id": "20", "input": "text"},
            "negative_prompt": {"node_id": "21", "input": "text"},
        },
        timeout=5,
        poll_interval=0.2,
    )


def test_comfyui_image_mapping_assigns_each_character_to_distinct_load_image_input(tmp_path):
    provider = _provider(tmp_path)
    workflow = json.loads(provider.workflow_path.read_text(encoding="utf-8"))
    provider._apply_mapping(
        workflow,
        {
            "mia": {"name": "mia-ref.png", "subfolder": "input"},
            "leo": {"name": "leo-ref.png"},
        },
        "Mia and Leo in one felt-clay scene",
        "blurry",
    )
    assert workflow["10"]["inputs"]["image"] == "input/mia-ref.png"
    assert workflow["11"]["inputs"]["image"] == "leo-ref.png"
    assert workflow["20"]["inputs"]["text"] == "Mia and Leo in one felt-clay scene"
    assert workflow["21"]["inputs"]["text"] == "blurry"


def test_comfyui_image_mapping_rejects_reference_collision_with_prompt(tmp_path):
    provider = _provider(tmp_path, {
        "characters": {"mia": {"node_id": "20", "input": "text"}},
        "prompt": {"node_id": "20", "input": "text"},
    })
    workflow = {"20": {"inputs": {"text": "old"}}}
    with pytest.raises(ValidationError, match="distinct input"):
        provider._apply_mapping(workflow, {"mia": {"name": "mia.png"}}, "prompt", "")


def test_comfyui_image_output_rejects_video_only_workflow():
    with pytest.raises(RuntimeError, match="without a still-image output"):
        ComfyUIImageProvider._find_image_output({
            "outputs": {"9": {"videos": [{"filename": "clip.mp4"}]}}
        })


def test_comfyui_image_output_selects_still_image():
    result = ComfyUIImageProvider._find_image_output({
        "outputs": {"9": {"images": [
            {"filename": "preview.png", "subfolder": "output", "type": "output"}
        ]}}
    })
    assert result["filename"] == "preview.png"
    assert result["node_id"] == "9"


def test_comfyui_image_generate_uploads_all_references_and_saves_valid_image(tmp_path, monkeypatch):
    provider = _provider(tmp_path)
    mia = tmp_path / "mia.png"
    leo = tmp_path / "leo.png"
    Image.new("RGB", (8, 8), "red").save(mia)
    Image.new("RGB", (8, 8), "blue").save(leo)
    uploaded: list[str] = []
    monkeypatch.setattr(
        provider, "_upload_image",
        lambda path: uploaded.append(Path(path).name) or {"name": Path(path).name},
    )
    submitted: dict = {}

    def fake_request(method, path, payload=None):
        if path == "/prompt":
            submitted["workflow"] = payload["prompt"]
            return {"prompt_id": "image-job-1"}
        return {}

    monkeypatch.setattr(provider, "_json_request", fake_request)
    monkeypatch.setattr(provider, "_wait_for_history", lambda _prompt_id: {
        "outputs": {"30": {"images": [{"filename": "render.png", "type": "output"}]}}
    })

    def fake_download(_entry, target):
        Image.new("RGB", (16, 16), "green").save(target)

    monkeypatch.setattr(provider, "_download_output", fake_download)
    output = tmp_path / "generated.png"
    result = provider.generate(
        prompt="Keep Mia and Leo visually consistent",
        references_by_character={"mia": mia, "leo": leo},
        output_path=output,
        negative_prompt="identity drift",
    )
    assert uploaded == ["mia.png", "leo.png"]
    assert submitted["workflow"]["10"]["inputs"]["image"] == "mia.png"
    assert submitted["workflow"]["11"]["inputs"]["image"] == "leo.png"
    assert submitted["workflow"]["20"]["inputs"]["text"] == "Keep Mia and Leo visually consistent"
    assert output.is_file() and output.stat().st_size > 0
    assert result["provider"] == "comfyui_image_workflow"
    assert result["reference_count"] == 2
    assert result["prompt_id"] == "image-job-1"


def test_comfyui_image_generate_rejects_reference_set_mismatch(tmp_path):
    provider = _provider(tmp_path)
    with pytest.raises(ValidationError, match="exactly match"):
        provider.generate(
            prompt="A scene",
            references_by_character={"mia": tmp_path / "mia.png"},
            output_path=tmp_path / "out.png",
        )
