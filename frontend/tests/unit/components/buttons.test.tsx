import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Button } from "@/components/buttons/Button";
import { IconButton } from "@/components/buttons/IconButton";

describe("Button", () => {
  it("renders children text", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("handles click events", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("applies primary variant by default", () => {
    render(<Button>Primary</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-primary-600");
  });

  it("applies secondary variant", () => {
    render(<Button variant="secondary">Secondary</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-surface-100");
  });

  it("applies ghost variant", () => {
    render(<Button variant="ghost">Ghost</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-transparent");
  });

  it("applies danger variant", () => {
    render(<Button variant="danger">Danger</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-red-600");
  });

  it("applies sm size", () => {
    render(<Button size="sm">Small</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("px-3");
    expect(btn.className).toContain("text-xs");
  });

  it("applies md size by default", () => {
    render(<Button>Middle</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("px-4");
    expect(btn.className).toContain("text-sm");
  });

  it("applies lg size", () => {
    render(<Button size="lg">Large</Button>);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("px-6");
    expect(btn.className).toContain("text-base");
  });

  it("shows loading spinner when isLoading", () => {
    render(<Button isLoading>Loading</Button>);
    const btn = screen.getByRole("button");
    expect(btn.querySelector(".animate-spin")).toBeInTheDocument();
    expect(btn).toBeDisabled();
  });

  it("is disabled when isLoading", () => {
    render(<Button isLoading>Loading</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled</Button>);
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("applies fullWidth class", () => {
    render(<Button fullWidth>Full</Button>);
    expect(screen.getByRole("button").className).toContain("w-full");
  });

  it("renders leftIcon", () => {
    render(
      <Button leftIcon={<span data-testid="left-icon">→</span>}>With Icon</Button>,
    );
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("hides leftIcon when loading", () => {
    render(
      <Button isLoading leftIcon={<span data-testid="left-icon">→</span>}>
        Loading
      </Button>,
    );
    expect(screen.queryByTestId("left-icon")).not.toBeInTheDocument();
  });

  it("renders rightIcon", () => {
    render(
      <Button rightIcon={<span data-testid="right-icon">←</span>}>With Icon</Button>,
    );
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("hides rightIcon when loading", () => {
    render(
      <Button isLoading rightIcon={<span data-testid="right-icon">←</span>}>
        Loading
      </Button>,
    );
    expect(screen.queryByTestId("right-icon")).not.toBeInTheDocument();
  });

  it("passes through HTML button attributes", () => {
    render(<Button type="submit" data-testid="custom">Submit</Button>);
    const btn = screen.getByTestId("custom");
    expect(btn).toHaveAttribute("type", "submit");
  });
});

describe("IconButton", () => {
  const icon = <span data-testid="icon">★</span>;

  it("renders icon", () => {
    render(<IconButton icon={icon} label="Favorite" />);
    expect(screen.getByTestId("icon")).toBeInTheDocument();
  });

  it("has accessible label", () => {
    render(<IconButton icon={icon} label="Favorite" />);
    expect(screen.getByLabelText("Favorite")).toBeInTheDocument();
  });

  it("has title attribute", () => {
    render(<IconButton icon={icon} label="Favorite" />);
    expect(screen.getByTitle("Favorite")).toBeInTheDocument();
  });

  it("handles click events", () => {
    const handleClick = vi.fn();
    render(<IconButton icon={icon} label="Click" onClick={handleClick} />);
    fireEvent.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("applies ghost variant by default", () => {
    render(<IconButton icon={icon} label="Ghost" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-transparent");
  });

  it("applies primary variant", () => {
    render(<IconButton icon={icon} label="Primary" variant="primary" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("bg-primary-600");
  });

  it("applies sm size", () => {
    render(<IconButton icon={icon} label="Small" size="sm" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("h-8");
    expect(btn.className).toContain("w-8");
  });

  it("applies md size by default", () => {
    render(<IconButton icon={icon} label="Medium" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("h-10");
    expect(btn.className).toContain("w-10");
  });

  it("applies lg size", () => {
    render(<IconButton icon={icon} label="Large" size="lg" />);
    const btn = screen.getByRole("button");
    expect(btn.className).toContain("h-12");
    expect(btn.className).toContain("w-12");
  });

  it("shows loading spinner when isLoading", () => {
    render(<IconButton icon={icon} label="Loading" isLoading />);
    const btn = screen.getByRole("button");
    expect(btn.querySelector(".animate-spin")).toBeInTheDocument();
    expect(btn).toBeDisabled();
  });

  it("is disabled when disabled", () => {
    render(<IconButton icon={icon} label="Disabled" disabled />);
    expect(screen.getByRole("button")).toBeDisabled();
  });
});
