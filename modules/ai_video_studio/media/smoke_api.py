"""API smoke test — exercise the real generation routes via TestClient.

Run:  python -m modules.ai_video_studio.media.smoke_api
"""
from __future__ import annotations

import sys


def _check(label: str, ok: bool, detail: str = "") -> None:
    print(f"[{'OK ' if ok else 'FAIL'}] {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def main() -> None:
    from fastapi.testclient import TestClient

    from modules.ai_video_studio.api.main import create_app

    app = create_app()
    client = TestClient(app)

    # 1. Image generation.
    r = client.post("/api/v1/video-studio/images/generate", json={
        "prompt": "a red sports car", "style": "realistic", "width": 256, "height": 256,
    })
    _check("images/generate", r.status_code == 200, f"status={r.status_code} {r.text[:120]}")
    image_data = r.json()["data"]
    _check("image has real file", bool(image_data.get("output_path")) and image_data.get("output_bytes", 0) > 0)
    image_url = image_data.get("download_url")
    _check("image download_url", bool(image_url))

    # 2. Download the generated image.
    r = client.get(image_url)
    _check("downloads/<kind>/<file> serves file", r.status_code == 200 and len(r.content) > 0, f"bytes={len(r.content)}")

    # 3. Animation.
    r = client.post("/api/v1/video-studio/animations/generate", json={
        "character": "hero", "action": "walk", "duration_seconds": 1.5, "fps": 12,
    })
    _check("animations/generate", r.status_code == 200, f"status={r.status_code} {r.text[:120]}")
    anim = r.json()["data"]
    _check("animation mp4 real", anim.get("output_bytes", 0) > 0, anim.get("output_path", ""))

    # 4. Physics.
    r = client.post("/api/v1/video-studio/physics/simulate", json={"duration_seconds": 1.5, "fps": 12})
    _check("physics/simulate", r.status_code == 200 and r.json()["data"].get("output_bytes", 0) > 0)

    # 5. Asset generation.
    r = client.post("/api/v1/video-studio/assets/generate", json={"name": "marble", "kind": "texture"})
    _check("assets/generate", r.status_code == 200 and r.json()["data"].get("output_bytes", 0) > 0)

    # 6. Video-to-video (auto-generates demo clip input, applies style transfer).
    r = client.post("/api/v1/video-studio/videos/video-to-video", json={
        "video_ref": "", "operation": "style_transfer", "style": "noir",
    })
    _check("videos/video-to-video", r.status_code == 200 and r.json()["data"].get("output_bytes", 0) > 0)

    # 7. Image-to-video (procedural scene fallback).
    r = client.post("/api/v1/video-studio/videos/image-to-video", json={
        "image_ref": "image:sunset", "duration_seconds": 1.5, "fps": 12,
    })
    _check("videos/image-to-video", r.status_code == 200 and r.json()["data"].get("output_bytes", 0) > 0)

    # 8. Path traversal guard on downloads.
    r = client.get("/api/v1/video-studio/downloads/../secret/evil.png")
    _check("downloads path-traversal blocked", r.status_code == 404)

    # 9. Video job flow (queued → poll status).
    r = client.post("/api/v1/video-studio/videos/generate", json={
        "project_id": "p1", "prompt": "a starry night", "duration_seconds": 2.0,
        "num_scenes": 2, "llm_timeout": 3.0,
    })
    _check("videos/generate queued", r.status_code == 202, f"status={r.status_code}")
    job_id = r.json()["job_id"]
    import time

    for _ in range(60):
        status = client.get(f"/api/v1/video-studio/videos/jobs/{job_id}").json()
        if status["status"] in ("completed", "failed"):
            break
        time.sleep(0.5)
    _check("videos/generate completes", status["status"] == "completed", f"status={status['status']} error={status.get('error')}")
    _check("video has download_url", bool(status.get("output_url")))

    print("\nALL API GENERATION ROUTES PRODUCE REAL FILES: PASS")


if __name__ == "__main__":
    main()
