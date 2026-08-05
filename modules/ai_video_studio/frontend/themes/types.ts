import type { ThemeName } from '../src/types';

export interface ThemeColors {
  /** App background */
  surface: string;
  /** Raised surfaces: cards, sidebars, headers */
  panel: string;
  /** Hairline borders and dividers */
  border: string;
  /** Brand / action color */
  primary: string;
  /** Secondary highlight color */
  accent: string;
  /** De-emphasized text and disabled fills */
  muted: string;
  /** Primary text */
  content: string;
  /** Secondary text */
  subtle: string;
}

export interface ThemeDefinition {
  name: ThemeName;
  label: string;
  dark: boolean;
  /** RGB triplets without parens, e.g. '13 17 23' (consumed as rgb(var(--color-X) / alpha)) */
  colors: ThemeColors;
}
