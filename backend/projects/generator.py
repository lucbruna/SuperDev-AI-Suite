from typing import Any


class ProjectGenerator:
    TEMPLATES = {
        "fastapi": "generate_fastapi",
        "react": "generate_react",
        "next": "generate_next",
    }

    def generate_from_template(self, template_name: str, project_data: dict[str, Any]) -> dict[str, str]:
        method_name = self.TEMPLATES.get(template_name)
        if not method_name:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.TEMPLATES.keys())}")
        method = getattr(self, method_name)
        return method(project_data)

    def generate_fastapi(self, project_data: dict[str, Any]) -> dict[str, str]:
        name = project_data.get("name", "app")
        return {
            f"{name}/__init__.py": "",
            f"{name}/main.py": f"""from fastapi import FastAPI

app = FastAPI(title="{name}")


@app.get("/")
async def root():
    return {{"message": "Hello from {name}"}}
""",
            f"{name}/routers/__init__.py": "",
            f"{name}/models/__init__.py": "",
            f"{name}/schemas/__init__.py": "",
            f"{name}/services/__init__.py": "",
            f"{name}/core/__init__.py": "",
            f"{name}/core/config.py": f"""from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "{name}"
    debug: bool = False

    class Config:
        env_file = ".env"
""",
            "requirements.txt": "fastapi\nuvicorn[standard]\npydantic\npydantic-settings\nsqlalchemy\nasyncpg\n",
            ".env": f"APP_NAME={name}\nDEBUG=false\n",
            "Dockerfile": f'FROM python:3.12-slim\n\nWORKDIR /app\nCOPY . .\nRUN pip install -r requirements.txt\nCMD ["uvicorn", "{name}.main:app", "--host", "0.0.0.0", "--port", "8000"]\n',
        }

    def generate_react(self, project_data: dict[str, Any]) -> dict[str, str]:
        name = project_data.get("name", "my-app")
        return {
            "src/App.tsx": f"""import React from 'react';

const App: React.FC = () => {{
  return <div>{{"Hello from {name}"}}</div>;
}};

export default App;
""",
            "src/main.tsx": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
            "src/vite-env.d.ts": '/// <reference types="vite/client" />',
            "index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>"""
            + name
            + """</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
""",
            "package.json": f'{{"name":"{name}","private":true,"version":"0.1.0","type":"module","scripts":{{"dev":"vite","build":"tsc && vite build","preview":"vite preview"}},"dependencies":{{"react":"^18.2.0","react-dom":"^18.2.0"}},"devDependencies":{{"@types/react":"^18.2.0","@types/react-dom":"^18.2.0","@vitejs/plugin-react":"^4.0.0","typescript":"^5.0.0","vite":"^5.0.0"}}}}',
            "tsconfig.json": '{"compilerOptions":{"target":"ES2020","useDefineForClassFields":true,"lib":["ES2020","DOM","DOM.Iterable"],"module":"ESNext","skipLibCheck":true,"moduleResolution":"bundler","allowImportingTsExtensions":true,"isolatedModules":true,"moduleDetection":"force","noEmit":true,"jsx":"react-jsx","strict":true,"noUnusedLocals":true,"noUnusedParameters":true,"noFallthroughCasesInSwitch":true},"include":["src"]}',
            "vite.config.ts": 'import { defineConfig } from "vite";\nimport react from "@vitejs/plugin-react";\n\nexport default defineConfig({\n  plugins: [react()],\n});\n',
            ".gitignore": "node_modules\ndist\n",
        }

    def generate_next(self, project_data: dict[str, Any]) -> dict[str, str]:
        name = project_data.get("name", "my-app")
        return {
            "src/app/layout.tsx": """export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
""",
            "src/app/page.tsx": f"""export default function Home() {{
  return <div>Hello from {name}</div>;
}}
""",
            "src/app/globals.css": "/* Global styles */\n",
            "package.json": f'{{"name":"{name}","version":"0.1.0","private":true,"scripts":{{"dev":"next dev","build":"next build","start":"next start"}},"dependencies":{{"next":"^14.0.0","react":"^18.2.0","react-dom":"^18.2.0"}},"devDependencies":{{"@types/node":"^20.0.0","@types/react":"^18.2.0","@types/react-dom":"^18.2.0","typescript":"^5.0.0"}}}}',
            "tsconfig.json": '{"compilerOptions":{"target":"ES2017","lib":["dom","dom.iterable","esnext"],"allowJs":true,"skipLibCheck":true,"strict":true,"noEmit":true,"esModuleInterop":true,"module":"esnext","moduleResolution":"bundler","resolveJsonModule":true,"isolatedModules":true,"jsx":"preserve","incremental":true,"plugins":[{"name":"next"}],"paths":{"@/*":["./src/*"]}},"include":["next-env.d.ts","**/*.ts","**/*.tsx",".next/types/**/*.ts"],"exclude":["node_modules"]}',
            "next.config.js": "/** @type {import('next').NextConfig} */\nconst nextConfig = {};\nmodule.exports = nextConfig;\n",
            ".gitignore": "node_modules\n.next\n",
        }
