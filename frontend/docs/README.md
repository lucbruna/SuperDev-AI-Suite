# Frontend Documentation

## Architecture

- React 18 + Next.js 14
- TypeScript 5.3
- Tailwind CSS 3
- Zustand for state management
- React Query for data fetching

## Directory Structure

```
src/
  app/          # Next.js app directory
  components/   # Reusable UI components
  pages/        # Page components
  hooks/        # Custom React hooks
  stores/       # Zustand stores
  api/          # API client functions
  types/        # TypeScript types
  utils/        # Utility functions
  styles/       # Global styles
```

## Development

```bash
npm install
npm run dev
```

## Testing

```bash
npm test          # Unit tests
npm run test:e2e  # E2E tests
```
