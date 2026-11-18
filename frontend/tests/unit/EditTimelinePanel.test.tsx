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
  it("shows final audio quality warnings after rendering an edited MP4", async () => {
    vi.spyOn(videoStudioApi, "getJob").mockResolvedValue({ job_id: "quality-job", project_id: "p1", status: "completed", progress: 1 });
    const renderJob = vi.spyOn(videoStudioApi, "renderJobEdits").mockResolvedValue({
      status: "completed", output_url: "/downloads/final.mp4", video_duration: 4, file_size_bytes: 1000, audio_status: "mixed_audio",
      quality: { status: "needs_review", export_allowed: true, peak_dbfs: -1.5, rms_dbfs: -18, clipping_ratio: 0, warning_count: 1, critical_count: 0, warnings: [{ code: "internal_silence_gaps", severity: "warning", message: "Silêncio interno detectado" }], silence_gaps: [{ start: 1, end: 1.8, duration: 0.8 }], narration_music_masking: [{ start: 2, end: 3, duration: 1, voice_music_gap_db: -2 }], recommendations: [{ action: "increase_ducking", recommended_ducking_db: 12, message: "Aumente o ducking em 3 dB." }], masking_method: "RMS heuristic" },
      message: "Render concluído com revisão recomendada.",
    });
    render(<EditTimelinePanel timeline={timeline} jobId="quality-job" />);
    fireEvent.click(screen.getByRole("button", { name: "Renderizar edição" }));
    await waitFor(() => expect(renderJob).toHaveBeenCalledWith("quality-job"));
    expect(await screen.findByText("Revisão recomendada")).toBeInTheDocument();
    expect(screen.getByText("Silêncio interno detectado")).toBeInTheDocument();
    expect(screen.getByText(/Possível voz encoberta/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Aplicar correção" }));
    expect(screen.getByLabelText("Redução (dB)")).toHaveValue(12);
    expect(screen.getByText(/Ducking atualizado no rascunho/)).toBeInTheDocument();
  });
  it("analyzes audio sources and applies the recommended ducking values", async () => {
    const audioTimeline: EditTimeline = {
      ...timeline,
      tracks: [...timeline.tracks,
        { id: "audio-music", type: "audio", role: "music", clips: [{ asset: "music/theme.wav", start_frame: 0, end_frame: 96, duration_frames: 96, start_seconds: 0, end_seconds: 4 }] },
      ],
    };
    vi.spyOn(videoStudioApi, "listJobAudioAssets").mockResolvedValue([]);
    vi.spyOn(videoStudioApi, "getJob").mockResolvedValue({ job_id: "analysis-job", project_id: "p1", status: "completed", progress: 1 });
    const analysis = vi.spyOn(videoStudioApi, "analyzeJobAudio").mockResolvedValue({
      sources_analyzed: 2,
      reports: { narration: [], music: [], sound_effect: [] },
      warnings: [{ role: "music", source: "music_0", code: "clipping_or_near_full_scale_peak" }],
      skipped: [],
      ducking_recommendation: { available: true, recommended_ducking_db: 12, recommended_threshold_db: -32, reason: "Níveis medidos." },
      message: "Análise concluída.",
    });
    render(<EditTimelinePanel timeline={audioTimeline} jobId="analysis-job" />);
    fireEvent.click(screen.getByRole("button", { name: "Analisar áudio" }));
    await waitFor(() => expect(analysis).toHaveBeenCalledWith("analysis-job"));
    expect(await screen.findByText(/clipping or near full scale peak/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Aplicar sugestão" }));
    expect(screen.getByRole("checkbox", { name: "Ativar ducking" })).toBeChecked();
    expect(screen.getByLabelText("Redução (dB)")).toHaveValue(12);
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
    const job = vi.spyOn(videoStudioApi, "getJob").mockResolvedValue({ job_id: "audio-job", project_id: "p1", status: "completed", progress: 1, audio_settings: { ducking_enabled: false, ducking_db: 14, normalization_enabled: false, normalization_target_dbfs: -22, loudness_normalization_enabled: true, target_lufs: -16, compressor_enabled: true, compressor_threshold_db: -20, compressor_ratio: 4, eq_enabled: true, eq_low_db: 2, eq_mid_db: -1, eq_high_db: 1 } });
    const save = vi.spyOn(videoStudioApi, "updateJobAudio").mockResolvedValue({
      edit_timeline: audioTimeline, audio_draft_status: "saved", message: "Faixas salvas",
    });
    render(<EditTimelinePanel timeline={audioTimeline} jobId="audio-job" />);
    await waitFor(() => expect(videoStudioApi.listJobAudioAssets).toHaveBeenCalledWith("audio-job"));
    await waitFor(() => expect(screen.getByRole("checkbox", { name: "Ativar ducking" })).not.toBeChecked());
    expect(screen.getByRole("checkbox", { name: "Ativar normalização" })).not.toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Ativar LUFS" })).toBeChecked();
    expect(screen.getByLabelText("Alvo LUFS")).toHaveValue(-16);
    expect(screen.getByRole("checkbox", { name: "Ativar compressor" })).toBeChecked();
    expect(screen.getByRole("checkbox", { name: "Ativar EQ" })).toBeChecked();
    expect(screen.getByLabelText("Graves")).toHaveValue("2");
    expect(screen.getByLabelText("Médios")).toHaveValue("-1");
    expect(screen.getByLabelText("Agudos")).toHaveValue("1");
    fireEvent.change(screen.getByLabelText("Preset de masterização"), { target: { value: "voice" } });
    fireEvent.change(screen.getAllByRole("slider", { name: /Panorama L\/R/ })[0], { target: { value: "-0.5" } });
    fireEvent.click(screen.getByRole("checkbox", { name: "Repetir" }));
    fireEvent.click(screen.getByRole("button", { name: "Remover" }));
    fireEvent.click(screen.getByRole("button", { name: "Salvar alterações de áudio" }));
    await waitFor(() => expect(save).toHaveBeenCalled());
    expect(save.mock.calls[0][1].sfx_clips).toEqual([]);
    expect(save.mock.calls[0][1].music_clips).toHaveLength(1);
    expect(save.mock.calls[0][1].music_clips[0].loop).toBe(true);
    expect(save.mock.calls[0][1].music_clips[0].pan).toBe(-0.5);
    expect(save.mock.calls[0][1].ducking_enabled).toBe(false);
    expect(save.mock.calls[0][1].ducking_db).toBe(14);
    expect(save.mock.calls[0][1].normalization_enabled).toBe(false);
    expect(save.mock.calls[0][1].normalization_target_dbfs).toBe(-22);
    expect(save.mock.calls[0][1].loudness_normalization_enabled).toBe(true);
    expect(save.mock.calls[0][1].target_lufs).toBe(-16);
    expect(save.mock.calls[0][1].compressor_enabled).toBe(true);
    expect(save.mock.calls[0][1].compressor_threshold_db).toBe(-22);
    expect(save.mock.calls[0][1].compressor_ratio).toBe(3.5);
    expect(save.mock.calls[0][1].eq_enabled).toBe(true);
    expect(save.mock.calls[0][1].eq_low_db).toBe(-2);
    expect(save.mock.calls[0][1].eq_mid_db).toBe(1.5);
    expect(save.mock.calls[0][1].eq_high_db).toBe(2);
    expect(save.mock.calls[0][1].mastering_preset).toBe("voice");
    save.mockRestore();
    assets.mockRestore();
    job.mockRestore();
  });
});


  it("runs studio-aware visual quality analysis and shows the heuristic score", async () => {
    vi.spyOn(videoStudioApi, "getJob").mockResolvedValue({
      job_id: "visual-job", project_id: "p1", status: "completed", progress: 1,
    });
    const analyze = vi.spyOn(videoStudioApi, "analyzeJobVisuals").mockResolvedValue({
      studio_id: "historical_documentary",
      status: "needs_review",
      score: 78,
      score_label: "pontuação heurística de metadados",
      components: { motion: 100, composition: 75, variety: 50, clarity: 87 },
      scene_count: 4,
      moving_camera_scenes: 4,
      animated_primitives: 3,
      unique_shot_types: 2,
      shot_counts: { wide: 2, medium: 2 },
      character_continuity_changes: 0,
      scenes: [],
      warnings: [{ code: "low_shot_variety", severity: "warning", unique_shots: 2 }],
      analysis_method: "scene_descriptor_metadata",
      limitations: ["Não inspeciona pixels do MP4 final."],
    });
    render(<EditTimelinePanel timeline={timeline} jobId="visual-job" />);
    fireEvent.click(screen.getByRole("button", { name: "Analisar qualidade visual" }));
    await waitFor(() => expect(analyze).toHaveBeenCalledWith("visual-job"));
    expect(await screen.findByText("78/100 · needs review")).toBeInTheDocument();
    expect(screen.getByText(/low shot variety/)).toBeInTheDocument();
    expect(screen.getByText(/não é análise de pixels do MP4/i)).toBeInTheDocument();
  });
