import { useEffect, useCallback, useRef } from "react";

type KeyCombo = {
  key: string;
  ctrl?: boolean;
  meta?: boolean;
  shift?: boolean;
  alt?: boolean;
};

type KeyMap = Record<string, KeyCombo>;

interface UseKeyboardOptions {
  keyMap: KeyMap;
  onShortcut: (action: string) => void;
  enabled?: boolean;
  preventDefault?: boolean;
}

export function useKeyboard({
  keyMap,
  onShortcut,
  enabled = true,
  preventDefault = true,
}: UseKeyboardOptions) {
  const onShortcutRef = useRef(onShortcut);
  onShortcutRef.current = onShortcut;

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      for (const [action, combo] of Object.entries(keyMap)) {
        const match =
          event.key.toLowerCase() === combo.key.toLowerCase() &&
          !!event.ctrlKey === !!combo.ctrl &&
          !!event.metaKey === !!combo.meta &&
          !!event.shiftKey === !!combo.shift &&
          !!event.altKey === !!combo.alt;

        if (match) {
          if (preventDefault) {
            event.preventDefault();
            event.stopPropagation();
          }
          onShortcutRef.current(action);
          return;
        }
      }
    },
    [keyMap, enabled, preventDefault],
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}

export function useKeyboardShortcut(
  combo: KeyCombo,
  callback: () => void,
  enabled: boolean = true,
) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  useEffect(() => {
    if (!enabled) return;

    const handler = (event: KeyboardEvent) => {
      const match =
        event.key.toLowerCase() === combo.key.toLowerCase() &&
        !!event.ctrlKey === !!combo.ctrl &&
        !!event.metaKey === !!combo.meta &&
        !!event.shiftKey === !!combo.shift &&
        !!event.altKey === !!combo.alt;

      if (match) {
        event.preventDefault();
        event.stopPropagation();
        callbackRef.current();
      }
    };

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [combo, enabled]);
}
