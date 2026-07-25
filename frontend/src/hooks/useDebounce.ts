import { useCallback, useEffect, useRef, useState } from "react";

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

export function useDebouncedCallback<Args extends unknown[]>(
  callback: (...args: Args) => void,
  delay: number = 300,
): (...args: Args) => void {
  const timer = useRef<ReturnType<typeof setTimeout>>();

  return useCallback(
    (...args: Args) => {
      clearTimeout(timer.current);
      timer.current = setTimeout(() => callback(...args), delay);
    },
    [callback, delay],
  );
}
