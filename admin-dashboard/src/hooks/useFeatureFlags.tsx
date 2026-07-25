import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { featureFlagsApi } from '../services/api';

interface FeatureFlagsContextType {
  flags: Record<string, boolean>;
  loading: boolean;
  evaluate: (name: string, context?: Record<string, any>) => Promise<boolean>;
  refresh: () => Promise<void>;
}

const FeatureFlagsContext = createContext<FeatureFlagsContextType | undefined>(undefined);

export function FeatureFlagsProvider({ children }: { children: ReactNode }) {
  const [flags, setFlags] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  const fetchFlags = async () => {
    try {
      const response = await featureFlagsApi.list();
      const flagsMap: Record<string, boolean> = {};
      response.data.forEach((flag: any) => {
        flagsMap[flag.name] = flag.enabled;
      });
      setFlags(flagsMap);
    } catch (error) {
      console.error('Failed to fetch feature flags:', error);
    } finally {
      setLoading(false);
    }
  };

  const evaluate = async (name: string, context?: Record<string, any>): Promise<boolean> => {
    try {
      const response = await featureFlagsApi.evaluate(name, context);
      return response.data.enabled;
    } catch {
      return flags[name] || false;
    }
  };

  useEffect(() => {
    fetchFlags();
  }, []);

  return (
    <FeatureFlagsContext.Provider value={{ flags, loading, evaluate, refresh: fetchFlags }}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

export function useFeatureFlags() {
  const context = useContext(FeatureFlagsContext);
  if (!context) {
    throw new Error('useFeatureFlags must be used within a FeatureFlagsProvider');
  }
  return context;
}