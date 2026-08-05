"""End-to-end smoke test — verifies every subsystem produces real files.

Run:  python -m modules.ai_video_studio.media.smoke_e2e
"""
from __future__ import annotations

import sys
from pathlib import Path


def _check(step: str, result: dict) -> None:
    path = result.get("output_path")
    ok = bool(path) and Path(path).exists() and Path(path).stat().st_size > 0
    status = "OK " if ok else "FAIL"
    print(f"[{status}] {step}: {path or result}")
    if not ok:
        sys.exit(1)


def main() -> None:
    # 1. Image generator — all 14 styles.
    from modules.ai_video_studio.ai_image_generator import get_image_engine

    engine = get_image_engine()
    for style in ["realistic", "anime", "cinematic", "fantasy", "architecture",
                  "agriculture", "medical", "ecommerce", "product", "logo",
                  "banner", "thumbnail", "icon", "infographic"]:
        rec = engine.generate("a beautiful scene", style=style)
        _check(f"image/{style}", rec["result"])

    # 2. Text to video.
    from modules.ai_video_studio.ai_video_generator import get_video_engine

    video_engine = get_video_engine()
    # ``llm_timeout`` is kept small so the smoke test is fast: it verifies the
    # deterministic fallback. The Ollama path is validated separately.
    ttv = video_engine.generate("a cinematic city at night", mode="text_to_video",
                                params={"duration": 3.0, "num_scenes": 2, "llm_timeout": 3.0})
    _check("text_to_video", ttv["output"])

    # 2b. Text to video with per-scene AI narration (voiceover=True).
    # Verifies the real TTS chain runs and the voiceover track (one clip per
    # scene, placed at each scene's timeline offset) is muxed into the video.
    from modules.ai_video_studio.media.video import ffmpeg_available

    if ffmpeg_available():
        ttv_voiced = video_engine.generate(
            "a calm ocean sunset", mode="text_to_video",
            params={"duration": 4.0, "num_scenes": 2, "llm_timeout": 3.0, "voiceover": True},
        )
        voiced_out = ttv_voiced["output"]
        _check("text_to_video_voiced", voiced_out)
        voice = voiced_out.get("voiceover") or {}
        if not voice.get("muxed"):
            print(f"[FAIL] text_to_video_voiced: narration not muxed ({voice.get('reason')})")
            sys.exit(1)
        clips = voice.get("clips") or []
        voiced_clips = [c for c in clips if c.get("audio_path")]
        offsets = [c.get("start") for c in voiced_clips]
        if not voiced_clips or not all(o is not None for o in offsets):
            print("[FAIL] text_to_video_voiced: no per-scene clips with offsets")
            sys.exit(1)
        print(f"      voiceover: muxed per-scene, clips={len(voiced_clips)} offsets={offsets}")
    else:
        print("[SKIP] text_to_video_voiced: ffmpeg unavailable (narration mux not tested)")

    # 3. Image to video.
    itv = video_engine.generate("image:demo_sunset", mode="image_to_video",
                                params={"duration": 2.0})
    _check("image_to_video", itv["output"])

    # 4. Video to video (style transfer on the generated clip).
    from modules.ai_video_studio.ai_video_generator import get_task_dispatcher

    vtv = get_task_dispatcher().dispatch({
        "id": "vtv_1", "mode": "video_to_video",
        "prompt": "", "params": {"operation": "style_transfer", "style": "noir",
                                 "video_ref": ttv["output"]["output_path"]},
    })
    _check("video_to_video", vtv)

    # 5. Animation.
    from modules.ai_video_studio.ai_animation import get_animation_engine

    anim = get_animation_engine().animate(character="hero", action="walk", duration=2.0)
    _check("animation/walk", anim)

    # 6. Camera.
    from modules.ai_video_studio.ai_camera import get_camera_engine

    cam = get_camera_engine()
    cam.create("main")
    _check("camera/orbit", cam.render_demo(move="orbit", duration=2.0))

    # 7. Physics.
    from modules.ai_video_studio.ai_physics import get_physics_engine

    _check("physics", get_physics_engine().render_simulation(duration=2.0))

    # 8. Asset library.
    from modules.ai_video_studio.asset_library import AssetManager

    manager = AssetManager()
    _check("asset/texture", manager.generate_placeholder(name="grass", kind="texture"))
    _check("asset/sound", manager.generate_placeholder(name="chord", kind="music"))

    print("\nALL SUBSYSTEMS PRODUCE REAL FILES: PASS")


if __name__ == "__main__":
    main()
