# AI Avatar & Digital Human Engine — Volume 6

> **AI Video Studio · Volume 6** — avatares 2D/3D, humanos digitais realistas,
> captura facial/corporal, expressões emocionais, gestos automáticos,
> vestuário, cabelos, biblioteca de atores virtuais e treinamento
> personalizado.

The **AI Avatar & Digital Human Engine** is the largest module of the
AI Video Studio blueprint (≈150 files across 11 subsystems). It powers
videos with virtual presenters and intelligent characters, from a
deterministic procedural generator of digital humans to full facial
animation, emotion blending, gesture vocabulary, motion-capture
retargeting, a domain-specific library of 48 virtual actors, a
training layer for identity learning and personalization, and a
speaking-avatar pipeline that connects the Voice Studio and Lip Sync
subsystems into narrated, lip-synced presenter videos.

Everything follows the studio's architectural pattern: singleton
accessors (`get_*`), numpy/PIL primitives, JSON-serializable results,
lazy subsystem imports, and stdlib-only engines (no mandatory
third-party dependencies).

---

## Table of contents

- [Architecture](#architecture)
- [Subsystems](#subsystems)
  - [Core](#core)
  - [Digital Humans](#digital-humans)
  - [Facial Animation](#facial-animation)
  - [Emotion Engine](#emotion-engine)
  - [Gesture Engine](#gesture-engine)
  - [Motion Capture](#motion-capture)
  - [Clothing System](#clothing-system)
  - [Hairstyle Studio](#hairstyle-studio)
  - [Avatar Library](#avatar-library)
  - [Avatar Training](#avatar-training)
  - [Speaking Avatar](#speaking-avatar)
- [Quick start](#quick-start)
- [REST API](#rest-api)
- [Integration with other studio modules](#integration-with-other-studio-modules)
- [Validation](#validation)

---

## Architecture

```
ai_avatar_engine/
├── avatar_engine.py        # AvatarEngine — public orchestrator (entry point)
├── avatar_manager.py       # profile lifecycle (register/get/list)
├── avatar_registry.py      # shared profile registry
├── avatar_scheduler.py     # job scheduling
├── avatar_optimizer.py     # quality/fps/resolution optimization
├── avatar_learning.py      # learning hooks
├── avatar_statistics.py    # generation statistics
├── avatar_cache.py         # generation cache
├── avatar_logger.py        # structured logging
├── avatar_profiles.py      # AvatarProfile model + profile_from_dict
├── avatar_permissions.py   # RBAC checks
├── avatar_metadata.py      # metadata enrichment
├── avatar_export.py        # export helpers
├── avatar_import.py        # import helpers
│
├── digital_humans/         # procedural body/face/feature generation
├── facial_animation/       # rig, mesh, landmarks, per-feature controllers
├── emotions/               # 12 emotional presets + blending
├── gestures/               # gesture vocabulary by context
├── motion_capture/         # keypoints → skeleton → retarget → export
├── clothing/               # wardrobe, garments, materials, textures
├── hairstyles/             # hairstyle catalogs + color engine
├── library/                # 48 domain-specific virtual actors
├── training/               # learning, personalization, validation, versioning
└── speaking/               # avatar × voice-studio × lip-sync → narrated video
```

The `AvatarEngine` wires the subsystems together with **lazy imports** so
the core works even when an optional subsystem is not installed:

- `generate_avatar(profile, ...)` → delegates to the Digital Humans
  subsystem; falls back to a deterministic structural descriptor when no
  renderer is available; records statistics, caches the result, and
  enriches it with metadata.
- `register_profile` / `get_profile` / `list_profiles` → profile
  lifecycle through the shared registry.
- `get_job` / `list_jobs` / `stats` → job introspection and aggregated
  statistics.

---

## Subsystems

### Core

The public entry point of the package. See
[Architecture](#architecture) — the engine, manager, registry, scheduler,
optimizer, learning, statistics, cache, logger, profiles, permissions,
metadata, export and import modules follow the exact same pattern as the
other studio volumes (config/context/engine/events/logger/manager/
metrics/models/protocols/registry/runtime/security/factory/interfaces).

```python
from modules.ai_video_studio.ai_avatar_engine import get_avatar_engine, AvatarProfile

engine = get_avatar_engine()
profile = AvatarProfile(id="biz_maya", name="Maya Chen", style="realistic",
                        dimension="3d", gender="female", default_outfit="business")
engine.register_profile(profile)
result = engine.generate_avatar(profile, quality="high", fps=24, seed=42)
print(result["status"], result["elapsed_seconds"])
```

### Digital Humans

Procedural generation of the human body and face (19 files):

- **15 generators** — body, face, skin, eyes, eyebrows, eyelashes, hair,
  beard, teeth, tongue, hands, feet, clothing, accessories.
- **Variations** — body proportions, body variations, age variations.

```python
from modules.ai_video_studio.ai_avatar_engine.digital_humans import get_digital_human_engine

human = get_digital_human_engine().generate(profile, settings={"quality": "high"}, seed=7)
# -> {body, face, skin, eyes, hair, ...} deterministic descriptor
```

### Facial Animation

Rig, face mesh (23 landmarks) and per-feature controllers (16 files):

- **Rig / mesh / solver** — `facial_rig`, `face_mesh`, `face_solver`,
  `facial_landmarks`.
- **Controllers** — smile, lips, jaw, cheeks, nose, eyebrows, forehead,
  blink, eye-tracking, eye-contact, gaze.

```python
from modules.ai_video_studio.ai_avatar_engine.facial_animation import get_facial_engine

frame = get_facial_engine().compose(t=0.1, smile=0.7, blink=0.0)
# -> per-frame blend of controller weights (JSON-serializable)
```

### Emotion Engine

12 emotional presets plus the engine and blending (14 files):
happy, sad, angry, fear, surprise, disgust, neutral, excitement,
confidence, empathy, curiosity, humor — with `emotional_blending` for
segmented timelines with easing.

```python
from modules.ai_video_studio.ai_avatar_engine.emotions import get_emotion_engine

state = get_emotion_engine().apply("happy", intensity=0.8)
```

### Gesture Engine

Automatic gesture vocabulary by context (16 files):
idle_pose, hand/finger/arm/shoulder/head movements, body language,
presentation, teaching, interview, conversation, applause, pointing,
waving.

```python
from modules.ai_video_studio.ai_avatar_engine.gestures import get_gesture_engine

plan = get_gesture_engine().plan_for_text("welcome everyone", context="presentation")
```

### Motion Capture

Full pipeline from raw keypoints to exportable animation (10 files):
`pose_estimation` → `body_tracker` → `skeleton_mapper` →
`movement_classifier` → `motion_cleaner` → `motion_smoothing` →
`motion_retarget` → `motion_blending` → `animation_export`.

```python
from modules.ai_video_studio.ai_avatar_engine.motion_capture import get_mocap_engine

result = get_mocap_engine().process(
    [{"t": 0.0, "hips": [0, 0, 0], "r_wrist": [0.5, 1, 0], ...}],
    fps=24, smooth=0.5, retarget=True,
)
# -> cleaned + smoothed + retargeted keyframes, JSON export
```

### Clothing System

Wardrobe and garment generation (14 files):
`shirt/pants/jacket/dress/shoes/hat/glasses/jewelry` generators +
`wardrobe_manager`, `fabric_materials`, `texture_library`,
`color_palettes`.

```python
from modules.ai_video_studio.ai_avatar_engine.clothing import get_clothing_engine

outfit = get_clothing_engine().dress(occasion="business", seed=5)
# primary/accent colors guaranteed to differ (review fix)
```

### Hairstyle Studio

Hairstyle catalogs and color engine (11 files):
short, medium, long, curly, straight, afro, beard, mustache, eyebrows +
`color_engine`.

```python
from modules.ai_video_studio.ai_avatar_engine.hairstyles import get_hairstyle_engine

styles = get_hairstyle_engine().styles("medium")
```

### Avatar Library

**48 virtual actors** in 15 domains (16 files): business, education,
medical, legal, agriculture, engineering, finance, tourism, ecommerce,
influencer, presenter, child, elderly, fantasy, sci-fi.

```python
from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library

lib = get_avatar_library()
profiles = lib.list(style="realistic", gender="female")
maya = lib.get("biz_maya")
```

### Avatar Training

Learning, personalization, validation and versioning (10 files):
`identity_learning`, `speech_learning`, `gesture_learning`,
`facial_learning`, `movement_learning`, `personalization`,
`reinforcement_learning` (bandit), `quality_validation`,
`model_versioning`.

```python
from modules.ai_video_studio.ai_avatar_engine.training import get_training_engine

report = get_training_engine().train(profile_id="biz_maya", data={...})
```

### Speaking Avatar

Narrated talking-presenter video (3 files): the end-to-end bridge between
the avatar engine, the AI Voice Studio and the AI Lip Sync subsystems.

Pipeline (`speaking_engine.py` → `avatar_renderer.py`):

1. **Narration** — Voice Studio synthesizes the audio
   (edge-tts → gTTS → pyttsx3 → offline formant) into a real file; a
   caller-provided ``audio_path`` skips TTS entirely.
2. **Lip sync** — the AI Lip Sync engine times the text against the audio
   and produces a per-frame viseme timeline (mouth open/round/wide +
   natural blinks).
3. **Facial rig** — each viseme frame is composed through the facial
   engine (``mouth_open``, smile/emotion base, forced blinks).
4. **Render + mux** — the talking head is drawn with the avatar's
   skin/hair/eye colors and the narration is muxed onto the video (MP4,
   GIF fallback), with a per-frame JSON timeline persisted alongside.

```python
import asyncio
from modules.ai_video_studio.ai_avatar_engine.speaking import get_speaking_engine

async def main():
    result = await get_speaking_engine().generate(
        "biz_maya", "Hello! Welcome to the AI video studio.",
        voice_id="corporate_female_1", language="en",
        fps=24, width=640, height=480, emotion="happy",
    )
    print(result["output_path"], result["duration"], result["frames"])

asyncio.run(main())
```

---

## Quick start

```bash
# 1. Generate a digital human for a library profile
python - <<'EOF'
from modules.ai_video_studio.ai_avatar_engine import get_avatar_engine
from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library

profile = get_avatar_library().get("biz_maya")
result = get_avatar_engine().generate_avatar(profile, quality="high", seed=42)
print(result["status"], result["elapsed_seconds"], "seconds")
EOF

# 2. Run the REST API (see next section)
uvicorn modules.ai_video_studio.api.main:create_app --factory --port 8001
# open http://localhost:8001/api/v1/video-studio/docs
```

---

## REST API

All avatar endpoints live under the
`/api/v1/video-studio/avatar-engine` prefix (router:
`modules/ai_video_studio/api/routes/avatar_engine.py`).

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/profiles` | List virtual actors (filters: `style`, `dimension`, `gender`) |
| `POST` | `/profiles` | Register an avatar profile |
| `POST` | `/generate` | Generate a full digital-human descriptor (`profile_id`, `quality`, `fps`, `resolution`, `seed`) |
| `GET`  | `/emotions` | List the 12 emotions |
| `GET`  | `/gestures` | List gestures (up to 30 entries with details) |
| `GET`  | `/clothing` | List clothing occasions |
| `GET`  | `/hairstyles` | List catalogs, or styles per catalog (`?catalog=medium`) |
| `POST` | `/motion-capture` | Process motion-capture keyframes (`keyframes`, `fps`, `smooth`, `retarget`) |
| `POST` | `/speak` | Narrated talking-avatar video with lip-sync (`profile_id`, `text`, `voice_id`, `language`, `emotion`, `speed`, `pitch`, `fps`, `width`, `height`, `quality`, `audio_path`) |
| `GET`  | `/speaking/voices` | List TTS voices available to the narration chain |
| `GET`  | `/stats` | Avatar engine statistics |

Example:

```bash
curl -s http://localhost:8001/api/v1/video-studio/avatar-engine/profiles | jq .data.count
curl -s -X POST http://localhost:8001/api/v1/video-studio/avatar-engine/generate \
  -H 'Content-Type: application/json' \
  -d '{"profile_id": "biz_maya", "quality": "high"}' | jq .data.status
# Speaking avatar (real TTS narration + lip-sync video)
curl -s -X POST http://localhost:8001/api/v1/video-studio/avatar-engine/speak \
  -H 'Content-Type: application/json' \
  -d '{"profile_id": "biz_maya", "text": "Hello! Welcome to the AI video studio.",
       "voice_id": "corporate_female_1", "emotion": "happy"}' | jq .data.output_path
```

Interactive docs: `/api/v1/video-studio/docs` (Swagger UI).

---

## Integration with other studio modules

The avatar engine plugs into the rest of the AI Video Studio:

| Studio module       | Role in the avatar pipeline                       |
|---------------------|---------------------------------------------------|
| AI Director         | scene/directorial decisions for presenters        |
| AI Storyboard       | framing and shot planning                          |
| AI Voice Studio     | narrator/voice profiles driving lip sync          |
| AI Lip Sync         | visemes from audio for the facial rig             |
| **Speaking Avatar** | **avatar × voice × lip-sync → narrated video**    |
| AI Animation Engine | character/skeleton animation output               |
| AI Camera Engine    | camera moves for presenter shots                  |
| AI Physics Engine   | cloth/hair simulation realism                     |
| AI Music Studio     | soundtrack                                       |
| AI Subtitle Studio  | captions for avatar speech                        |
| AI Export Studio    | final render of the avatar performance            |
| Super AI Orchestrator | end-to-end job orchestration                    |

---

## Validation

- **1007/1007 modules import** across the studio (0 broken).
- **1001 passed / 0 failed** in the full pytest suite (unit +
  integration + runtime_engine + e2e), including the 33 tests in
  `tests/unit/test_avatar_engine_v6.py` and the 10 hermetic tests in
  `tests/unit/test_speaking_avatar.py` (no TTS/network required).
- **Lint (ruff) clean** on all module files + API router + tests.
- **API validated live** — every `/avatar-engine/*` endpoint returns
  200 (48 profiles, 12 emotions, 9 gestures, 9 clothing occasions,
  9 hairstyle catalogs, generate, motion-capture, speak, speaking/voices,
  stats).
- **End-to-end verified** — the speaking pipeline synthesized real
  narration (edge-tts), timed 36 phonemes to the audio, drove 55 frames
  of mouth animation (9 distinct mouth-open levels + natural blinks) and
  muxed the audio into a playable MP4.

### Review fixes applied

- Operator-precedence bug in `clothing/wardrobe_manager.py` — primary and
  accent colors now guaranteed to differ.
- Lazy imports in `facial_animation/facial_engine.py` (no top-level
  import cycle).
- Encapsulated registry internals in `avatar_manager.py`; removed dead
  `_logger` assignment in `avatar_registry.py`; relaxed `keyframes` type
  in the motion-capture API.
