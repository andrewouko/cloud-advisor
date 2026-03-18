"use client";

/** Reusable shimmer / skeleton loading primitive.
 *
 *  Uses a CSS gradient animation that sweeps left→right, giving a
 *  polished "content is loading" feel. Pass `className` to control
 *  the shape (height, width, rounded corners).
 */
export function Shimmer({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-shimmer rounded-md bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%] ${className}`}
    />
  );
}

/** Skeleton block that mimics a chat message bubble. */
export function MessageSkeleton() {
  return (
    <div className="flex flex-col gap-3 p-4">
      {/* User message skeleton — right aligned */}
      <div className="flex justify-end">
        <Shimmer className="h-10 w-48 rounded-2xl" />
      </div>
      {/* Assistant message skeleton — left aligned */}
      <div className="flex flex-col gap-2">
        <Shimmer className="h-4 w-12 rounded" />
        <Shimmer className="h-24 w-full max-w-lg rounded-2xl" />
      </div>
    </div>
  );
}

/** Skeleton for a single history sidebar item. */
export function HistoryItemSkeleton() {
  return (
    <div className="flex flex-col gap-1.5 px-3 py-2.5">
      <Shimmer className="h-4 w-3/4 rounded" />
      <Shimmer className="h-3 w-1/3 rounded" />
    </div>
  );
}

/** Skeleton group for the history sidebar (shows several items). */
export function HistorySidebarSkeleton() {
  return (
    <div className="flex flex-col gap-1">
      {Array.from({ length: 5 }).map((_, i) => (
        <HistoryItemSkeleton key={i} />
      ))}
    </div>
  );
}