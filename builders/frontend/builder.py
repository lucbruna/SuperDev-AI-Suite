"""Frontend Builder — generates React/Next.js/TypeScript project scaffolding."""

from __future__ import annotations

import json
import time
from typing import Any

from ..base import (
    ApiType, BaseBuilder, BuildConfig, BuildResult, FrameworkType,
    GeneratedFile,
)


class FrontendBuilder(BaseBuilder):
    name = "frontend"
    description = "Generates frontend project scaffolding (React, Next.js, Vue, Svelte)"
    framework = FrameworkType.REACT

    async def build(self, config: BuildConfig) -> BuildResult:
        start = time.time()
        slug = config.project_slug
        files: list[GeneratedFile] = []

        try:
            if config.framework in (FrameworkType.NEXTJS,):
                files = self._generate_nextjs(config, slug)
            elif config.framework in (FrameworkType.VUE,):
                files = self._generate_vue(config, slug)
            elif config.framework in (FrameworkType.SVELTE,):
                files = self._generate_svelte(config, slug)
            else:
                files = self._generate_react(config, slug)

            elapsed_ms = round((time.time() - start) * 1000, 2)
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                total_files=len(files),
                files=files,
                build_duration_ms=elapsed_ms,
            )
        except Exception as e:
            return BuildResult(
                builder_name=self.name,
                project_name=config.project_name,
                project_slug=slug,
                error=str(e),
                build_duration_ms=round((time.time() - start) * 1000, 2),
            )

    def _generate_react(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        # package.json
        pkg = {
            "name": slug,
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "lint": "eslint .",
            },
            "dependencies": {
                "react": "^18.3.0",
                "react-dom": "^18.3.0",
                "react-router-dom": "^6.22.0",
            },
            "devDependencies": {
                "@types/react": "^18.3.0",
                "@types/react-dom": "^18.3.0",
                "@vitejs/plugin-react": "^4.2.0",
                "typescript": "^5.4.0",
                "vite": "^5.2.0",
                "eslint": "^8.57.0",
            },
        }
        if config.api_type == ApiType.REST:
            pkg["dependencies"]["axios"] = "^1.6.0"
        elif config.api_type == ApiType.GRAPHQL:
            pkg["dependencies"]["@apollo/client"] = "^3.9.0"
            pkg["dependencies"]["graphql"] = "^16.8.0"

        files.append(self._make_file(
            f"{slug}/package.json",
            json.dumps(pkg, indent=2) + "\n",
            language="json",
        ))

        # tsconfig.json
        files.append(self._make_file(
            f"{slug}/tsconfig.json",
            json.dumps({
                "compilerOptions": {
                    "target": "ES2020",
                    "useDefineForClassFields": True,
                    "lib": ["ES2020", "DOM", "DOM.Iterable"],
                    "module": "ESNext",
                    "skipLibCheck": True,
                    "moduleResolution": "bundler",
                    "allowImportingTsExtensions": True,
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx",
                    "strict": True,
                },
                "include": ["src"],
            }, indent=2) + "\n",
            language="json",
        ))

        # vite.config.ts
        files.append(self._make_file(
            f"{slug}/vite.config.ts",
            '''import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
});
''',
            language="typescript",
        ))

        # index.html
        files.append(self._make_file(
            f"{slug}/index.html",
            f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{config.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
            language="html",
        ))

        # src/main.tsx
        files.append(self._make_file(
            f"{slug}/src/main.tsx",
            '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
''',
            language="typescript",
        ))

        # src/App.tsx
        files.append(self._make_file(
            f"{slug}/src/App.tsx",
            f'''import {{ Routes, Route }} from "react-router-dom";

function Home() {{
  return (
    <div style={{ padding: "2rem", textAlign: "center" }}>
      <h1>{config.project_name}</h1>
      <p>Frontend built with React + TypeScript</p>
    </div>
  );
}}

export default function App() {{
  return (
    <Routes>
      <Route path="/" element={{<Home />}} />
    </Routes>
  );
}}
''',
            language="typescript",
        ))

        # src/index.css
        files.append(self._make_file(
            f"{slug}/src/index.css",
            '''* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
''',
            language="css",
        ))

        # src/api.ts (REST client)
        if config.api_type == ApiType.REST:
            api_url = config.extra_config.get("api_url", "http://localhost:8000")
            files.append(self._make_file(
                f"{slug}/src/api.ts",
                f'''import axios from "axios";

const api = axios.create({{
  baseURL: "{api_url}",
  headers: {{ "Content-Type": "application/json" }},
}});

export default api;
''',
                language="typescript",
            ))

        if config.include_docker:
            files.append(self._make_file(
                f"{slug}/Dockerfile",
                f'''FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
''',
                language="dockerfile",
            ))

        if config.include_tests:
            files.append(self._make_file(
                f"{slug}/src/App.test.tsx",
                '''import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import App from "./App";

test("renders the app", () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
});
''',
                language="typescript",
            ))

        # .gitignore
        files.append(self._make_file(
            f"{slug}/.gitignore",
            "node_modules/\ndist/\n.env\n",
            language="ini",
        ))

        return files

    def _generate_nextjs(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        # package.json
        pkg = {
            "name": slug,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
            },
            "dependencies": {
                "next": "^14.2.0",
                "react": "^18.3.0",
                "react-dom": "^18.3.0",
            },
            "devDependencies": {
                "typescript": "^5.4.0",
                "@types/node": "^20.12.0",
                "@types/react": "^18.3.0",
                "@types/react-dom": "^18.3.0",
            },
        }
        files.append(self._make_file(
            f"{slug}/package.json",
            json.dumps(pkg, indent=2) + "\n",
            language="json",
        ))

        files.append(self._make_file(
            f"{slug}/next.config.ts",
            '''import type { NextConfig } from "next";

const nextConfig: NextConfig = {};
export default nextConfig;
''',
            language="typescript",
        ))

        files.append(self._make_file(
            f"{slug}/app/layout.tsx",
            f'''import type {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{config.project_name}",
}};

export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}
''',
            language="typescript",
        ))

        files.append(self._make_file(
            f"{slug}/app/page.tsx",
            f'''export default function Home() {{
  return (
    <main style={{ padding: "2rem", textAlign: "center" }}>
      <h1>{config.project_name}</h1>
      <p>Frontend built with Next.js</p>
    </main>
  );
}}
''',
            language="typescript",
        ))

        return files

    def _generate_vue(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        pkg = {
            "name": slug,
            "private": True,
            "version": "0.1.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview",
            },
            "dependencies": {
                "vue": "^3.4.0",
                "vue-router": "^4.3.0",
            },
            "devDependencies": {
                "@vitejs/plugin-vue": "^5.0.0",
                "typescript": "^5.4.0",
                "vite": "^5.2.0",
                "vue-tsc": "^2.0.0",
            },
        }
        files.append(self._make_file(
            f"{slug}/package.json",
            json.dumps(pkg, indent=2) + "\n",
            language="json",
        ))

        files.append(self._make_file(
            f"{slug}/src/App.vue",
            f'''<script setup lang="ts">
const title = "{config.project_name}"
</script>

<template>
  <div style="padding: 2rem; text-align: center">
    <h1>{{{{ title }}}}</h1>
    <p>Frontend built with Vue 3</p>
  </div>
</template>
''',
            language="html",
        ))

        return files

    def _generate_svelte(self, config: BuildConfig, slug: str) -> list[GeneratedFile]:
        files: list[GeneratedFile] = []

        pkg = {
            "name": slug,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "vite dev",
                "build": "vite build",
                "preview": "vite preview",
            },
            "dependencies": {},
            "devDependencies": {
                "@sveltejs/vite-plugin-svelte": "^3.1.0",
                "svelte": "^4.2.0",
                "typescript": "^5.4.0",
                "vite": "^5.2.0",
            },
        }
        files.append(self._make_file(
            f"{slug}/package.json",
            json.dumps(pkg, indent=2) + "\n",
            language="json",
        ))

        files.append(self._make_file(
            f"{slug}/src/App.svelte",
            f'''<script lang="ts">
  let title = "{config.project_name}";
</script>

<h1>{{title}}</h1>
<p>Frontend built with Svelte</p>
''',
            language="html",
        ))

        return files
