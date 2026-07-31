import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Badge } from "@/components/badges/Badge";

describe("Badge", () => {
  it("renders children text", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("applies default variant", () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText("Default");
    expect(badge.className).toContain("bg-surface-100");
  });

  it("applies primary variant", () => {
    render(<Badge variant="primary">Primary</Badge>);
    const badge = screen.getByText("Primary");
    expect(badge.className).toContain("bg-primary-50");
  });

  it("applies success variant", () => {
    render(<Badge variant="success">Success</Badge>);
    const badge = screen.getByText("Success");
    expect(badge.className).toContain("bg-green-50");
  });

  it("applies warning variant", () => {
    render(<Badge variant="warning">Warning</Badge>);
    const badge = screen.getByText("Warning");
    expect(badge.className).toContain("bg-amber-50");
  });

  it("applies danger variant", () => {
    render(<Badge variant="danger">Danger</Badge>);
    const badge = screen.getByText("Danger");
    expect(badge.className).toContain("bg-red-50");
  });

  it("applies info variant", () => {
    render(<Badge variant="info">Info</Badge>);
    const badge = screen.getByText("Info");
    expect(badge.className).toContain("bg-blue-50");
  });

  it("applies sm size", () => {
    render(<Badge size="sm">Small</Badge>);
    const badge = screen.getByText("Small");
    expect(badge.className).toContain("px-1.5");
  });

  it("applies md size by default", () => {
    render(<Badge>Medium</Badge>);
    const badge = screen.getByText("Medium");
    expect(badge.className).toContain("px-2.5");
  });

  it("applies lg size", () => {
    render(<Badge size="lg">Large</Badge>);
    const badge = screen.getByText("Large");
    expect(badge.className).toContain("px-3");
    expect(badge.className).toContain("text-sm");
  });

  it("renders dot when dot is true", () => {
    const { container } = render(<Badge dot>With dot</Badge>);
    const dot = container.querySelector(".rounded-full");
    expect(dot).toBeInTheDocument();
  });

  it("does not render dot by default", () => {
    const { container } = render(<Badge>No dot</Badge>);
    const dots = container.querySelectorAll(".h-1\\.5");
    expect(dots.length).toBe(0);
  });

  it("renders remove button when removable", () => {
    const handleRemove = vi.fn();
    render(<Badge removable onRemove={handleRemove}>Removable</Badge>);
    expect(screen.getByLabelText("Remove")).toBeInTheDocument();
  });

  it("calls onRemove when remove button clicked", () => {
    const handleRemove = vi.fn();
    render(<Badge removable onRemove={handleRemove}>Removable</Badge>);
    fireEvent.click(screen.getByLabelText("Remove"));
    expect(handleRemove).toHaveBeenCalledTimes(1);
  });

  it("does not render remove button by default", () => {
    render(<Badge>Not removable</Badge>);
    expect(screen.queryByLabelText("Remove")).not.toBeInTheDocument();
  });

  it("is a span element", () => {
    render(<Badge>Span badge</Badge>);
    expect(screen.getByText("Span badge").tagName).toBe("SPAN");
  });

  it("has rounded-full class", () => {
    render(<Badge>Rounded</Badge>);
    expect(screen.getByText("Rounded").className).toContain("rounded-full");
  });

  it("applies custom className", () => {
    render(<Badge className="custom-badge">Custom</Badge>);
    expect(screen.getByText("Custom").className).toContain("custom-badge");
  });
});
