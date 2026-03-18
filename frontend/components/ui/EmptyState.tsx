"use client";

const SUGGESTIONS = [
  "How do I migrate to Google Workspace?",
  "What are cloud security best practices?",
  "Compare AWS vs GCP for startups",
];

interface EmptyStateProps {
  onSuggestionClick: (question: string) => void;
}

export function EmptyState({ onSuggestionClick }: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-4 text-center">
      {/* Icon */}
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-100 text-brand-600">
        <svg
          className="h-8 w-8"
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

      <div>
        <h2 className="text-xl font-semibold text-gray-900">CloudAdvisor</h2>
        <p className="mt-1 text-sm text-gray-500">
          Your AI Cloud &amp; IT Consultant
        </p>
      </div>

      <div className="flex flex-col gap-2">
        <p className="text-xs font-medium tracking-wide text-gray-400 uppercase">
          Try asking
        </p>
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestionClick(s)}
            className="rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-left text-sm text-gray-700 shadow-sm transition-all hover:border-brand-300 hover:bg-brand-50 hover:shadow-md"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}