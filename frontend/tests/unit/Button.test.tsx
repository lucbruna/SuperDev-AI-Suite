import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Button } from "@/components/buttons/Button";

describe("Button", () => {
  it("renders with label", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole("button", { name: /click me/i })).toBeInTheDocument();
  });

  it("handles click event", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    render(<Button onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole("button"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire click when disabled", async () => {
    const handleClick = vi.fn();
    const user = userEvent.setup();
    render(<Button disabled onClick={handleClick}>Click me</Button>);
    await user.click(screen.getByRole("button"));
    expect(handleClick).not.toHaveBeenCalled();
  });

  it("shows loading state", () => {
    render(<Button isLoading>Loading</Button>);
    const button = screen.getByRole("button");
    expect(button).toBeDisabled();
    expect(button.querySelector("svg")).toBeInTheDocument();
  });

  it("does not render children text when loading", () => {
    render(<Button isLoading>Submit</Button>);
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent("Submit");
  });

  it("applies primary variant class by default", () => {
    render(<Button>Primary</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-primary-600");
  });

  it("applies secondary variant class", () => {
    render(<Button variant="secondary">Secondary</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-surface-100");
  });

  it("applies ghost variant class", () => {
    render(<Button variant="ghost">Ghost</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-transparent");
  });

  it("applies danger variant class", () => {
    render(<Button variant="danger">Danger</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-red-600");
  });

  it("applies size classes", () => {
    render(<Button size="lg">Large</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("px-6");
  });

  it("applies fullWidth class", () => {
    render(<Button fullWidth>Full</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("w-full");
  });

  it("passes additional className", () => {
    render(<Button className="custom-class">Custom</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("custom-class");
  });

  it("renders with left icon", () => {
    render(<Button leftIcon={<span data-testid="left-icon" />}>With Icon</Button>);
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("renders with right icon", () => {
    render(<Button rightIcon={<span data-testid="right-icon" />}>With Icon</Button>);
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("does not show left icon when loading", () => {
    render(<Button isLoading leftIcon={<span data-testid="left-icon" />}>Loading</Button>);
    expect(screen.queryByTestId("left-icon")).not.toBeInTheDocument();
  });

  it("sets display name", () => {
    expect(Button.displayName).toBe("Button");
  });
});