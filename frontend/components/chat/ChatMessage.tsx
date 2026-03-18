"use client";

import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { ChatMessage as ChatMessageType } from "@/types";
import { formatTime } from "@/lib/utils";
import { TypingIndicator } from "./TypingIndicator";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  if (message.isLoading) {
    return <TypingIndicator />;
  }

  if (message.isError) {
    return (
      <div className="animate-fade-in flex gap-3 px-4 py-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-500">
          <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {message.content}
        </div>
      </div>
    );
  }

  if (isUser) {
    return (
      <div className="animate-fade-in flex justify-end px-4 py-2">
        <div className="flex max-w-[75%] flex-col items-end gap-1">
          <div className="rounded-2xl rounded-br-md bg-brand-600 px-4 py-2.5 text-sm text-white shadow-sm">
            {message.content}
          </div>
          <span className="text-[10px] text-gray-400">
            {formatTime(message.timestamp)}
          </span>
        </div>
      </div>
    );
  }

  // Assistant message — rendered as markdown
  return (
    <div className="animate-fade-in flex gap-3 px-4 py-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600">
        <svg
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z"
          />
        </svg>
      </div>

      <div className="flex max-w-[90%] flex-col gap-1">
        <div className="prose prose-sm max-w-none rounded-2xl rounded-tl-md border border-gray-200 bg-white px-4 py-3 shadow-sm text-[#111827]">
          <ReactMarkdown
            components={{
              code({ className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                const code = String(children).replace(/\n$/, "");

                if (match) {
                  return (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      className="!rounded-lg !text-xs"
                    >
                      {code}
                    </SyntaxHighlighter>
                  );
                }

                return (
                  <code
                    className="rounded bg-gray-200 px-1 py-0.5 text-xs"
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        <span className="text-[10px] text-gray-400">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}