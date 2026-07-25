"""Gerenciador de jobs em background para tarefas assíncronas."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)


class JobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class Job:
    """Representa uma tarefa em background."""

    def __init__(
        self,
        job_type: str,
        payload: dict[str, Any],
        priority: int = 0,
        max_retries: int = 3,
        timeout: int = 300,
    ) -> None:
        self.id = str(uuid4())
        self.type = job_type
        self.payload = payload
        self.priority = priority
        self.max_retries = max_retries
        self.timeout = timeout

        self.status = JobStatus.PENDING
        self.result: Any = None
        self.error: str | None = None
        self.progress: float = 0.0
        self.retries = 0

        self.created_at = datetime.now(UTC)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status.value,
            "payload": self.payload,
            "result": self.result,
            "error": self.error,
            "progress": self.progress,
            "retries": self.retries,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class JobManager:
    """Gerenciador de jobs em background."""

    def __init__(self, max_workers: int = 4) -> None:
        self._jobs: dict[str, Job] = {}
        self._handlers: dict[str, Callable] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._workers: list[asyncio.Task] = []
        self._max_workers = max_workers
        self._running = False

    def register_handler(self, job_type: str, handler: Callable) -> None:
        """Registra um handler para um tipo de job."""
        self._handlers[job_type] = handler
        logger.info(f"Handler registrado para: {job_type}")

    async def submit(
        self,
        job_type: str,
        payload: dict[str, Any],
        priority: int = 0,
        max_retries: int = 3,
        timeout: int = 300,
    ) -> Job:
        """Submete um novo job para processamento."""
        if job_type not in self._handlers:
            raise ValueError(f"Nenhum handler registrado para: {job_type}")

        job = Job(
            job_type=job_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
        )

        self._jobs[job.id] = job
        await self._queue.put(job.id)

        logger.info(f"Job submetido: {job.id} ({job_type})")
        return job

    async def start(self) -> None:
        """Inicia os workers de processamento."""
        if self._running:
            return

        self._running = True
        for i in range(self._max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self._workers.append(worker)

        logger.info(f"JobManager iniciado com {self._max_workers} workers")

    async def stop(self) -> None:
        """Para os workers."""
        self._running = False

        # Cancelar workers
        for worker in self._workers:
            worker.cancel()

        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("JobManager parado")

    async def _worker(self, worker_id: str) -> None:
        """Worker que processa jobs da fila."""
        logger.info(f"Worker {worker_id} iniciado")

        while self._running:
            try:
                job_id = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_job(job_id)
            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no worker {worker_id}: {e}")

        logger.info(f"Worker {worker_id} finalizado")

    async def _process_job(self, job_id: str) -> None:
        """Processa um job individual."""
        job = self._jobs.get(job_id)
        if not job or job.status != JobStatus.PENDING:
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

        handler = self._handlers.get(job.type)
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"Nenhum handler para: {job.type}"
            return

        try:
            # Executar com timeout
            result = await asyncio.wait_for(
                handler(job),
                timeout=job.timeout,
            )
            job.result = result
            job.status = JobStatus.COMPLETED
            job.progress = 100.0

        except TimeoutError:
            job.status = JobStatus.FAILED
            job.error = f"Timeout após {job.timeout}s"

        except Exception as e:
            job.error = str(e)
            job.retries += 1

            if job.retries < job.max_retries:
                job.status = JobStatus.RETRYING
                await asyncio.sleep(2 ** job.retries)  # Backoff exponencial
                await self._queue.put(job_id)
                logger.warning(f"Job {job_id} retry {job.retries}/{job.max_retries}")
            else:
                job.status = JobStatus.FAILED
                logger.error(f"Job {job_id} falhou: {e}")

        finally:
            job.completed_at = datetime.now(UTC)

    def get_job(self, job_id: str) -> Job | None:
        """Obtém um job pelo ID."""
        return self._jobs.get(job_id)

    def get_jobs_by_type(self, job_type: str) -> list[Job]:
        """Obtém jobs por tipo."""
        return [j for j in self._jobs.values() if j.type == job_type]

    def get_jobs_by_status(self, status: JobStatus) -> list[Job]:
        """Obtém jobs por status."""
        return [j for j in self._jobs.values() if j.status == status]

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas dos jobs."""
        stats = {
            "total": len(self._jobs),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0,
        }

        for job in self._jobs.values():
            stats[job.status.value] = stats.get(job.status.value, 0) + 1

        return stats


# ── Handlers pré-definidos ────────────────────────────────────────

async def handle_code_review(job: Job) -> dict[str, Any]:
    """Handler para revisão de código."""
    job.payload.get("code", "")
    language = job.payload.get("language", "python")

    # Simular revisão
    job.progress = 50.0
    await asyncio.sleep(1)

    return {
        "score": 85,
        "issues": [],
        "suggestions": ["Adicionar type hints", "Usar docstrings"],
        "language": language,
    }


async def handle_notification(job: Job) -> dict[str, Any]:
    """Handler para envio de notificações."""
    notification_type = job.payload.get("type", "info")
    job.payload.get("message", "")

    job.progress = 50.0
    await asyncio.sleep(0.5)

    return {"sent": True, "type": notification_type}


async def handle_data_export(job: Job) -> dict[str, Any]:
    """Handler para exportação de dados."""
    format_type = job.payload.get("format", "csv")
    data = job.payload.get("data", [])

    job.progress = 50.0
    await asyncio.sleep(2)

    return {"format": format_type, "rows": len(data)}


# Instância global
job_manager = JobManager(max_workers=4)

# Registrar handlers padrão
job_manager.register_handler("code_review", handle_code_review)
job_manager.register_handler("notification", handle_notification)
job_manager.register_handler("data_export", handle_data_export)
