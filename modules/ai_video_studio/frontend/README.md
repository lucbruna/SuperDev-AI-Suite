# SuperDev AI Video Studio — Frontend (Volume 8)

Professional web interface for the AI Video Studio module. Fully separated from the
backend, organized by functionality.

## Stack

- **React 18** + **TypeScript 5** (strict)
- **Vite 5** build tooling (`npm run build` = `tsc && vite build`)
- **Tailwind CSS 3** with runtime theme tokens (CSS variables)
- **React Router 6** — lazy-loaded routes per page
- **Zustand** global store (`src/store.ts`)
- **lucide-react** icons

## Structure

```
frontend/
├── package.json / vite.config.ts / tsconfig.json / tailwind.config.js / postcss.config.js / index.html
├── public/            # static assets (favicon)
├── assets/            # brand assets (logo)
├── locales/           # i18n dictionaries (en, pt-BR)
├── themes/            # theme token definitions
├── tests/             # smoke tests (pure functions, no runner)
└── src/
    ├── main.tsx / App.tsx / router.tsx
    ├── store.ts / theme.ts / constants.ts / permissions.ts
    ├── api.ts / hooks.ts / types.ts / utils.ts / ui.tsx / index.css
    ├── layout/        # Main, Studio, Dashboard, Editor, Admin, Guest + chrome
    ├── pages/         # dashboard, editor, assets, marketplace, avatar, voice,
    │                  # render, analytics, settings, collaboration, admin
    └── components/    # timeline, preview, ai
```

## Path alias

`@/*` resolves to `src/*` (configured in `vite.config.ts` and `tsconfig.json`).

## Run

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # typecheck + production build
```
