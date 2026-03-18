import { format, formatDistanceToNow, parseISO } from "date-fns";

/** Format an ISO timestamp to a short time string (e.g. "2:30 PM"). */
export function formatTime(iso: string): string {
  return format(parseISO(iso), "h:mm a");
}

/** Format an ISO timestamp to a relative string (e.g. "3 minutes ago"). */
export function formatRelative(iso: string): string {
  return formatDistanceToNow(parseISO(iso), { addSuffix: true });
}

/** Format an ISO timestamp to a full date/time (e.g. "Mar 18, 2026 2:30 PM"). */
export function formatDateTime(iso: string): string {
  return format(parseISO(iso), "MMM d, yyyy h:mm a");
}

/** Truncate a string to a maximum length, adding ellipsis if needed. */
export function truncate(text: string, maxLength = 60): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "…";
}