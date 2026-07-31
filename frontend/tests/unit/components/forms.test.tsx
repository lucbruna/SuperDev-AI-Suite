import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { FormField } from "@/components/forms/FormField";

describe("FormField", () => {
  it("renders children", () => {
    render(
      <FormField>
        <input />
      </FormField>,
    );
    expect(screen.getByRole("textbox")).toBeInTheDocument();
  });

  it("renders label when provided", () => {
    render(
      <FormField label="Username">
        <input />
      </FormField>,
    );
    expect(screen.getByText("Username")).toBeInTheDocument();
  });

  it("does not render label when not provided", () => {
    render(
      <FormField>
        <input />
      </FormField>,
    );
    expect(screen.queryByRole("label")).not.toBeInTheDocument();
  });

  it("links label to field via htmlFor", () => {
    render(
      <FormField label="Email">
        <input />
      </FormField>,
    );
    const label = screen.getByText("Email");
    expect(label.tagName).toBe("LABEL");
    expect(label).toHaveAttribute("for", "email");
  });

  it("renders error message", () => {
    render(
      <FormField label="Name" error="Required field">
        <input />
      </FormField>,
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Required field");
  });

  it("does not render error when not provided", () => {
    render(
      <FormField label="Name">
        <input />
      </FormField>,
    );
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders hint when no error", () => {
    render(
      <FormField label="Password" hint="At least 8 characters">
        <input type="password" />
      </FormField>,
    );
    expect(screen.getByText("At least 8 characters")).toBeInTheDocument();
  });

  it("hides hint when error is present", () => {
    render(
      <FormField label="Password" hint="At least 8 chars" error="Too short">
        <input type="password" />
      </FormField>,
    );
    expect(screen.queryByText("At least 8 characters")).not.toBeInTheDocument();
  });

  it("shows required asterisk when required", () => {
    const { container } = render(
      <FormField label="Email" required>
        <input />
      </FormField>,
    );
    const label = container.querySelector("label");
    expect(label?.className).toContain("after:content-['*']");
  });

  it("does not show asterisk when not required", () => {
    const { container } = render(
      <FormField label="Email">
        <input />
      </FormField>,
    );
    const label = container.querySelector("label");
    expect(label?.className).not.toContain("after:content-['*']");
  });

  it("applies custom className", () => {
    const { container } = render(
      <FormField className="custom-field">
        <input />
      </FormField>,
    );
    expect((container.firstChild as HTMLElement).className).toContain("custom-field");
  });

  it("applies custom labelClassName", () => {
    render(
      <FormField label="Test" labelClassName="custom-label">
        <input />
      </FormField>,
    );
    const label = screen.getByText("Test");
    expect(label.className).toContain("custom-label");
  });

  it("applies custom errorClassName", () => {
    render(
      <FormField error="Error msg" errorClassName="custom-error">
        <input />
      </FormField>,
    );
    const error = screen.getByRole("alert");
    expect(error.className).toContain("custom-error");
  });

  it("has space-y-1.5 spacing", () => {
    const { container } = render(
      <FormField>
        <input />
      </FormField>,
    );
    expect((container.firstChild as HTMLElement).className).toContain("space-y-1.5");
  });
});
