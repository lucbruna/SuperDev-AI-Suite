import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";

describe("StatusBadge", () => {
  it("renders with default label for success", () => {
    render(<StatusBadge status="success" />);
    expect(screen.getByText("Sucesso")).toBeInTheDocument();
  });

  it("renders with default label for error", () => {
    render(<StatusBadge status="error" />);
    expect(screen.getByText("Erro")).toBeInTheDocument();
  });

  it("renders with default label for warning", () => {
    render(<StatusBadge status="warning" />);
    expect(screen.getByText("Aviso")).toBeInTheDocument();
  });

  it("renders with default label for info", () => {
    render(<StatusBadge status="info" />);
    expect(screen.getByText("Info")).toBeInTheDocument();
  });

  it("renders with default label for idle", () => {
    render(<StatusBadge status="idle" />);
    expect(screen.getByText("Ocioso")).toBeInTheDocument();
  });

  it("renders with default label for running", () => {
    render(<StatusBadge status="running" />);
    expect(screen.getByText("Executando")).toBeInTheDocument();
  });

  it("renders custom label when provided", () => {
    render(<StatusBadge status="success" label="Deployed" />);
    expect(screen.getByText("Deployed")).toBeInTheDocument();
  });

  it("has correct CSS classes for success", () => {
    render(<StatusBadge status="success" />);
    const badge = screen.getByText("Sucesso");
    expect(badge.className).toContain("bg-green-100");
    expect(badge.className).toContain("text-green-800");
  });

  it("has correct CSS classes for error", () => {
    render(<StatusBadge status="error" />);
    const badge = screen.getByText("Erro");
    expect(badge.className).toContain("bg-red-100");
    expect(badge.className).toContain("text-red-800");
  });

  it("is a span element", () => {
    render(<StatusBadge status="info" />);
    expect(screen.getByText("Info").tagName).toBe("SPAN");
  });
});

describe("LoadingSpinner", () => {
  it("renders without text by default", () => {
    render(<LoadingSpinner />);
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });

  it("renders with text when provided", () => {
    render(<LoadingSpinner text="Loading data..." />);
    expect(screen.getByText("Loading data...")).toBeInTheDocument();
  });

  it("applies sm size class", () => {
    const { container } = render(<LoadingSpinner size="sm" />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner?.className).toContain("w-4");
    expect(spinner?.className).toContain("h-4");
  });

  it("applies md size class by default", () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner?.className).toContain("w-8");
    expect(spinner?.className).toContain("h-8");
  });

  it("applies lg size class", () => {
    const { container } = render(<LoadingSpinner size="lg" />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner?.className).toContain("w-12");
    expect(spinner?.className).toContain("h-12");
  });

  it("has spinning animation", () => {
    const { container } = render(<LoadingSpinner />);
    const spinner = container.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
  });

  it("renders text with correct styling", () => {
    render(<LoadingSpinner text="Please wait" />);
    const text = screen.getByText("Please wait");
    expect(text.className).toContain("text-sm");
    expect(text.className).toContain("text-gray-500");
  });
});

describe("EmptyState", () => {
  it("renders title", () => {
    render(<EmptyState title="No items found" />);
    expect(screen.getByText("No items found")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(
      <EmptyState title="No items" description="Create your first item to get started" />,
    );
    expect(screen.getByText("Create your first item to get started")).toBeInTheDocument();
  });

  it("does not render description when not provided", () => {
    render(<EmptyState title="Empty" />);
    expect(screen.queryByText(/create/i)).not.toBeInTheDocument();
  });

  it("renders icon when provided", () => {
    render(
      <EmptyState
        icon={<span data-testid="test-icon">📦</span>}
        title="No data"
      />,
    );
    expect(screen.getByTestId("test-icon")).toBeInTheDocument();
  });

  it("does not render icon container when not provided", () => {
    const { container } = render(<EmptyState title="Empty" />);
    expect(container.querySelector(".text-gray-400")).not.toBeInTheDocument();
  });

  it("renders action when provided", () => {
    render(
      <EmptyState
        title="Empty"
        action={<button>Create New</button>}
      />,
    );
    expect(screen.getByRole("button", { name: "Create New" })).toBeInTheDocument();
  });

  it("does not render action when not provided", () => {
    render(<EmptyState title="Empty" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("centers content", () => {
    const { container } = render(<EmptyState title="Centered" />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain("flex-col");
    expect(wrapper.className).toContain("items-center");
    expect(wrapper.className).toContain("text-center");
  });
});
