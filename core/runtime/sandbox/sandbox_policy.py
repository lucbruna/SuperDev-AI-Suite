from pydantic import BaseModel, Field


class SandboxPolicy(BaseModel):
    allowed_commands: list[str] = Field(default_factory=lambda: ["python3", "python", "node", "bash", "sh", "zsh"])
    blocked_commands: list[str] = Field(default_factory=lambda: ["rm -rf /", "sudo", "chmod 777", "dd"])
    max_processes: int = 10
    network_access: bool = False
    filesystem_access: bool = True
    allow_subprocesses: bool = True
    allow_file_write: bool = True
    allow_file_read: bool = True

    def is_command_allowed(self, command: str) -> bool:
        cmd_name = command.split()[0] if command else ""
        if cmd_name in self.blocked_commands:
            return False
        if self.allowed_commands and cmd_name not in self.allowed_commands:
            return False
        return True
