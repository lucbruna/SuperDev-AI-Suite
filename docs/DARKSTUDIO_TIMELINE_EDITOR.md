# DARKSTUDIO AI — Timeline editor

## Current workflow

1. Generate a video with `POST /api/v1/video-studio/videos/generate`.
2. Read its scene timeline from `GET /api/v1/video-studio/videos/jobs/{job_id}`.
3. Save edits with `PATCH /api/v1/video-studio/videos/jobs/{job_id}/timeline`.
4. Render the edited visual sequence with `POST /api/v1/video-studio/videos/jobs/{job_id}/render-edits`.

## Edit request

```json
{
  "scene_order": [1, 0, 2],
  "scene_edits": [
    {
      "scene_index": 1,
      "duration_frames": 240,
      "transition_type": "crossfade",
      "transition_duration_frames": 12
    },
    {
      "scene_index": 0,
      "duration_frames": 300,
      "transition_type": "cut"
    }
  ]
}
```

`scene_index` always refers to the original generated storyboard. The order array must contain each original scene index exactly once. Durations are frame-based and constrained to 0.5–60 seconds. Supported transitions are `cut`, `crossfade`, and `fade_through_black`; the final scene cannot have an outgoing crossfade.

## Persistence

Video jobs, source scenes, edited scenes, and timeline metadata are stored in SQLite at:

`modules/downloads/jobs/darkstudio_jobs.sqlite3`

The database uses SQLite WAL mode. It survives API process restarts when the host keeps the downloads directory on persistent storage. It is a local single-server store, not a replicated database; container deployments must mount `modules/downloads` on a persistent volume and should plan a migration to the platform's shared database before horizontal scaling.

## Edited render limitation

The render endpoint creates a separate MP4 file and does not overwrite the original generated/narrated output. It currently renders the edited visual scenes with strict FFmpeg MP4 encoding. It does **not** yet retime narration, music, sound effects, or subtitle cues after scene reorder/duration changes. The API returns `audio_status: "not_retimed"`; treat the edited MP4 as a silent visual preview until the audio timeline renderer is implemented.

## API response statuses

- `edit_draft_status: persisted_local_sqlite`: scene edits were stored in the local SQLite database.
- `edit_render_status: rendering | completed | failed`: edited MP4 render lifecycle.
- `audio_status: not_retimed`: original audio tracks were not re-aligned to the new visual timing.
