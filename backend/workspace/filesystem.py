from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class FileNode:
    name: str
    path: str
    type: str  # "file" or "dir"
    children: list["FileNode"] = field(default_factory=list)
    size: int = 0
    modified: str | None = None

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "size": self.size,
            "modified": self.modified,
        }
        if self.type == "dir" and self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


class WorkspaceFilesystem:
    def __init__(self) -> None:
        self._files: dict[str, str] = {}

    async def create_file(self, path: str, content: str) -> None:
        self._files[path] = content

    async def read_file(self, path: str) -> str | None:
        return self._files.get(path)

    async def write_file(self, path: str, content: str) -> None:
        self._files[path] = content

    async def delete_file(self, path: str) -> bool:
        return self._files.pop(path, None) is not None

    async def list_files(self, prefix: str = "") -> list[str]:
        if not prefix:
            return list(self._files.keys())
        return [p for p in self._files if p.startswith(prefix)]

    async def get_file_tree(self, path: str = "") -> dict:
        prefix = path.rstrip("/") + "/" if path else ""
        relevant = [p for p in self._files if p.startswith(prefix)] if prefix else list(self._files.keys())

        root = FileNode(
            name=path.split("/")[-1] if path else "",
            path=path or "/",
            type="dir",
        )

        for file_path in relevant:
            relative = file_path[len(prefix):] if prefix else file_path
            parts = relative.split("/")
            current = root
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    child_path = path + "/" + part if path else part
                    node = FileNode(
                        name=part,
                        path=child_path,
                        type="file",
                        size=len(self._files[file_path]),
                        modified=datetime.now(UTC).isoformat(),
                    )
                    self._merge_node(current, node)
                else:
                    child_path = path + "/" + part if path else part
                    dir_node = FileNode(
                        name=part,
                        path=child_path,
                        type="dir",
                    )
                    if not self._merge_node(current, dir_node):
                        existing = self._find_child(current, part)
                        if existing is None:
                            current.children.append(dir_node)
                            current = dir_node
                        else:
                            current = existing

        return root.to_dict()

    def _find_child(self, node: FileNode, name: str) -> FileNode | None:
        for c in node.children:
            if c.name == name:
                return c
        return None

    def _merge_node(self, parent: FileNode, node: FileNode) -> bool:
        existing = self._find_child(parent, node.name)
        if existing:
            if node.type == "file":
                existing.size = node.size
                existing.modified = node.modified
            return True
        if node.type == "file":
            parent.children.append(node)
            return True
        return False

    def get_all_files(self) -> dict[str, str]:
        return dict(self._files)

    def set_all_files(self, files: dict[str, str]) -> None:
        self._files = dict(files)
