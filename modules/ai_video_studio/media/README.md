# Media output toolkit — real media generation

This package turns the Volume 3 logic engines into producers of **real
files** using PIL, numpy and FFmpeg, with a local Ollama model for
AI-driven scene planning.

## Output directory

Everything lands under `<project>/modules/downloads/`:

| Folder        | Contents                                        |
|---------------|-------------------------------------------------|
| `images/`     | AI Image Generator PNGs (14 styles)             |
| `videos/`     | text-to-video / image-to-video / video-to-video MP4s |
| `animations/` | AI Animation Engine MP4s (skeleton render)      |
| `camera/`     | AI Camera Engine demo moves                     |
| `physics/`    | AI Physics Engine particle simulations          |
| `assets/`     | Asset Library generated textures/sounds         |

## Capabilities & fallbacks

- **LLM planning** — a local Ollama model (`mistral-nemo`, configured via
  `OLLAMA_BASE_URL`/`OLLAMA_MODEL`) plans scenes from a prompt. If Ollama is
  unreachable or times out, a deterministic planner produces valid scenes so
  generation never fails.
- **FFmpeg** — encodes real MP4s. If FFmpeg is missing, frames become an
  animated GIF via Pillow.
- **Audio** — real WAV synthesis (tone/chord/noise) with numpy.

## Quick check

```bash
python -m modules.ai_video_studio.media.smoke_e2e
```

Runs every subsystem end-to-end and verifies each produces a non-empty file.

## Voice narration (TTS)

`TextToVideoEngine` can add real AI voiceover to generated videos. Pass
`voiceover: true` in the job params:

```python
result = await TextToVideoEngine().generate_async({
    "prompt": "a cinematic sunset",
    "params": {"duration": 6.0, "voiceover": True, "voice_id": "aria"},
})
print(result["voiceover"]["tts_engine"])  # edge-tts | gtts | pyttsx3
```

* Narration text is built from the scene descriptions (capped at 800 chars).
* Voice pipeline: edge-tts -> gTTS -> pyttsx3 (offline), via `VoiceStudioService`.
* Fails soft: if TTS is unavailable the silent video is returned with a
  `voiceover.reason` explaining why.
* `generate_async()` is preferred in async contexts; the sync `generate()`
  bridge drives the async pipeline in a worker thread when a loop is running.

## Volume 4 — AI Voice / Audio Studio

All audio subsystems write **real files** under `modules/downloads/` (voice,
voice_clones, dubbing, lip_sync, music, effects, mix, subtitles). Shared DSP
primitives live in `media/dsp.py`.

### Voice studio (`ai_voice_studio`)
- Chained TTS: edge-tts → gTTS → pyttsx3 → **local formant synthesizer** (offline).
- 37+ narrator profiles; multilingual; expressive/emotion prosody; streaming;
  normalization (numbers, dates, currency, units, abbreviations); disk cache.
```python
from modules.ai_video_studio.ai_voice_studio import get_voice_engine
get_voice_engine().synthesize("Olá mundo", voice_id="francisca", language="pt")
```

### Voice clone (`ai_voice_clone`)
- Real analysis: f0 (autocorrelation), timbre, SNR, vibrato; speaker embeddings;
  similarity matching; prosodic cloning with phase-vocoder pitch shift.

### Translation (`ai_translation`)
- Real AI translation via local **Ollama** (verified: EN→PT works), glossary,
  terminology protection, translation memory; deterministic fallback.

### Subtitles (`ai_subtitles`)
- Real SRT/VTT/ASS exporters, reading-speed timing, VAD segmentation, whisper
  when installed, ASS styles + animation tags.

### Dubbing (`ai_dubbing`)
- Full pipeline: extract audio → transcribe/transcript → translate (Ollama) →
  TTS per line → align → mix → mux. Produces a real dubbed MP4.

### Lip sync (`ai_lip_sync`)
- phoneme → viseme → per-frame timeline (JSON) + a rendered mouth-animation MP4.

### Music (`ai_music_generator`)
- 20 genres, 10 real instrument synthesizers (Karplus-Strong guitar, formant
  choir, Schroeder drums...), chord progressions, bass/melody/drums patterns.

### Sound effects (`ai_sound_effects`)
- 16 real effects (rain, thunder, ocean, explosion, footsteps, ui, whoosh...).

### Mixer (`ai_audio_mixer`)
- Compressor, limiter, biquad EQ, Schroeder reverb, delay, chorus, flanger,
  de-esser, spectral denoiser, mid/side widening, loudness, mastering chain.

### Quick check
```bash
python -m modules.ai_video_studio.media.smoke_audio
```
Runs all Volume 4 subsystems end-to-end (17 checks) and verifies every one
produces a non-empty real file.
