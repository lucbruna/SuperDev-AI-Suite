"""
Context Manager - Maintains interaction context and session management.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .multimodal_models import (
    InputType, OutputType, InteractionStatus,
    MultimodalInput, MultimodalOutput, InteractionSession,
)

logger = logging.getLogger(__name__)


class ContextManager:
    def __init__(self):
        self._sessions: Dict[str, InteractionSession] = {}
        self._context_links: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        self._default_session_ttl_minutes: int = 120

    async def create_session(
        self,
        user_id: Optional[str] = None,
        ttl_minutes: Optional[int] = None,
    ) -> InteractionSession:
        session_id = str(uuid.uuid4())
        ttl = ttl_minutes or self._default_session_ttl_minutes
        expires_at = datetime.utcnow() + timedelta(minutes=ttl)
        session = InteractionSession(
            id=session_id,
            user_id=user_id,
            status=InteractionStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        async with self._lock:
            self._sessions[session_id] = session
        logger.debug(f"Created session {session_id} for user {user_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[InteractionSession]:
        async with self._lock:
            session = self._sessions.get(session_id)
        if session and session.is_expired():
            await self.close_session(session_id)
            return None
        return session

    async def update_session(
        self,
        session_id: str,
        status: Optional[InteractionStatus] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[InteractionSession]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            if status is not None:
                session.status = status
            if context:
                session.context.update(context)
            if metadata:
                session.metadata.update(metadata)
            session.updated_at = datetime.utcnow()
        return session

    async def close_session(self, session_id: str) -> None:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.status = InteractionStatus.COMPLETED
                session.updated_at = datetime.utcnow()
        async with self._lock:
            self._context_links.pop(session_id, None)
            for links in self._context_links.values():
                if session_id in links:
                    links.remove(session_id)
        logger.debug(f"Closed session {session_id}")

    async def link_context(self, source_session_id: str, target_session_id: str) -> bool:
        async with self._lock:
            if source_session_id not in self._sessions or target_session_id not in self._sessions:
                return False
            if source_session_id not in self._context_links:
                self._context_links[source_session_id] = []
            self._context_links[source_session_id].append(target_session_id)
            source = self._sessions[source_session_id]
            if target_session_id not in source.linked_session_ids:
                source.linked_session_ids.append(target_session_id)
        logger.debug(f"Linked session {source_session_id} -> {target_session_id}")
        return True

    async def get_linked_sessions(self, session_id: str) -> List[InteractionSession]:
        async with self._lock:
            linked_ids = self._context_links.get(session_id, [])
            sessions = []
            for lid in linked_ids:
                s = self._sessions.get(lid)
                if s and not s.is_expired():
                    sessions.append(s)
        return sessions

    async def get_conversation_history(
        self, session_id: str, limit: int = 50
    ) -> List[Dict[str, str]]:
        session = await self.get_session(session_id)
        if not session:
            return []
        history = []
        for inp, out in zip(session.inputs[-limit:], session.outputs[-limit:]):
            history.append({
                "role": "user",
                "content": str(inp.data),
                "modality": inp.type.value,
                "timestamp": inp.timestamp.isoformat(),
            })
            history.append({
                "role": "assistant",
                "content": str(out.content),
                "modality": out.type.value,
                "timestamp": out.timestamp.isoformat(),
            })
        return history

    async def add_input_to_session(
        self, session_id: str, inp: MultimodalInput
    ) -> Optional[InteractionSession]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            session.add_input(inp)
            if session.status == InteractionStatus.PENDING:
                session.status = InteractionStatus.PROCESSING
        return session

    async def add_output_to_session(
        self, session_id: str, out: MultimodalOutput
    ) -> Optional[InteractionSession]:
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            session.add_output(out)
            session.status = InteractionStatus.COMPLETED
        return session

    async def get_session_count(self) -> int:
        async with self._lock:
            return len(self._sessions)

    async def get_active_sessions(self) -> List[InteractionSession]:
        async with self._lock:
            now = datetime.utcnow()
            return [
                s for s in self._sessions.values()
                if s.status in (InteractionStatus.PENDING, InteractionStatus.PROCESSING)
                and (s.expires_at is None or s.expires_at > now)
            ]

    async def cleanup_expired(self) -> int:
        async with self._lock:
            now = datetime.utcnow()
            expired_ids = [
                sid for sid, s in self._sessions.items()
                if s.is_expired() or s.status == InteractionStatus.COMPLETED
            ]
            for sid in expired_ids:
                del self._sessions[sid]
                self._context_links.pop(sid, None)
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired sessions")
        return len(expired_ids)

    async def search_sessions(
        self,
        user_id: Optional[str] = None,
        status: Optional[InteractionStatus] = None,
        modality: Optional[InputType] = None,
        limit: int = 50,
    ) -> List[InteractionSession]:
        async with self._lock:
            results = list(self._sessions.values())
        if user_id:
            results = [s for s in results if s.user_id == user_id]
        if status:
            results = [s for s in results if s.status == status]
        if modality:
            results = [s for s in results if s.modality_counts.get(modality.value, 0) > 0]
        return results[:limit]
