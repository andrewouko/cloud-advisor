"use client";

import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { HistorySidebar } from "@/components/history/HistorySidebar";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { ErrorBanner } from "@/components/ui/ErrorBanner";
import { useChat } from "@/hooks/useChat";
import { useHistory } from "@/hooks/useHistory";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);

  const chat = useChat();
  const history = useHistory();

  const handleSend = (question: string) => {
    setActiveHistoryId(null);
    chat.sendMessage(question);
  };

  return (
    <div className="relative flex h-dvh flex-col overflow-hidden bg-white">
      {/* Error banner */}
      <ErrorBanner message={chat.error} />

      {/* Header */}
      <Header onToggleSidebar={() => setSidebarOpen((o) => !o)} />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — desktop (always visible) */}
        <div className="hidden w-72 shrink-0 lg:block">
          <HistorySidebar
            history={history.history}
            isLoading={history.isLoading}
            activeId={activeHistoryId}
            onSelect={(item) => {
              setActiveHistoryId(item.id);
              chat.loadFromHistory(item);
            }}
            onClear={() => {
              history.clearHistory();
              chat.clearChat();
              setActiveHistoryId(null);
            }}
            isClearing={history.isClearing}
          />
        </div>

        {/* Sidebar — mobile (slide-in drawer) */}
        {sidebarOpen && (
          <>
            <div
              className="fixed inset-0 z-40 bg-black/30 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <div className="animate-slide-in-left fixed inset-y-0 left-0 z-50 w-72 lg:hidden">
              <HistorySidebar
                history={history.history}
                isLoading={history.isLoading}
                activeId={activeHistoryId}
                onSelect={(item) => {
                  setActiveHistoryId(item.id);
                  chat.loadFromHistory(item);
                  setSidebarOpen(false);
                }}
                onClear={() => {
                  history.clearHistory();
                  chat.clearChat();
                  setActiveHistoryId(null);
                }}
                isClearing={history.isClearing}
                onClose={() => setSidebarOpen(false)}
              />
            </div>
          </>
        )}

        {/* Main chat area */}
        <ChatWindow
          messages={chat.messages}
          isLoading={chat.isLoading}
          onSend={handleSend}
        />
      </div>
    </div>
  );
}