import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ChatMessage } from "@/components/chat/ChatMessage";
import type { ChatMessage as ChatMessageType } from "@/types";

const userMsg: ChatMessageType = {
  id: "1",
  role: "user",
  content: "How do I migrate to Google Workspace?",
  timestamp: new Date().toISOString(),
};

const assistantMsg: ChatMessageType = {
  id: "2",
  role: "assistant",
  content: "Here is a **migration guide** for Google Workspace.",
  timestamp: new Date().toISOString(),
};

describe("ChatMessage", () => {
  it("renders user message content", () => {
    render(<ChatMessage message={userMsg} />);
    expect(screen.getByText(userMsg.content)).toBeInTheDocument();
  });

  it("renders assistant message as markdown", () => {
    render(<ChatMessage message={assistantMsg} />);
    expect(screen.getByText("migration guide")).toBeInTheDocument();
  });

  it("shows loading indicator when isLoading", () => {
    const loading: ChatMessageType = {
      id: "3",
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      isLoading: true,
    };
    const { container } = render(<ChatMessage message={loading} />);
    expect(container.querySelector(".animate-bounce")).toBeInTheDocument();
  });

  it("renders error state", () => {
    const error: ChatMessageType = {
      id: "4",
      role: "assistant",
      content: "Something went wrong",
      timestamp: new Date().toISOString(),
      isError: true,
    };
    render(<ChatMessage message={error} />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });
});