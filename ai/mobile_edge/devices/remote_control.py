"""Remote Control - Remote device management operations."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RemoteCommand(Enum):
    REBOOT = "reboot"
    LOCK = "lock"
    UNLOCK = "unlock"
    WIPE = "wipe"
    UPDATE = "update"
    CONFIGURE = "configure"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    SCAN = "scan"
    BACKUP = "backup"


class CommandStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class RemoteCommandResult:
    command_id: str
    device_id: str
    command: RemoteCommand
    status: CommandStatus = CommandStatus.PENDING
    result_data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    sent_at: datetime | None = None
    completed_at: datetime | None = None


class RemoteControlManager:
    def __init__(self):
        self.commands: list[RemoteCommandResult] = []
        self.authorized_commands: dict[str, list[RemoteCommand]] = {}

    def authorize_device(self, device_id: str, commands: list[RemoteCommand]) -> None:
        self.authorized_commands[device_id] = commands

    def send_command(self, device_id: str, command: RemoteCommand, params: dict[str, Any] = None) -> RemoteCommandResult:
        command_id = hashlib.sha256(f"{device_id}{command.value}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        result = RemoteCommandResult(command_id=command_id, device_id=device_id, command=command, sent_at=datetime.now())
        self.commands.append(result)
        return result

    def update_status(self, command_id: str, status: CommandStatus, data: dict[str, Any] = None, error: str = "") -> bool:
        for cmd in self.commands:
            if cmd.command_id == command_id:
                cmd.status = status
                if data:
                    cmd.result_data = data
                if error:
                    cmd.error = error
                if status in (CommandStatus.COMPLETED, CommandStatus.FAILED, CommandStatus.TIMEOUT):
                    cmd.completed_at = datetime.now()
                return True
        return False

    def get_command(self, command_id: str) -> RemoteCommandResult | None:
        for cmd in self.commands:
            if cmd.command_id == command_id:
                return cmd
        return None

    def get_device_commands(self, device_id: str) -> list[RemoteCommandResult]:
        return [c for c in self.commands if c.device_id == device_id]

    def count(self) -> int:
        return len(self.commands)
