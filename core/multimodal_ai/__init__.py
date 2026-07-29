"""
SuperDev Multimodal AI Engine

Enterprise multimodal intelligence system providing:
- Text processing & understanding
- Voice recognition & synthesis
- Computer vision & image analysis
- Video analysis & scene detection
- Document parsing & summarization
- Sensor data processing
- Conversation management
- Cross-modal translation
"""

from ._engine_types import EngineConfig, EngineState, EngineMetrics
from .multimodal_engine import MultimodalEngine
from .interaction_manager import InteractionManager, ManagerConfig
from .multimodal_config import MultimodalConfig, TextConfig, VoiceConfig, VisionConfig, VideoConfig, DocumentConfig, SensorConfig, ConversationConfig, TranslationConfig
from .multimodal_models import (
    InputType, OutputType, ModalityType, InteractionStatus,
    MultimodalInput, MultimodalOutput, ProcessedInput,
    UnderstandingResult, ResponsePlan, InteractionSession,
)
from .multimodal_security import MultimodalSecurityManager, PrivacyManager, AccessControl, DataMasker, ConsentManager
from .input_processor import InputProcessor
from .output_generator import OutputGenerator
from .context_manager import ContextManager

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "MultimodalEngine", "EngineConfig", "EngineState", "EngineMetrics",
    "InteractionManager", "ManagerConfig",
    "MultimodalConfig", "TextConfig", "VoiceConfig", "VisionConfig",
    "VideoConfig", "DocumentConfig", "SensorConfig",
    "ConversationConfig", "TranslationConfig",
    "InputType", "OutputType", "ModalityType", "InteractionStatus",
    "MultimodalInput", "MultimodalOutput", "ProcessedInput",
    "UnderstandingResult", "ResponsePlan", "InteractionSession",
    "MultimodalSecurityManager", "PrivacyManager", "AccessControl",
    "DataMasker", "ConsentManager",
    "InputProcessor",
    "OutputGenerator",
    "ContextManager",
]
