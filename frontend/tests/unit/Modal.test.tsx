import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Modal } from "@/components/modals/Modal";

describe("Modal", () => {
  it("renders when open", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <p>Modal content</p>
      </Modal>,
    );
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Modal content")).toBeInTheDocument();
  });

  it("does not render when closed", () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()}>
        <p>Modal content</p>
      </Modal>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("calls onClose when overlay clicked", async () => {
    const handleClose = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <p>Content</p>
      </Modal>,
    );
    await user.click(screen.getByRole("dialog").parentElement!);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("renders children", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <span data-testid="child">Child element</span>
      </Modal>,
    );
    expect(screen.getByTestId("child")).toBeInTheDocument();
  });

  it("renders title when provided", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
        <p>Content</p>
      </Modal>,
    );
    expect(screen.getByText("Test Modal")).toBeInTheDocument();
  });

  it("renders close button by default", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <p>Content</p>
      </Modal>,
    );
    expect(screen.getByRole("button", { name: /close/i })).toBeInTheDocument();
  });

  it("hides close button when showCloseButton is false", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} showCloseButton={false}>
        <p>Content</p>
      </Modal>,
    );
    expect(screen.queryByRole("button", { name: /close/i })).not.toBeInTheDocument();
  });

  it("sets aria-modal attribute", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        <p>Content</p>
      </Modal>,
    );
    expect(screen.getByRole("dialog")).toHaveAttribute("aria-modal", "true");
  });

  it("does not call onClose when clicking content", async () => {
    const handleClose = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <button>Inside</button>
      </Modal>,
    );
    await user.click(screen.getByRole("button", { name: /inside/i }));
    expect(handleClose).not.toHaveBeenCalled();
  });

  it("calls onClose when close button clicked", async () => {
    const handleClose = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <p>Content</p>
      </Modal>,
    );
    await user.click(screen.getByRole("button", { name: /close/i }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("does not call onClose when closeOnOverlay is false", async () => {
    const handleClose = vi.fn();
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={handleClose} closeOnOverlay={false}>
        <p>Content</p>
      </Modal>,
    );
    await user.click(screen.getByRole("dialog").parentElement!);
    expect(handleClose).not.toHaveBeenCalled();
  });

  it("applies size class", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="lg">
        <p>Content</p>
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog.className).toContain("max-w-lg");
  });
});