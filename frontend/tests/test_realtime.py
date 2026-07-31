from __future__ import annotations

from frontend.realtime.realtime_engine import RealtimeEngine
from frontend.realtime.collaboration import Collaboration


def test_realtime_pub_sub() -> None:
    realtime = RealtimeEngine()
    received: list[dict] = []

    def handler(_channel: str, data: dict) -> None:
        received.append(data)

    realtime.subscribe("events", handler)
    realtime.publish("events", {"type": "ping"})
    assert received and received[-1].get("type") == "ping"


def test_collaboration_sessions() -> None:
    collab = Collaboration()
    session = collab.create_session("doc-1")
    assert session.session_id == "doc-1"
    assert "doc-1" in collab.list_sessions()
    assert collab.get_session("doc-1") is session
