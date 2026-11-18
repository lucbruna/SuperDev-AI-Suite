import { fireEvent, render, screen } from "@testing-library/react";
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
});
