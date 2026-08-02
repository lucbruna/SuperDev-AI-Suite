import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { CloudVMPanel } from "./CloudVMPanel";

vi.mock("@/utils/api-fetch", () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

import { api } from "@/utils/api-fetch";
const mockedApi = vi.mocked(api);

const vmsData = {
  vms: [
    { id: "vm_abc123", name: "test-vm-1", provider: "aws", region: "us-east-1", spec: { cpu: 2, memory_gb: 4, disk_gb: 20 }, status: "running", ip: "10.0.1.42", agent_id: null, created_at: "2026-07-28T10:00:00Z" },
    { id: "vm_def456", name: "test-vm-2", provider: "aws", region: "us-east-1", spec: { cpu: 4, memory_gb: 8, disk_gb: 40 }, status: "stopped", ip: null, agent_id: null, created_at: "2026-07-28T09:00:00Z" },
  ],
  total: 2,
};

const statsData = { total: 2, by_status: { running: 1, stopped: 1 }, provider: "aws", region: "us-east-1", pool: { total: 3, busy: 1, idle: 2 }, snapshots: { total_snapshots: 2, total_size_mb: 512, avg_size_mb: 256 } };

beforeEach(() => {
  mockedApi.get.mockReset();
  mockedApi.post.mockReset();
  mockedApi.get.mockImplementation(async (path: string) => {
    if (path === "/api/cloud/vms") return vmsData;
    if (path === "/api/cloud/stats") return statsData;
    return {};
  });
  mockedApi.post.mockResolvedValue({});
});

describe("CloudVMPanel", () => {
  it("renders stats cards", async () => {
    render(<CloudVMPanel />);
    await waitFor(() => expect(screen.getByText("2")).toBeDefined());
    expect(screen.getAllByText("aws").length).toBeGreaterThan(0);
  });

  it("renders VM rows", async () => {
    render(<CloudVMPanel />);
    await waitFor(() => expect(screen.getByText("test-vm-1")).toBeDefined());
    expect(screen.getByText("test-vm-2")).toBeDefined();
  });

  it("shows empty state", async () => {
    mockedApi.get.mockImplementation(async () => ({ vms: [], total: 0 }));
    render(<CloudVMPanel />);
    await waitFor(() => expect(screen.getByText(/No VMs yet/)).toBeDefined());
  });

  it("calls create VM on enter", async () => {
    render(<CloudVMPanel />);
    await waitFor(() => expect(screen.getByPlaceholderText(/New VM name/)).toBeDefined());
    const input = screen.getByPlaceholderText(/New VM name/);
    fireEvent.change(input, { target: { value: "my-vm" } });
    fireEvent.keyDown(input, { key: "Enter" });
    await waitFor(() =>
      expect(mockedApi.post).toHaveBeenCalledWith(expect.stringContaining("name=my-vm"))
    );
  });
});
