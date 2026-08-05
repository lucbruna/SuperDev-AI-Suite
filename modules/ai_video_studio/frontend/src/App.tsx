import { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { useAppStore } from '@/store';
import { applyTheme, getInitialTheme, persistTheme } from '@/theme';
import AppRoutes from '@/router';

export default function App() {
  const theme = useAppStore((state) => state.theme);
  const setTheme = useAppStore((state) => state.setTheme);

  // Apply the user's persisted/system theme on first paint.
  useEffect(() => {
    setTheme(getInitialTheme());
  }, [setTheme]);

  // Keep the document theme in sync with the store.
  useEffect(() => {
    applyTheme(theme);
    persistTheme(theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
