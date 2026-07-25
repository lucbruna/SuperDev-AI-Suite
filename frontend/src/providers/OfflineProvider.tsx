"use client";

import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

interface OfflineState {
  isOnline: boolean;
  pendingChanges: number;
  sync: () => Promise<void>;
}

const OfflineContext = createContext<OfflineState>({
  isOnline: true,
  pendingChanges: 0,
  sync: async () => {},
});

export function OfflineProvider({ children }: { children: ReactNode }) {
  const [isOnline, setIsOnline] = useState(true);
  const [pendingChanges, setPendingChanges] = useState(0);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  const sync = async () => {
    if (!navigator.onLine) return;
    setPendingChanges(0);
  };

  return (
    <OfflineContext.Provider value={{ isOnline, pendingChanges, sync }}>
      {!isOnline && (
        <div className="fixed bottom-4 right-4 bg-amber-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 text-sm">
          Offline - {pendingChanges} pending changes
        </div>
      )}
      {children}
    </OfflineContext.Provider>
  );
}

export function useOffline() {
  return useContext(OfflineContext);
}