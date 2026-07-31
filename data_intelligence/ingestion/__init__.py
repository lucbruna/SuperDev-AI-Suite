"""Ingestion subsystem (Volume 22).

Collects raw data from SQL, NoSQL, APIs, files, streams, ERP and CRM
sources and normalizes it into ``DataRecord`` objects.
"""

from __future__ import annotations

from data_intelligence.ingestion.api_source import ApiSource
from data_intelligence.ingestion.base import BaseSource
from data_intelligence.ingestion.collector import IngestionCollector
from data_intelligence.ingestion.erp_crm_source import CrmSource, ErpSource
from data_intelligence.ingestion.file_source import FileSource
from data_intelligence.ingestion.nosql_source import MongoSource
from data_intelligence.ingestion.sql_source import SqlSource
from data_intelligence.ingestion.stream_source import StreamSource

__all__ = [
    "IngestionCollector", "BaseSource", "SqlSource", "MongoSource",
    "ApiSource", "FileSource", "StreamSource", "ErpSource", "CrmSource",
]
