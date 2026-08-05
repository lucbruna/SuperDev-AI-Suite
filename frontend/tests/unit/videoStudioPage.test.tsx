import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";
import VideoStudioPage from "@/app/video-studio/page";
import { useAuthStore } from "@/stores/authStore";
import type { StudioJob } from "@/api/videoStudio";

vi.mock("@/api/videoStudio", () => ({
  videoStudioApi: {
    health: vi.fn(),
    listVoices: vi.fn(),
    listJobs: vi.fn(),
    getJob: vi.fn(),
    generateVideo: vi.fn(),
  },
}));

import { videoStudioApi } from "@/api/videoStudio";
const mockedApi = vi.mocked(videoStudioApi);

const shortsJob: StudioJob = {
  job_id: "job_shorts_1",
  project_id: "p1",
  status: "completed",
  progress: 1,
  format: "shorts",
  resolution: "1080x1920",
  video_duration: 30,
};

const customJob: StudioJob = {
  job_id: "job_custom_1",
  project_id: "p1",
  status: "completed",
  progress: 1,
  format: "custom",
  resolution: "1280x720",
};

const legacyJob: StudioJob = {
  job_id: "job_legacy_1",
  project_id: "p1",
  status: "failed",
  progress: 0,
};

beforeEach(() => {
  mockedApi.health.mockReset();
  mockedApi.listVoices.mockReset();
  mockedApi.listJobs.mockReset();
  mockedApi.getJob.mockReset();
  mockedApi.generateVideo.mockReset();

  mockedApi.health.mockResolvedValue({
    status: "healthy",
    service: "video-studio",
    version: "6.0.0",
  });
  mockedApi.listVoices.mockResolvedValue([]);
  mockedApi.listJobs.mockResolvedValue([]);

  // AuthGuard only renders children when hydrated + authenticated.
  useAuthStore.setState({
    _hydrated: true,
    isAuthenticated: true,
    accessToken: "test-token",
    user: { id: "u1", email: "dev@superdev.com", fullName: "Dev" },
  });
});

describe("VideoStudioPage", () => {
  it("renders the format badge only for jobs with a known format preset", async () => {
    mockedApi.listJobs.mockResolvedValue([shortsJob, customJob, legacyJob]);
    render(<VideoStudioPage />);

    // Await the jobs list, then scope every query to the jobs card so the
    // format preset buttons ("YouTube 16:9", "Quadrado 1:1") don't collide.
    // NOTE: the Card root is anchored by its `.rounded-xl` class — if the Card
    // component changes that class, update this selector.
    const badge = await screen.findByText("YouTube Shorts 9:16");
    const jobsSection = badge.closest(".rounded-xl") as HTMLElement;

    // The persisted "shorts" job shows its preset badge label.
    expect(within(jobsSection).getByText("YouTube Shorts 9:16")).toBeInTheDocument();

    // "custom" and legacy jobs (no format) must not render any format badge.
    expect(within(jobsSection).queryByText("YouTube 16:9")).not.toBeInTheDocument();
    expect(within(jobsSection).queryByText("Reels 9:16")).not.toBeInTheDocument();
    expect(within(jobsSection).queryByText("TikTok 9:16")).not.toBeInTheDocument();
    expect(within(jobsSection).queryByText("Quadrado 1:1")).not.toBeInTheDocument();
  });

  it("suggests the matching duration preset when a format is active", async () => {
    render(<VideoStudioPage />);
    await screen.findByText("Gerar vídeo com narração");

    // No suggestion while the format is custom.
    expect(screen.queryByText(/sugere \d+s/)).not.toBeInTheDocument();

    const tiktokButton = screen.getByRole("button", { name: /TikTok/ });
    expect(tiktokButton).toHaveAttribute("aria-pressed", "false");

    fireEvent.click(tiktokButton);

    // Format becomes active, duration pinned to the preset (15s) and the
    // matching DURATION_PRESETS chip is highlighted with a title + hint.
    expect(screen.getByRole("button", { name: /TikTok/ })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText(/Formato ativo: TikTok/)).toBeInTheDocument();
    expect(screen.getByText(/TikTok sugere 15s/)).toBeInTheDocument();

    const suggestedChip = screen.getByTitle("15s — recomendado para TikTok");
    expect(suggestedChip).toHaveAttribute("aria-pressed", "true");
    expect(within(suggestedChip).getByText("✦")).toBeInTheDocument();
  });
});
