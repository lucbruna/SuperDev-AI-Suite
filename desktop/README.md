# SuperDev Desktop

Desktop application for SuperDev AI Suite.

## Platform

- **Framework**: Electron
- **Language**: TypeScript
- **UI**: React

## Features

- Full IDE experience
- Local file editing
- Terminal integration
- Git integration
- Agent console

## Setup

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Structure

```
src/
  main/           # Electron main process
    index.ts
    ipc.ts
  renderer/       # React UI
    App.tsx
    components/
    pages/
```
