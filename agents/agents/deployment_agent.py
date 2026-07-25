from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class DeploymentAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            action = context.get("action", "generate")
            project_path = context.get("path", task)
            project_name = context.get("project_name", "myapp")
            base_image = context.get("base_image", "python:3.11-slim")

            artifacts = {}

            if action in ("generate", "all"):
                dockerfile = self._generate_dockerfile(project_name, base_image, context)
                dockerfile_path = os.path.join(project_path, "Dockerfile")
                os.makedirs(project_path, exist_ok=True)
                with open(dockerfile_path, "w") as f:
                    f.write(dockerfile)
                artifacts["dockerfile"] = dockerfile_path

                compose = self._generate_docker_compose(project_name, base_image, context)
                compose_path = os.path.join(project_path, "docker-compose.yml")
                with open(compose_path, "w") as f:
                    f.write(compose)
                artifacts["docker_compose"] = compose_path

            if action in ("build", "all"):
                build_result = await self._build_image(project_path, project_name)
                artifacts["build"] = build_result

            output = self._generate_report(artifacts)

            return AgentResult(
                success=True,
                output=output,
                metrics={
                    "action": action,
                    "artifacts_created": len(artifacts),
                },
                artifacts=artifacts,
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def _generate_dockerfile(self, project_name: str, base_image: str, context: dict) -> str:
        return f"""FROM {base_image}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {context.get("port", 8000)}

CMD ["python", "{context.get("entrypoint", "main.py")}"]
"""

    def _generate_docker_compose(self, project_name: str, base_image: str, context: dict) -> str:
        services = context.get("services", ["app"])
        compose = "version: '3.8'\n\nservices:\n"
        for svc in services:
            compose += f"""  {svc}:
    build: .
    container_name: {svc}
    ports:
      - "{context.get('port', 8000)}:{context.get('port', 8000)}"
    volumes:
      - .:/app
    restart: unless-stopped\n\n"""
        return compose

    async def _build_image(self, project_path: str, project_name: str) -> dict[str, Any]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "docker", "build", "-t", project_name, project_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            return {
                "success": proc.returncode == 0,
                "output": stdout.decode() if stdout else "",
                "error": stderr.decode() if stderr else "",
            }
        except FileNotFoundError:
            return {"success": False, "error": "Docker not found in PATH"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_report(self, artifacts: dict) -> str:
        lines = ["## Deployment Report", ""]
        for key, value in artifacts.items():
            lines.append(f"**{key}:** {value}")
        return "\n".join(lines)

    def capabilities(self) -> list[str]:
        return ["dockerfile_generation", "docker_compose", "container_build", "deployment_config"]
