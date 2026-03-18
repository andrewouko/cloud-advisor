"use client";

import type { HistoryItem as HistoryItemType } from "@/types";
import { HistoryItem } from "./HistoryItem";
import { HistorySidebarSkeleton } from "@/components/ui/Shimmer";

interface HistorySidebarProps {
  history: HistoryItemType[];
  isLoading: boolean;
  activeId: string | null;
  onSelect: (item: HistoryItemType) => void;
  onClear: () => void;
  isClearing: boolean;
  onClose?: () => void;
}

export function HistorySidebar({
  history,
  isLoading,
  activeId,
  onSelect,
  onClear,
  isClearing,
  onClose,
}: HistorySidebarProps) {
  return (
    <aside className="flex h-full w-full flex-col border-r border-gray-200 bg-gray-50/50">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <h2 className="text-sm font-semibold text-gray-700">History</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-200 hover:text-gray-600 lg:hidden"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </div>

      {/* List */}
      <div className="flex-1 overflow-y-auto p-2">
        {isLoading ? (
          <HistorySidebarSkeleton />
        ) : history.length === 0 ? (
          <p className="px-3 py-6 text-center text-xs text-gray-400">
            No conversations yet
          </p>
        ) : (
          <div className="flex flex-col gap-0.5">
            {history.map((item) => (
              <HistoryItem
                key={item.id}
                item={item}
                isActive={activeId === item.id}
                onClick={() => onSelect(item)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {history.length > 0 && (
        <div className="border-t border-gray-200 p-3">
          <button
            onClick={() => onClear()}
            disabled={isClearing}
            className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:bg-gray-100 disabled:opacity-50"
          >
            {isClearing ? "Clearing..." : "Clear History"}
          </button>
        </div>
      )}
    </aside>
  );
}