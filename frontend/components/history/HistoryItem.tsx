"use client";

import type { HistoryItem as HistoryItemType } from "@/types";
import { truncate, formatRelative } from "@/lib/utils";

interface HistoryItemProps {
  item: HistoryItemType;
  isActive: boolean;
  onClick: () => void;
}

export function HistoryItem({ item, isActive, onClick }: HistoryItemProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-lg px-3 py-2.5 text-left transition-colors ${
        isActive
          ? "bg-brand-50 border border-brand-200"
          : "hover:bg-gray-100 border border-transparent"
      }`}
    >
      <p
        className={`truncate text-sm font-medium ${isActive ? "text-brand-700" : "text-gray-700"}`}
      >
        {truncate(item.question)}
      </p>
      <p className="mt-0.5 text-[11px] text-gray-400">
        {formatRelative(item.timestamp)}
      </p>
    </button>
  );
}