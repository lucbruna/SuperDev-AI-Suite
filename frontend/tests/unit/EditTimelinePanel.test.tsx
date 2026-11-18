import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import { videoStudioApi } from "@/api/videoStudio";
import { describe, expect, it } from "vitest";
import EditTimelinePanel from "@/components/video-studio/EditTimelinePanel";
import type { EditTimeline } from "@/api/videoStudio";

const timeline: EditTimeline = {
  version: "1.0",
  timebase: "frames",
  fps: 24,
  width: 1080,
  height: 1920,
  duration_frames: 96,
  duration_seconds: 4,
  tracks: [
    {
      id: "video-main",
      type: "video",
      clips: [
        { scene_index: 0, start_frame: 0, end_frame: 48, duration_frames: 48, shot_type: "wide" },
        { scene_index: 1, start_frame: 48, end_frame: 96, duration_frames: 48, shot_type: "close_up" },
      ],
    },
    {
      id: "audio-narration",
      type: "audio",
      role: "narration",
      clips: [{ asset: "voice.wav", start_frame: 0, end_frame: 72, duration_frames: 72 }],
    },
    {
      id: "text-subtitles",
      type: "subtitle",
      clips: [{ text: "Uma legenda de teste", start_frame: 12, end_frame: 48, duration_frames: 36 }],
    },
  ],
};

describe("EditTimelinePanel", () => {
  it("renders video, narration and subtitle tracks with timeline metadata", () => {
    render(<EditTimelinePanel timeline={timeline} />);
    expect(screen.getByText(/1080×1920 · 24 FPS · 00:04.0/)).toBeInTheDocument();
    expect(screen.getByText("🎬 Vídeo")).toBeInTheDocument();
    expect(screen.getByText("🎙️ Narração")).toBeInTheDocument();
    expect(screen.getByText("💬 Legendas")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Cena 1 · wide/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /voice.wav/ })).toBeInTheDocument();
  });

  it("lets the user scrub the playhead and inspect a selected clip", () => {
    render(<EditTimelinePanel timeline={timeline} />);
    fireEvent.click(screen.getByRole("button", { name: /Cena 2 · close_up/ }));
    expect(screen.getByText(/Selecionado: Cena 2 · close_up/)).toBeInTheDocument();

    fireEvent.change(screen.getByRole("slider", { name: "Posição do cursor da timeline" }), {
      target: { value: "60" },
    });
    expect(screen.getByText("00:02.5")).toBeInTheDocument();
  });
  it("allows removing a sound effect and persists the remaining audio clips", async () => {
    const audioTimeline: EditTimeline = {
      ...timeline,
      tracks: [...timeline.tracks,
        { id: "audio-music", type: "audio", role: "music", clips: [{ asset: "music/theme.wav", start_frame: 0, end_frame: 96, duration_frames: 96, start_seconds: 0, end_seconds: 4, volume: 0.3 }] },
        { id: "audio-sfx", type: "audio", role: "sound_effect", clips: [{ asset: "effects/hit.wav", start_frame: 24, end_frame: 36, duration_frames: 12, start_seconds: 1, end_seconds: 1.5, volume: 0.8 }] },
      ],
    };
    const assets = vi.spyOn(videoStudioApi, "listJobAudioAssets").mockResolvedValue([]);
    const job = vi.spyOn(videoStudioApi, "getJob").mockResolvedValue({ job_id: "audio-job", project_id: "p1", status: "completed", progress: 1, audio_settings: { ducking_enabled: false, ducking_db: 14, normalization_enabled: false, normalization_target_dbfs: -22 } });
    const save = vi.spyOn(videoStudioApi, "updateJobAudio").mockResolvedValue({
      edit_timeline: audioTimeline, audio_draft_status: "saved", message: "Faixas salvas",
    });
    render(<EditTimelinePanel timeline={audioTimeline} jobId="audio-job" />);
    await waitFor(() => expect(videoStudioApi.listJobAudioAssets).toHaveBeenCalledWith("audio-job"));
    await waitFor(() => expect(screen.getByRole("checkbox", { name: "Ativar ducking" })).not.toBeChecked());
    expect(screen.getByRole("checkbox", { name: "Ativar normalização" })).not.toBeChecked();
    fireEvent.click(screen.getByRole("checkbox", { name: "Repetir" }));
    fireEvent.click(screen.getByRole("button", { name: "Remover" }));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações de áudio" }));
    await waitFor(() => expect(save).toHaveBeenCalled());
    expect(save.mock.calls[0][1].sfx_clips).toEqual([]);
    expect(save.mock.calls[0][1].music_clips).toHaveLength(1);
    expect(save.mock.calls[0][1].music_clips[0].loop).toBe(true);
    expect(save.mock.calls[0][1].ducking_enabled).toBe(false);
    expect(save.mock.calls[0][1].ducking_db).toBe(14);
    expect(save.mock.calls[0][1].normalization_enabled).toBe(false);
    expect(save.mock.calls[0][1].normalization_target_dbfs).toBe(-22);
    save.mockRestore();
    assets.mockRestore();
    job.mockRestore();
  });
});
