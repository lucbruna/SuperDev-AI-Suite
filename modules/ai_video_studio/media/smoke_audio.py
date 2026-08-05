"""Volume 4 smoke test — exercises every audio subsystem end-to-end.

Each check produces a REAL file (WAV/MP3/MP4/SRT/JSON) and asserts it is
non-empty. Run with: ``python -m modules.ai_video_studio.media.smoke_audio``
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CHECKS = []


def check(name: str, result: dict) -> None:
    ok = bool(result.get("ok"))
    size = result.get("bytes", 0)
    extra = result.get("extra", "")
    CHECKS.append((name, ok, size, extra))
    print(f"{'PASS' if ok else 'FAIL'}  {name:32s} {size:>8d}B  {extra}")


def run() -> int:
    from modules.ai_video_studio.media import dsp

    # ── 1. DSP sanity ────────────────────────────────────────────
    tone = dsp.sine(440.0, 0.5)
    filtered = dsp.one_pole_lp(tone, 1000.0)
    f0 = dsp.f0_autocorr(dsp.sine(220.0, 0.5))
    check("dsp primitives", {"ok": len(tone) > 0 and len(filtered) > 0 and 200 < f0 < 240,
                             "bytes": len(tone), "extra": f"f0={f0:.1f}Hz"})

    # ── 2. Voice studio ──────────────────────────────────────────
    from modules.ai_video_studio.ai_voice_studio import get_voice_engine

    voice = get_voice_engine()
    synth = voice.synthesize("The AI voice studio speaks with real synthesized audio.",
                             voice_id="female_warm", language="en", use_cache=False)
    check("voice studio TTS", {"ok": synth["bytes"] > 1000, "bytes": synth["bytes"],
                               "extra": f"engine={synth['engine']} {synth['duration']}s"})
    check("voice catalog", {"ok": len(voice.list_voices()) >= 30,
                            "bytes": len(voice.list_voices()), "extra": f"{len(voice.list_voices())} voices"})

    # ── 3. Voice clone ───────────────────────────────────────────
    from modules.ai_video_studio.ai_voice_clone import get_clone_engine

    clone_engine = get_clone_engine()
    profile = clone_engine.create_profile([synth["output_path"]], clone_id="smoke_clone")
    cloned = clone_engine.clone("The clone speaks with the reference voice.", "smoke_clone", language="en")
    check("voice clone", {"ok": cloned["bytes"] > 1000, "bytes": cloned["bytes"],
                          "extra": f"pitch_shifted={cloned['pitch_shifted']} f0_target={profile['analysis'].get('f0_mean', 0):.0f}"})
    clone_engine.delete_clone("smoke_clone")

    # ── 4. Translation ───────────────────────────────────────────
    from modules.ai_video_studio.ai_translation import get_translation_engine, detect_language

    detected = detect_language("Hello, this is a test message in English.")
    translation = get_translation_engine().translate(
        "Hello, welcome to the studio.", "pt", source="en", use_llm=False,
    )
    check("translation (fallback)", {"ok": detected == "en" and translation["engine"] in ("fallback", "memory"),
                                     "bytes": len(translation["text"]),
                                     "extra": f"detected={detected} -> {translation['text'][:30]}"})

    # ── 5. Subtitles ─────────────────────────────────────────────
    from modules.ai_video_studio.ai_subtitles import get_subtitle_engine

    subs = get_subtitle_engine()
    for fmt in ("srt", "vtt", "ass"):
        result = subs.generate("This is the first subtitle line. And this is the second one.", format=fmt)
        check(f"subtitle {fmt}", {"ok": result["bytes"] > 50, "bytes": result["bytes"],
                                  "extra": f"{result['cues']} cues"})
    vad = subs.generate(media_path=synth["output_path"], format="srt")
    check("subtitle VAD", {"ok": vad["bytes"] > 0, "bytes": vad["bytes"],
                           "extra": f"engine={vad['engine']} cues={vad['cues']}"})

    # ── 6. Lip sync ──────────────────────────────────────────────
    from modules.ai_video_studio.ai_lip_sync import get_lip_sync_engine

    lip = get_lip_sync_engine().generate("Hello there, this is lip sync working.",
                                         duration=2.0, fps=15)
    check("lip sync MP4", {"ok": lip["output_bytes"] > 100, "bytes": lip["output_bytes"],
                           "extra": f"{lip['frames']} frames @ {lip['fps']}fps"})

    # ── 7. Music generator ───────────────────────────────────────
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    music = get_music_engine().generate("lofi", duration=8.0)
    check("music lofi", {"ok": music["bytes"] > 10000, "bytes": music["bytes"],
                         "extra": f"{music['duration']}s bpm={music['bpm']} tracks={music['instruments']}"})

    # ── 8. Sound effects ─────────────────────────────────────────
    from modules.ai_video_studio.ai_sound_effects import get_effects_engine

    effects = get_effects_engine()
    for name in ("rain", "thunder", "ui"):
        result = effects.generate(name)
        check(f"sfx {name}", {"ok": result["bytes"] > 500, "bytes": result["bytes"],
                              "extra": f"{result['duration']}s"})

    # ── 9. Audio mixer + mastering ───────────────────────────────
    from modules.ai_video_studio.ai_audio_mixer import get_mixer_engine, export_audio

    t1 = dsp.sine(330.0, 3.0) * 0.5
    t2 = dsp.sine(494.0, 3.0) * 0.5
    mix = get_mixer_engine().mix([{"samples": t1, "gain": 0.8, "pan": -0.3, "eq": [(3000.0, 2.0, 1.0)]},
                                  {"samples": t2, "gain": 0.7, "pan": 0.3}],
                                 master_preset="warm")
    check("mixer", {"ok": mix["bytes"] > 5000, "bytes": mix["bytes"],
                    "extra": f"loudness={mix['loudness']}"})
    exported = export_audio.export(mix["samples"], str(Path(mix["output_path"]).with_suffix(".mp3")))
    check("export mp3", {"ok": exported["bytes"] > 1000, "bytes": exported["bytes"], "extra": "mp3"})

    # ── 10. Dubbing pipeline (fast, deterministic) ───────────────
    from modules.ai_video_studio.ai_dubbing import get_dubbing_engine

    small_video = Path(mix["output_path"]).parent.parent / "videos" / "_smoke_dub_src.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=navy:s=160x90:d=3",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(small_video)],
        capture_output=True, text=True, timeout=120,
    )
    dub = get_dubbing_engine().dub(
        str(small_video), "pt",
        source_transcript="Hello world. This is a dubbing test.",
        source_language="en", use_llm=False,
    )
    check("dubbing pipeline", {"ok": Path(dub["output_path"]).stat().st_size > 500,
                               "bytes": Path(dub["output_path"]).stat().st_size,
                               "extra": f"muxed={dub['muxed']} lines={dub['lines']}"})

    failed = [c for c in CHECKS if not c[1]]
    print(f"\n{'=' * 60}\nTotal: {len(CHECKS)} checks, {len(CHECKS) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
