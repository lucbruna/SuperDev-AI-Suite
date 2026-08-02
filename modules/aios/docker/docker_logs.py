"""Docker logs — fetch container output with optional streaming."""
from __future__ import annotations

import asyncio

from modules.aios.docker.docker_client import (
    DockerClient,
    require_docker_action,
)


class DockerLogs:
    """Container log retrieval over the docker CLI."""

    def __init__(self, client: DockerClient) -> None:
        self._client = client

    async def logs(
        self,
        container: str,
        *,
        tail: int | None = 100,
        timestamps: bool = False,
        stream: bool = False,
    ) -> str:
        require_docker_action("logs")
        args = ["logs"]
        if tail is not None:
            args += ["--tail", str(tail)]
        if timestamps:
            args.append("-t")
        if stream:
            args.append("-f")
        args.append(container)

        if not stream:
            code, out, err = await self._client._run(args, timeout_s=60.0)
            if code != 0:
                raise RuntimeError(f"docker logs failed: {err.strip() or out.strip()}")
            return out

        # Streaming: read lines until the process exits or the deadline hits.
        try:
            proc = await asyncio.create_subprocess_exec(
                self._client.binary,
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return ""
        chunks: list[str] = []
        assert proc.stdout is not None
        try:
            while True:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=30.0)
                if not line:
                    break
                chunks.append(line.decode("utf-8", errors="replace"))
        except (TimeoutError, asyncio.CancelledError):
            proc.kill()
        await proc.wait()
        return "".join(chunks)


__all__ = ["DockerLogs"]
