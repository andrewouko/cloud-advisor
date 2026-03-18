"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage as ChatMessageType } from "@/types";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { EmptyState } from "@/components/ui/EmptyState";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading: boolean;
  onSend: (question: string) => void;
}

export function ChatWindow({ messages, isLoading, onSend }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <EmptyState onSuggestionClick={onSend} />
        ) : (
          <div className="mx-auto max-w-3xl py-4">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <ChatInput onSend={onSend} disabled={isLoading} />
    </div>
  );
}