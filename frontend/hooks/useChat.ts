"use client";

import { useState, useCallback } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ChatMessage, HistoryItem } from "@/types";
import { api } from "@/lib/api";

export function useChat() {
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const mutation = useMutation({
    mutationFn: (question: string) => api.query(question),
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });

  const sendMessage = useCallback(
    async (question: string) => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: question,
        timestamp: new Date().toISOString(),
      };

      const loadingMsg: ChatMessage = {
        id: "loading",
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        isLoading: true,
      };

      setMessages((prev) => [...prev, userMsg, loadingMsg]);

      try {
        const response = await mutation.mutateAsync(question);

        const assistantMsg: ChatMessage = {
          id: response.id,
          role: "assistant",
          content: response.answer,
          timestamp: response.timestamp,
        };

        // Replace loading placeholder (and remove any stale error) with the real response
        setMessages((prev) =>
          prev
            .filter((m) => !m.isError)
            .map((m) => (m.id === "loading" ? assistantMsg : m))
        );
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Something went wrong.";

        setMessages((prev) =>
          prev.map((m) =>
            m.id === "loading"
              ? { ...m, id: crypto.randomUUID(), isLoading: false, isError: true, content: message }
              : m
          )
        );
      }
    },
    [mutation]
  );

  const loadFromHistory = useCallback((item: HistoryItem) => {
    const restored: ChatMessage[] = [
      {
        id: `${item.id}-q`,
        role: "user",
        content: item.question,
        timestamp: item.timestamp,
      },
      {
        id: item.id,
        role: "assistant",
        content: item.answer,
        timestamp: item.timestamp,
      },
    ];
    setMessages(restored);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isLoading: mutation.isPending,
    error: mutation.error?.message ?? null,
    sendMessage,
    loadFromHistory,
    clearChat,
  };
}