import { useState, useEffect, createContext, useContext, ReactNode, useCallback } from 'react';
import { featureFlagsApi } from '../services/api';

interface FeatureFlagsContextType {
  flags: Record<string, boolean>;
  loading: boolean;
  evaluate: (name: string) => boolean;
  isEnabled: (name: string) => boolean;
  refresh: () => Promise<void>;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextType | undefined>(undefined);

/** Flags que garantem a UI completa mesmo se o backend estiver indisponível. */
const DEFAULT_ENABLED: Record<string, boolean> = {
  knowledge_base: true,
  plugin_marketplace: true,
  feature_flags: true,
  new_dashboard: true,
  advanced_analytics: true,
};

export function FeatureFlagsProvider({ children }: { children: ReactNode }) {
  const [flags, setFlags] = useState<Record<string, boolean>>({ ...DEFAULT_ENABLED });
  const [loading, setLoading] = useState(true);

  const fetchFlags = useCallback(async () => {
    try {
      const response = await featureFlagsApi.list();
      const flagsMap: Record<string, boolean> = { ...DEFAULT_ENABLED };
      (response.flags ?? []).forEach((flag) => {
        flagsMap[flag.name] = flag.enabled;
      });
      setFlags(flagsMap);
    } catch {
      // Backend indisponível: mantém os defaults (UI completa).
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchFlags();
  }, [fetchFlags]);

  const evaluate = (name: string) => flags[name] ?? false;
  const isEnabled = (name: string) => flags[name] ?? false;

  return (
    <FeatureFlagsContext.Provider value={{ flags, loading, evaluate, isEnabled, refresh: fetchFlags }}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

export function useFeatureFlags() {
  const context = useContext(FeatureFlagsContext);
  if (!context) {
    throw new Error('useFeatureFlags deve ser usado dentro de um FeatureFlagsProvider');
  }
  return context;
}
