import type { ThemeDefinition } from './types';

const HighContrast: ThemeDefinition = {
  name: 'high-contrast',
  label: 'High Contrast',
  dark: true,
  colors: {
    surface: '0 0 0',
    panel: '20 20 20',
    border: '255 255 255',
    primary: '250 204 21',
    accent: '34 211 238',
    muted: '107 114 128',
    content: '255 255 255',
    subtle: '229 231 235',
  },
};

export default HighContrast;
