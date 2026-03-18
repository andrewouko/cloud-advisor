import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { EmptyState } from "@/components/ui/EmptyState";

describe("EmptyState", () => {
  it("renders the CloudAdvisor heading", () => {
    render(<EmptyState onSuggestionClick={vi.fn()} />);
    expect(screen.getByText("CloudAdvisor")).toBeInTheDocument();
  });

  it("renders suggestion buttons", () => {
    render(<EmptyState onSuggestionClick={vi.fn()} />);
    const buttons = screen.getAllByRole("button");
    expect(buttons.length).toBeGreaterThanOrEqual(3);
  });

  it("calls onSuggestionClick when a suggestion is clicked", () => {
    const onClick = vi.fn();
    render(<EmptyState onSuggestionClick={onClick} />);
    const buttons = screen.getAllByRole("button");
    fireEvent.click(buttons[0]);
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});