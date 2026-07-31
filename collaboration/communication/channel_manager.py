"""Channel lifecycle management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import ChannelKind, ChannelRecord
from collaboration.collaboration_protocols import new_id


class ChannelManager:
    """CRUD for channels (public, private, direct)."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry

    def create(self, workspace_id: str, name: str,
               topic: str = "",
               kind: ChannelKind = ChannelKind.CHANNEL) -> ChannelRecord:
        channel = ChannelRecord(channel_id=new_id("chan"),
                                workspace_id=workspace_id, name=name,
                                topic=topic, kind=kind)
        if self.registry is not None:
            self.registry.register_channel(channel.channel_id, channel)
        return channel

    def get(self, channel_id: str) -> ChannelRecord | None:
        if self.registry is None:
            return None
        return self.registry.get_channel(channel_id)

    def list(self) -> list[str]:
        if self.registry is None:
            return []
        return self.registry.list_channels()

    def remove(self, channel_id: str) -> bool:
        if self.registry is not None:
            return self.registry.remove_channel(channel_id)
        return False

    def join(self, channel_id: str, member_id: str) -> ChannelRecord | None:
        channel = self.get(channel_id)
        if channel is None:
            return None
        if member_id not in channel.members:
            channel.members.append(member_id)
        return channel

    def leave(self, channel_id: str, member_id: str) -> ChannelRecord | None:
        channel = self.get(channel_id)
        if channel is None:
            return None
        if member_id in channel.members:
            channel.members.remove(member_id)
        return channel

    def by_workspace(self, workspace_id: str) -> list[ChannelRecord]:
        if self.registry is None:
            return []
        channels = []
        for channel_id in self.registry.list_channels():
            channel = self.registry.get_channel(channel_id)
            if channel is not None and channel.workspace_id == workspace_id:
                channels.append(channel)
        return channels

    def count(self) -> int:
        if self.registry is None:
            return 0
        return len(self.registry.list_channels())
