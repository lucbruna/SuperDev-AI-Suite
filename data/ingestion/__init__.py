"""Data Ingestion subsystem package."""

from __future__ import annotations

from .agent_ingestion import AgentCollector
from .api_ingestion import APICollector, APIConnector
from .collector import BaseCollector, CollectorManager
from .connector import BaseConnector, ConnectorManager
from .database_ingestion import DatabaseCollector, DatabaseConnector
from .event_ingestion import EventCollector
from .file_ingestion import FileCollector, FileConnector
from .ingestion_engine import IngestionEngine
from .log_ingestion import LogCollector
from .project_ingestion import ProjectCollector

__all__ = [
    "IngestionEngine",
    "BaseConnector", "ConnectorManager",
    "BaseCollector", "CollectorManager",
    "APIConnector", "APICollector",
    "DatabaseConnector", "DatabaseCollector",
    "FileConnector", "FileCollector",
    "EventCollector",
    "LogCollector",
    "AgentCollector",
    "ProjectCollector",
]
