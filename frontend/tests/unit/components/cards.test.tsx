import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Card, CardHeader, CardBody, CardFooter } from "@/components/cards/Card";
import { StatCard } from "@/components/cards/StatCard";

describe("Card", () => {
  it("renders children", () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText("Card content")).toBeInTheDocument();
  });

  it("renders header when provided", () => {
    render(<Card header={<h2>Header</h2>}>Content</Card>);
    expect(screen.getByText("Header")).toBeInTheDocument();
  });

  it("renders footer when provided", () => {
    render(<Card footer={<p>Footer</p>}>Content</Card>);
    expect(screen.getByText("Footer")).toBeInTheDocument();
  });

  it("does not render header when not provided", () => {
    render(<Card>Content</Card>);
    expect(screen.queryByRole("heading")).not.toBeInTheDocument();
  });

  it("applies padding sm", () => {
    render(<Card padding="sm">Padded</Card>);
    const content = screen.getByText("Padded");
    expect(content.className).toContain("p-3");
  });

  it("applies padding md by default", () => {
    render(<Card>Default padding</Card>);
    const content = screen.getByText("Default padding");
    expect(content.className).toContain("p-5");
  });

  it("applies padding lg", () => {
    render(<Card padding="lg">Large padding</Card>);
    const content = screen.getByText("Large padding");
    expect(content.className).toContain("p-7");
  });

  it("applies padding none", () => {
    render(<Card padding="none">No padding</Card>);
    const content = screen.getByText("No padding");
    expect(content.className).not.toContain("p-");
  });

  it("applies hover effect", () => {
    const { container } = render(<Card hover>Hoverable</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("hover:shadow-md");
  });

  it("applies custom className", () => {
    const { container } = render(<Card className="custom-class">Custom</Card>);
    expect((container.firstChild as HTMLElement).className).toContain("custom-class");
  });

  it("has border and rounded styling", () => {
    const { container } = render(<Card>Styled</Card>);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain("rounded-xl");
    expect(card.className).toContain("border");
  });
});

describe("CardHeader", () => {
  it("renders children", () => {
    render(
      <Card>
        <CardHeader>
          <span>Title</span>
          <span>Action</span>
        </CardHeader>
      </Card>,
    );
    expect(screen.getByText("Title")).toBeInTheDocument();
    expect(screen.getByText("Action")).toBeInTheDocument();
  });
});

describe("CardBody", () => {
  it("renders children", () => {
    render(
      <Card>
        <CardBody>
          <p>Body text</p>
        </CardBody>
      </Card>,
    );
    expect(screen.getByText("Body text")).toBeInTheDocument();
  });
});

describe("CardFooter", () => {
  it("renders children", () => {
    render(
      <Card>
        <CardFooter>
          <button>Save</button>
          <button>Cancel</button>
        </CardFooter>
      </Card>,
    );
    expect(screen.getByText("Save")).toBeInTheDocument();
    expect(screen.getByText("Cancel")).toBeInTheDocument();
  });
});

describe("StatCard", () => {
  const icon = <span data-testid="stat-icon">📊</span>;

  it("renders value and label", () => {
    render(<StatCard icon={icon} value={42} label="Total Projects" />);
    expect(screen.getByText("42")).toBeInTheDocument();
    expect(screen.getByText("Total Projects")).toBeInTheDocument();
  });

  it("renders string value", () => {
    render(<StatCard icon={icon} value="$1,234" label="Revenue" />);
    expect(screen.getByText("$1,234")).toBeInTheDocument();
  });

  it("renders icon", () => {
    render(<StatCard icon={icon} value={0} label="Items" />);
    expect(screen.getByTestId("stat-icon")).toBeInTheDocument();
  });

  it("renders trend when provided", () => {
    render(
      <StatCard
        icon={icon}
        value={100}
        label="Users"
        trend={{ value: "+12%", direction: "up" }}
      />,
    );
    expect(screen.getByText("+12%")).toBeInTheDocument();
  });

  it("renders upward trend with correct arrow", () => {
    render(
      <StatCard
        icon={icon}
        value={100}
        label="Users"
        trend={{ value: "+5%", direction: "up" }}
      />,
    );
    expect(screen.getByText("↑")).toBeInTheDocument();
  });

  it("renders downward trend with correct arrow", () => {
    render(
      <StatCard
        icon={icon}
        value={50}
        label="Errors"
        trend={{ value: "-3%", direction: "down" }}
      />,
    );
    expect(screen.getByText("↓")).toBeInTheDocument();
  });

  it("renders neutral trend", () => {
    render(
      <StatCard
        icon={icon}
        value={0}
        label="Stable"
        trend={{ value: "0%", direction: "neutral" }}
      />,
    );
    expect(screen.getByText("→")).toBeInTheDocument();
  });

  it("does not render trend when not provided", () => {
    render(<StatCard icon={icon} value={0} label="No trend" />);
    expect(screen.queryByText("↑")).not.toBeInTheDocument();
    expect(screen.queryByText("↓")).not.toBeInTheDocument();
  });

  it("applies custom className", () => {
    const { container } = render(
      <StatCard icon={icon} value={0} label="Custom" className="custom-stat" />,
    );
    expect((container.firstChild as HTMLElement).className).toContain("custom-stat");
  });
});
