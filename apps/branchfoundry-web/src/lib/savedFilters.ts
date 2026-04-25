import { useCallback, useEffect, useState } from "react";

/** Simple localStorage-backed persistent state hook. */
export function usePersistentState<T>(key: string, fallback: T): [T, (next: T) => void] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window === "undefined") return fallback;
    try {
      const raw = window.localStorage.getItem(key);
      return raw === null ? fallback : (JSON.parse(raw) as T);
    } catch {
      return fallback;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* quota exceeded, ignore */
    }
  }, [key, value]);

  const set = useCallback((next: T) => setValue(next), []);
  return [value, set];
}
