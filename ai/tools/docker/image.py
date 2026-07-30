from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DockerImage(BaseTool):
    """Manage Docker images."""

    _name = "docker_image"
    _description = "Manage Docker images: list, pull, build, remove, tag, push"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._images: list[dict[str, Any]] = []
        self._operation_log: list[str] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        try:
            if action == "list":
                return {"success": True, "images": self._images, "count": len(self._images)}
            elif action == "pull":
                name = params.get("name", "")
                tag = params.get("tag", "latest")
                image = {"name": name, "tag": tag, "id": f"sha256:{name.replace('/', '_')}_{tag}"}
                self._images.append(image)
                self._operation_log.append(f"pulled {name}:{tag}")
                return {"success": True, "image": image}
            elif action == "build":
                path = params.get("path", ".")
                tag = params.get("tag", "latest")
                image = {"name": tag, "tag": "latest", "id": f"sha256:built_{path.replace('/', '_')}"}
                self._images.append(image)
                self._operation_log.append(f"built {tag} from {path}")
                return {"success": True, "image": image}
            elif action == "remove":
                image_id = params.get("image_id", "")
                self._images = [i for i in self._images if i.get("id") != image_id]
                self._operation_log.append(f"removed {image_id}")
                return {"success": True, "message": f"Removed image {image_id}"}
            elif action == "tag":
                source = params.get("source", "")
                target = params.get("target", "")
                self._operation_log.append(f"tagged {source} as {target}")
                return {"success": True, "message": f"Tagged {source} as {target}"}
            elif action == "push":
                name = params.get("name", "")
                self._operation_log.append(f"pushed {name}")
                return {"success": True, "message": f"Pushed {name}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._operation_log.clear()

    async def cleanup(self) -> None:
        self._images.clear()
        self._operation_log.clear()
