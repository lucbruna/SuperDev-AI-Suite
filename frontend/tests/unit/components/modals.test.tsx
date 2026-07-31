import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Modal } from "@/components/modals/Modal";
import { ConfirmDialog } from "@/components/modals/ConfirmDialog";

describe("Modal", () => {
  it("renders nothing when closed", () => {
    const { container } = render(
      <Modal isOpen={false} onClose={vi.fn()}>
        Content
      </Modal>,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders children when open", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        Modal content
      </Modal>,
    );
    expect(screen.getByText("Modal content")).toBeInTheDocument();
  });

  it("renders title when provided", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="My Dialog">
        Content
      </Modal>,
    );
    expect(screen.getByText("My Dialog")).toBeInTheDocument();
  });

  it("has dialog role with aria-modal", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()}>
        Content
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog).toHaveAttribute("aria-modal", "true");
  });

  it("calls onClose when close button clicked", () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} title="Closeable">
        Content
      </Modal>,
    );
    fireEvent.click(screen.getByLabelText("Close"));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when Escape pressed", () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} closeOnEsc={true}>
        Content
      </Modal>,
    );
    fireEvent.keyDown(document, { key: "Escape" });
    expect(handleClose).toHaveBeenCalled();
  });

  it("does not close on Escape when closeOnEsc is false", () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} closeOnEsc={false}>
        Content
      </Modal>,
    );
    fireEvent.keyDown(document, { key: "Escape" });
    expect(handleClose).not.toHaveBeenCalled();
  });

  it("hides close button when showCloseButton is false", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} showCloseButton={false} title="No Close">
        Content
      </Modal>,
    );
    expect(screen.queryByLabelText("Close")).not.toBeInTheDocument();
  });

  it("applies size classes", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="lg">
        Large modal
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog.className).toContain("max-w-lg");
  });

  it("applies sm size", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="sm">
        Small modal
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog.className).toContain("max-w-sm");
  });

  it("applies xl size", () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} size="xl">
        XL modal
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog.className).toContain("max-w-xl");
  });
});

describe("ConfirmDialog", () => {
  it("renders nothing when closed", () => {
    const { container } = render(
      <ConfirmDialog
        isOpen={false}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Are you sure?"
      />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("renders title and message when open", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Confirm Delete"
        message="This action cannot be undone."
      />,
    );
    expect(screen.getByText("Confirm Delete")).toBeInTheDocument();
    expect(screen.getByText("This action cannot be undone.")).toBeInTheDocument();
  });

  it("calls onConfirm when confirm button clicked", () => {
    const handleConfirm = vi.fn();
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={handleConfirm}
        title="Delete"
        message="Sure?"
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
    expect(handleConfirm).toHaveBeenCalledTimes(1);
  });

  it("calls onClose when cancel button clicked", () => {
    const handleClose = vi.fn();
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={handleClose}
        onConfirm={vi.fn()}
        title="Delete"
        message="Sure?"
      />,
    );
    fireEvent.click(screen.getByRole("button", { name: /cancel/i }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("renders custom confirm label", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Sure?"
        confirmLabel="Yes, delete it"
      />,
    );
    expect(screen.getByRole("button", { name: /yes, delete it/i })).toBeInTheDocument();
  });

  it("renders custom cancel label", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Sure?"
        cancelLabel="No, keep it"
      />,
    );
    expect(screen.getByRole("button", { name: /no, keep it/i })).toBeInTheDocument();
  });

  it("renders loading state on confirm button", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Sure?"
        isLoading={true}
      />,
    );
    const confirmBtn = screen.getByRole("button", { name: /confirm/i });
    expect(confirmBtn).toBeDisabled();
  });

  it("disables cancel when loading", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message="Sure?"
        isLoading={true}
      />,
    );
    const cancelBtn = screen.getByRole("button", { name: /cancel/i });
    expect(cancelBtn).toBeDisabled();
  });

  it("renders ReactNode message", () => {
    render(
      <ConfirmDialog
        isOpen={true}
        onClose={vi.fn()}
        onConfirm={vi.fn()}
        title="Delete"
        message={<strong>Bold message</strong>}
      />,
    );
    expect(screen.getByText("Bold message")).toBeInTheDocument();
  });
});
