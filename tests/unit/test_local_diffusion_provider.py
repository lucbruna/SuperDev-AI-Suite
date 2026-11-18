from __future__ import annotations

import base64
from io import BytesIO

from PIL import Image

from modules.ai_video_studio.ai_image_generator.providers import local_diffusion


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (8, 8), (120, 30, 200)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_text_to_image_uses_local_diffusion_api_and_saves_png(monkeypatch, tmp_path):
    output = tmp_path / "generated.png"
    captured = {}
    monkeypatch.setenv("DARKSTUDIO_IMAGE_API_URL", "http://127.0.0.1:7860")
    monkeypatch.setattr(local_diffusion, "unique_filename", lambda *_args: output)

    def fake_post(url, payload, timeout):
        captured.update(url=url, payload=payload, timeout=timeout)
        return {"images": [base64.b64encode(_png_bytes()).decode("ascii")]}
    monkeypatch.setattr(local_diffusion, "_post_json", fake_post)

    result = local_diffusion.generate_scene_image(
        "A felt-clay forest", negative_prompt="text", width=512, height=512, steps=12,
    )
    assert captured["url"].endswith("/sdapi/v1/txt2img")
    assert captured["payload"]["prompt"] == "A felt-clay forest"
    assert captured["payload"]["steps"] == 12
    assert output.read_bytes().startswith(b"\\x89PNG")
    assert result["provider"] == "automatic1111_compatible"


def test_image_to_image_sends_source_and_edit_prompt(monkeypatch, tmp_path):
    source = tmp_path / "source.png"
    source.write_bytes(b"source-image")
    output = tmp_path / "edited.png"
    captured = {}
    monkeypatch.setenv("DARKSTUDIO_IMAGE_API_URL", "http://localhost:7860")
    monkeypatch.setattr(local_diffusion, "unique_filename", lambda *_args: output)

    def fake_post(url, payload, timeout):
        captured.update(url=url, payload=payload)
        return {"images": [base64.b64encode(_png_bytes()).decode("ascii")]}
    monkeypatch.setattr(local_diffusion, "_post_json", fake_post)

    result = local_diffusion.edit_image(source, "Change the sky to sunset", denoising_strength=0.3)
    assert captured["url"].endswith("/sdapi/v1/img2img")
    assert captured["payload"]["prompt"] == "Change the sky to sunset"
    assert captured["payload"]["denoising_strength"] == 0.3
    assert base64.b64decode(captured["payload"]["init_images"][0]) == b"source-image"
    assert result["operation"] == "image_to_image"


def test_image_to_image_rejects_missing_source(tmp_path):
    import pytest

    with pytest.raises(ValueError, match="existing PNG"):
        local_diffusion.edit_image(tmp_path / "missing.png", "Change the scene")


def test_fit_image_dimensions_preserves_landscape_and_portrait_aspect_ratio():
    assert local_diffusion.fit_image_dimensions(1920, 1080) == (1024, 576)
    assert local_diffusion.fit_image_dimensions(720, 1280) == (576, 1024)
    assert local_diffusion.fit_image_dimensions(640, 360) == (640, 360)
