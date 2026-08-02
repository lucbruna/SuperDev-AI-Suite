import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Input } from "@/components/inputs/Input";
import { Select } from "@/components/inputs/Select";

describe("Input", () => {
  it("renders an input element", () => {
    render(<Input />);
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("renders with placeholder", () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText("Enter text")).toBeInTheDocument();
  });

  it("renders with label", () => {
    render(<Input label="Email" />);
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("generates id from label", () => {
    render(<Input label="First Name" />);
    const input = screen.getByLabelText("First Name");
    expect(input).toHaveAttribute("id", "first-name");
  });

  it("uses custom id when provided", () => {
    render(<Input id="custom-id" label="Name" />);
    expect(screen.getByLabelText("Name")).toHaveAttribute("id", "custom-id");
  });

  it("renders error message", () => {
    render(<Input label="Email" error="Invalid email" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Invalid email");
  });

  it("sets aria-invalid when error is present", () => {
    render(<Input error="Required" />);
    expect(screen.getByRole("textbox")).toHaveAttribute("aria-invalid", "true");
  });

  it("does not set aria-invalid when no error", () => {
    render(<Input />);
    expect(screen.getByRole("textbox")).not.toHaveAttribute("aria-invalid");
  });

  it("renders hint when no error", () => {
    render(<Input hint="This is a hint" />);
    expect(screen.getByText("This is a hint")).toBeInTheDocument();
  });

  it("hides hint when error is present", () => {
    render(<Input hint="This is a hint" error="Error occurred" />);
    expect(screen.queryByText("This is a hint")).not.toBeInTheDocument();
  });

  it("handles value changes", () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} />);
    fireEvent.change(screen.getByRole("textbox"), { target: { value: "test" } });
    expect(handleChange).toHaveBeenCalled();
  });

  it("can be disabled", () => {
    render(<Input disabled />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });

  it("renders left icon", () => {
    render(<Input leftIcon={<span data-testid="left-icon">🔍</span>} />);
    expect(screen.getByTestId("left-icon")).toBeInTheDocument();
  });

  it("renders right icon", () => {
    render(<Input rightIcon={<span data-testid="right-icon">✓</span>} />);
    expect(screen.getByTestId("right-icon")).toBeInTheDocument();
  });

  it("passes through HTML input attributes", () => {
    const { container } = render(<Input type="password" maxLength={20} />);
    const input = container.querySelector("input") as HTMLInputElement;
    expect(input).toHaveAttribute("type", "password");
    expect(input).toHaveAttribute("maxLength", "20");
  });

  it("forwards ref", () => {
    const ref = { current: null };
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });
});

describe("Select", () => {
  const options = [
    { value: "us", label: "United States" },
    { value: "br", label: "Brazil" },
    { value: "uk", label: "United Kingdom" },
  ];

  it("renders a select element", () => {
    render(<Select options={options} />);
    expect(screen.getByRole("combobox")).toBeInTheDocument();
  });

  it("renders all options", () => {
    render(<Select options={options} />);
    expect(screen.getByText("United States")).toBeInTheDocument();
    expect(screen.getByText("Brazil")).toBeInTheDocument();
    expect(screen.getByText("United Kingdom")).toBeInTheDocument();
  });

  it("renders with label", () => {
    render(<Select options={options} label="Country" />);
    expect(screen.getByLabelText("Country")).toBeInTheDocument();
  });

  it("handles value changes", () => {
    const handleChange = vi.fn();
    render(<Select options={options} onChange={handleChange} />);
    fireEvent.change(screen.getByRole("combobox"), { target: { value: "br" } });
    expect(handleChange).toHaveBeenCalled();
  });

  it("can be disabled", () => {
    render(<Select options={options} disabled />);
    expect(screen.getByRole("combobox")).toBeDisabled();
  });

  it("renders error message", () => {
    render(<Select options={options} error="Required field" />);
    expect(screen.getByRole("alert")).toHaveTextContent("Required field");
  });

  it("renders placeholder option when provided", () => {
    render(<Select options={options} placeholder="Select a country" />);
    expect(screen.getByText("Select a country")).toBeInTheDocument();
  });

  it("sets value correctly", () => {
    render(<Select options={options} value="uk" />);
    expect(screen.getByRole("combobox")).toHaveValue("uk");
  });
});
