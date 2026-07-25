from pydantic import BaseModel, Field


class SandboxPermissions(BaseModel):
    filesystem_read: bool = True
    filesystem_write: bool = True
    network_access: bool = False
    docker_access: bool = False
    environment_access: bool = False
    allowed_paths: list[str] = Field(default_factory=list)
    blocked_paths: list[str] = Field(default_factory=list)

    def can_read(self, path: str) -> bool:
        if not self.filesystem_read:
            return False
        for blocked in self.blocked_paths:
            if path.startswith(blocked):
                return False
        return True

    def can_write(self, path: str) -> bool:
        if not self.filesystem_write:
            return False
        for blocked in self.blocked_paths:
            if path.startswith(blocked):
                return False
        return True
