# First Project

## Create a Project

```bash
superdev init my-app --template react
cd my-app
```

## Project Structure

```
my-app/
  src/
    App.tsx
    main.tsx
    index.css
  package.json
  tsconfig.json
  vite.config.ts
```

## Start Development

```bash
npm install
npm run dev
```

Visit http://localhost:3000.

## Connect to Backend

```bash
# In another terminal
superdev init my-api --template fastapi
cd my-api
superdev dev
```

The React app is configured to proxy API requests to the backend.
