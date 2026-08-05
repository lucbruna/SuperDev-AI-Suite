"""AI Editor — professional NLE-style editor (Volume 5).

Core orchestration, project persistence, autosave/recovery, undo/redo,
clipboard, scheduling, learning, statistics, memory, logging, history and the
multi-track timeline with ripple/slip/slide/trim/snap/magnetic edits,
transitions, effects, markers, subtitles, nested sequences and proxies.
"""
from modules.ai_video_studio.ai_editor.editor_engine import EditorEngine, get_editor_engine
from modules.ai_video_studio.ai_editor.editor_manager import EditorManager
from modules.ai_video_studio.ai_editor.project_manager import ProjectManager, get_project_manager
from modules.ai_video_studio.ai_editor.autosave import AutosaveManager
from modules.ai_video_studio.ai_editor.recovery_engine import RecoveryEngine
from modules.ai_video_studio.ai_editor.undo_redo import UndoRedoManager
from modules.ai_video_studio.ai_editor.clipboard_manager import ClipboardManager
from modules.ai_video_studio.ai_editor.editor_scheduler import EditorScheduler
from modules.ai_video_studio.ai_editor.editor_learning import EditorLearning
from modules.ai_video_studio.ai_editor.editor_statistics import EditorStatistics
from modules.ai_video_studio.ai_editor.editor_optimizer import EditorOptimizer
from modules.ai_video_studio.ai_editor.editor_memory import EditorMemory
from modules.ai_video_studio.ai_editor.editor_logger import get_editor_logger, recent_logs
from modules.ai_video_studio.ai_editor.editor_history import EditorHistory

__all__ = [
    "EditorEngine",
    "get_editor_engine",
    "EditorManager",
    "ProjectManager",
    "get_project_manager",
    "AutosaveManager",
    "RecoveryEngine",
    "UndoRedoManager",
    "ClipboardManager",
    "EditorScheduler",
    "EditorLearning",
    "EditorStatistics",
    "EditorOptimizer",
    "EditorMemory",
    "get_editor_logger",
    "recent_logs",
    "EditorHistory",
]
