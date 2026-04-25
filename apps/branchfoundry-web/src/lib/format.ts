import { formatDistanceToNowStrict, parseISO } from "date-fns";

export function formatRelative(iso: string | null | undefined): string {
  if (!iso) return "never";
  try {
    return `${formatDistanceToNowStrict(parseISO(iso))} ago`;
  } catch {
    return iso;
  }
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "-";
  try {
    return parseISO(iso).toISOString().slice(0, 10);
  } catch {
    return iso;
  }
}

export function shortSha(sha: string | null | undefined, len = 8): string {
  if (!sha) return "";
  return sha.slice(0, len);
}
