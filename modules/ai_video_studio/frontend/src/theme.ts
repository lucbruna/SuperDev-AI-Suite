import type { ThemeName } from '@/types';
import type { ThemeDefinition } from '../themes/types';
import DarkEnterprise from '../themes/DarkEnterprise';
import DarkBlue from '../themes/DarkBlue';
import DarkGreen from '../themes/DarkGreen';
import DarkPurple from '../themes/DarkPurple';
import LightEnterprise from '../themes/LightEnterprise';
import HighContrast from '../themes/HighContrast';

export const THEMES: Record<ThemeName, ThemeDefinition> = {
  'dark-enterprise': DarkEnterprise,
  'dark-blue': DarkBlue,
  'dark-green': DarkGreen,
  'dark-purple': DarkPurple,
  'light-enterprise': LightEnterprise,
  'high-contrast': HighContrast,
};

export const THEME_OPTIONS: ThemeDefinition[] = Object.values(THEMES);

export function applyTheme(name: ThemeName): void {
  const theme = THEMES[name];
  if (!theme) return;
  const root = document.documentElement;
  root.setAttribute('data-theme', theme.dark ? 'dark' : 'light');
  for (const [key, value] of Object.entries(theme.colors)) {
    root.style.setProperty(`--color-${key}`, value);
  }
}

export function getInitialTheme(): ThemeName {
  try {
    const saved = window.localStorage.getItem('studio-theme');
    if (saved && Object.prototype.hasOwnProperty.call(THEMES, saved)) {
      return saved as ThemeName;
    }
  } catch {
    /* ignore storage errors */
  }
  if (typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light-enterprise';
  }
  return 'dark-enterprise';
}

export function persistTheme(name: ThemeName): void {
  try {
    window.localStorage.setItem('studio-theme', name);
  } catch {
    /* ignore storage errors */
  }
}
