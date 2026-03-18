import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ChatInput } from "@/components/chat/ChatInput";

describe("ChatInput", () => {
  it("renders the input textarea", () => {
    render(<ChatInput onSend={vi.fn()} disabled={false} />);
    expect(screen.getByPlaceholderText(/ask about cloud/i)).toBeInTheDocument();
  });

  it("calls onSend with trimmed text on submit", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled={false} />);

    const textarea = screen.getByPlaceholderText(/ask about cloud/i);
    fireEvent.change(textarea, { target: { value: "  test question  " } });
    fireEvent.click(screen.getByRole("button"));

    expect(onSend).toHaveBeenCalledWith("test question");
  });

  it("disables textarea and button when disabled", () => {
    render(<ChatInput onSend={vi.fn()} disabled={true} />);
    expect(screen.getByPlaceholderText(/ask about cloud/i)).toBeDisabled();
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("does not submit empty input", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled={false} />);
    fireEvent.click(screen.getByRole("button"));
    expect(onSend).not.toHaveBeenCalled();
  });
});