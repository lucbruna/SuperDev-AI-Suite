import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Input } from "@/components/inputs/Input";

describe("Input", () => {
  it("renders with label", () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("renders input element", () => {
    render(<Input label="Name" />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("shows error message", () => {
    render(<Input label="Email" error="Invalid email address" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Invalid email address");
  });

  it("sets aria-invalid when error is present", () => {
    render(<Input label="Email" error="Required" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("does not set aria-invalid when no error", () => {
    render(<Input label="Email" />);
    expect(screen.getByRole("textbox")).not.toHaveAttribute("aria-invalid");
  });

  it("links error to input via aria-describedby", () => {
    render(<Input label="Email" error="Required" />);
    const input = screen.getByRole("textbox");
    const errorId = input.getAttribute("aria-describedby");
    expect(errorId).toMatch(/email-error/);
    expect(screen.getByRole("alert")).toHaveAttribute("id", errorId);
  });

  it("handles value change", async () => {
    const handleChange = vi.fn();
    const user = userEvent.setup();
    render(<Input label="Name" onChange={handleChange} />);
    await user.type(screen.getByRole("textbox"), "a");
    expect(handleChange).toHaveBeenCalled();
  });

  it("displays the correct value", () => {
    render(<Input label="Name" value="John" readOnly />);
    expect(screen.getByRole("textbox")).toHaveValue("John");
  });

  it("renders hint text when no error", () => {
    render(<Input label="Password" hint="At least 8 characters" />);
    expect(screen.getByText("At least 8 characters")).toBeInTheDocument();
  });

  it("does not render hint when error is present", () => {
    render(<Input label="Password" hint="At least 8 characters" error="Too short" />);
    expect(screen.queryByText("At least 8 characters")).not.toBeInTheDocument();
  });

  it("renders left icon", () => {
    render(<Input label="Search" leftIcon={<span data-testid="left-icon" />} />);
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("renders right icon", () => {
    render(<Input label="Search" rightIcon={<span data-testid="right-icon" />} />);
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("generates id from label", () => {
    render(<Input label="Full Name" />);
    expect(screen.getByLabelText("Full Name")).toHaveAttribute("id", "full-name");
  });

  it("uses custom id when provided", () => {
    render(<Input label="Email" id="custom-email" />);
    expect(screen.getByLabelText("Email")).toHaveAttribute("id", "custom-email");
  });

  it("disables input", () => {
    render(<Input label="Email" disabled />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("sets input type", () => {
    render(<Input label="Password" type="password" />);
    expect(screen.getByLabelText("Password")).toHaveAttribute("type", "password");
  });

  it("applies container class name", () => {
    const { container } = render(<Input label="Name" containerClassName="custom-container" />);
    expect(container.querySelector(".custom-container")).toBeInTheDocument();
  });

  it("sets display name", () => {
    expect(Input.displayName).toBe("Input");
  });
});