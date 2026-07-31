"""AI Module API Router — REST endpoints for all AI subsystem stats."""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

# Ensure the ai/ directory is on sys.path for module imports
_AI_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "ai")
_AI_ROOT = os.path.normpath(_AI_ROOT)
if _AI_ROOT not in sys.path:
    sys.path.insert(0, _AI_ROOT)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Modules"])


def _safe_import(module_path: str, class_name: str) -> Any:
    """Safely import a class from a module."""
    try:
        import importlib
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)
    except (ImportError, AttributeError) as e:
        logger.warning("AI module not available: %s.%s — %s", module_path, class_name, e)
        return None


# ── Health ─────────────────────────────────────────────────────────────
@router.get("/health")
async def ai_health() -> dict[str, Any]:
    """Check health of all AI subsystems."""
    modules = {
        "cybersecurity_engine": ("cybersecurity_engine", "CybersecurityEngine"),
        "data_platform": ("data_platform", "DataPlatformEngine"),
        "erp_operations": ("erp_operations", "ERPEngine"),
        "knowledge_engine": ("ai_knowledge_engine", "KnowledgeEngine"),
    }
    health = {}
    for name, (mod_path, cls_name) in modules.items():
        cls = _safe_import(mod_path, cls_name)
        health[name] = "available" if cls else "unavailable"
    return {"status": "ok", "modules": health}


# ── Module Listing ─────────────────────────────────────────────────────
@router.get("/modules")
async def list_modules() -> dict[str, Any]:
    """List all AI modules and their status."""
    modules_info = [
        {"name": "cybersecurity_engine", "description": "Autonomous Cybersecurity & Digital Defense Engine", "volumes": ["threat_detection", "vulnerability", "identity", "encryption", "monitoring", "incident_response", "compliance", "penetration", "audit"]},
        {"name": "data_platform", "description": "Enterprise Data Platform & Analytics Engine", "volumes": ["ingestion", "storage", "processing", "streaming", "etl", "quality", "governance", "analytics", "machine_learning", "knowledge_graph"]},
        {"name": "erp_operations", "description": "Enterprise Resource Planning & Operations Engine", "volumes": ["inventory", "sales", "purchases", "suppliers", "production", "logistics", "warehouse", "hr", "workflow", "automation"]},
        {"name": "ai_knowledge_engine", "description": "Autonomous AI Research & Knowledge Engine", "volumes": ["research", "documents", "vector_memory", "embeddings", "reasoning", "learning", "validation", "knowledge_graph"]},
    ]
    return {"modules": modules_info, "total": len(modules_info)}


# ── Aggregate Stats ───────────────────────────────────────────────────
@router.get("/stats")
async def ai_stats() -> dict[str, Any]:
    """Returns stats from all AI modules."""
    all_stats = {}

    # Cybersecurity
    cls = _safe_import("cybersecurity_engine", "CybersecurityEngine")
    if cls:
        try:
            engine = cls()
            all_stats["cybersecurity"] = engine.get_stats()
        except Exception as e:
            all_stats["cybersecurity"] = {"error": str(e)}
    else:
        all_stats["cybersecurity"] = {"status": "unavailable"}

    # Data Platform
    cls = _safe_import("data_platform", "DataPlatformEngine")
    if cls:
        try:
            engine = cls()
            all_stats["data_platform"] = engine.get_stats()
        except Exception as e:
            all_stats["data_platform"] = {"error": str(e)}
    else:
        all_stats["data_platform"] = {"status": "unavailable"}

    # ERP
    cls = _safe_import("erp_operations", "ERPEngine")
    if cls:
        try:
            engine = cls()
            all_stats["erp"] = engine.get_stats()
        except Exception as e:
            all_stats["erp"] = {"error": str(e)}
    else:
        all_stats["erp"] = {"status": "unavailable"}

    # Knowledge Engine
    cls = _safe_import("ai_knowledge_engine", "KnowledgeEngine")
    if cls:
        try:
            engine = cls()
            all_stats["knowledge"] = engine.get_stats()
        except Exception as e:
            all_stats["knowledge"] = {"error": str(e)}
    else:
        all_stats["knowledge"] = {"status": "unavailable"}

    return {"stats": all_stats, "total_modules": len(all_stats)}


# ── Cybersecurity Endpoints ────────────────────────────────────────────
@router.get("/cybersecurity/stats")
async def cybersecurity_stats() -> dict[str, Any]:
    cls = _safe_import("cybersecurity_engine", "CybersecurityEngine")
    if not cls:
        raise HTTPException(status_code=503, detail="Cybersecurity engine not available")
    engine = cls()
    return {"stats": engine.get_stats()}


@router.get("/cybersecurity/threats")
async def cybersecurity_threats() -> dict[str, Any]:
    cls = _safe_import("cybersecurity_engine", "CybersecurityEngine")
    if not cls:
        raise HTTPException(status_code=503, detail="Cybersecurity engine not available")
    engine = cls()
    threats = engine.get_threats()
    return {"threats": [{"id": t.threat_id, "type": t.threat_type.value, "severity": t.severity.value, "source_ip": t.source_ip, "target": t.target} for t in threats]}


# ── Data Platform Endpoints ────────────────────────────────────────────
@router.get("/data-platform/stats")
async def data_platform_stats() -> dict[str, Any]:
    cls = _safe_import("data_platform", "DataPlatformEngine")
    if not cls:
        raise HTTPException(status_code=503, detail="Data platform not available")
    engine = cls()
    return {"stats": engine.get_stats()}


# ── ERP Endpoints ──────────────────────────────────────────────────────
@router.get("/erp/stats")
async def erp_stats() -> dict[str, Any]:
    cls = _safe_import("erp_operations", "ERPEngine")
    if not cls:
        raise HTTPException(status_code=503, detail="ERP engine not available")
    engine = cls()
    return {"stats": engine.get_stats()}


# ── Knowledge Engine Endpoints ─────────────────────────────────────────
@router.get("/knowledge/stats")
async def knowledge_stats() -> dict[str, Any]:
    cls = _safe_import("ai_knowledge_engine", "KnowledgeEngine")
    if not cls:
        raise HTTPException(status_code=503, detail="Knowledge engine not available")
    engine = cls()
    return {"stats": engine.get_stats()}
