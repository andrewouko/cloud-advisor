"use client";

import { useEffect, useState } from "react";

interface ErrorBannerProps {
  message: string | null;
  onDismiss?: () => void;
  autoDismissMs?: number;
}

export function ErrorBanner({
  message,
  onDismiss,
  autoDismissMs = 6000,
}: ErrorBannerProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (message) {
      setVisible(true);
      const timer = setTimeout(() => {
        setVisible(false);
        onDismiss?.();
      }, autoDismissMs);
      return () => clearTimeout(timer);
    } else {
      setVisible(false);
    }
  }, [message, autoDismissMs, onDismiss]);

  if (!visible || !message) return null;

  return (
    <div className="animate-slide-down absolute inset-x-0 top-0 z-50 mx-4 mt-4 flex items-center justify-between rounded-lg border border-red-200 bg-red-50 px-4 py-3 shadow-md">
      <div className="flex items-center gap-2">
        <svg
          className="h-5 w-5 shrink-0 text-red-500"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
            clipRule="evenodd"
          />
        </svg>
        <p className="text-sm font-medium text-red-800">{message}</p>
      </div>
      <button
        onClick={() => {
          setVisible(false);
          onDismiss?.();
        }}
        className="ml-4 text-red-400 transition-colors hover:text-red-600"
      >
        <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
          <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
        </svg>
      </button>
    </div>
  );
}
