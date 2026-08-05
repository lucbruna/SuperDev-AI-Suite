"""AI Video Generator — core video generation engine (blueprint Volume 3).

Orchestrates text-to-video, image-to-video and video-to-video pipelines:
model routing, GPU/CPU allocation, rendering, task dispatch, quality
control, checkpoints, scheduling, optimisation, statistics, memory, cache
and logging.
"""
from modules.ai_video_studio.ai_video_generator.video_engine import VideoEngine, get_video_engine
from modules.ai_video_studio.ai_video_generator.generation_manager import GenerationManager, get_generation_manager
from modules.ai_video_studio.ai_video_generator.generation_scheduler import GenerationScheduler, get_generation_scheduler
from modules.ai_video_studio.ai_video_generator.generation_optimizer import GenerationOptimizer, get_generation_optimizer
from modules.ai_video_studio.ai_video_generator.generation_statistics import GenerationStatistics, get_generation_statistics
from modules.ai_video_studio.ai_video_generator.generation_memory import GenerationMemory, get_generation_memory
from modules.ai_video_studio.ai_video_generator.generation_cache import GenerationCache, get_generation_cache
from modules.ai_video_studio.ai_video_generator.generation_logger import GenerationLogger, get_generation_logger
from modules.ai_video_studio.ai_video_generator.quality_controller import QualityController, get_quality_controller
from modules.ai_video_studio.ai_video_generator.model_router import ModelRouter, get_model_router
from modules.ai_video_studio.ai_video_generator.model_registry import ModelRegistry, get_model_registry
from modules.ai_video_studio.ai_video_generator.gpu_allocator import GPUAllocator, get_gpu_allocator
from modules.ai_video_studio.ai_video_generator.cpu_allocator import CPUAllocator, get_cpu_allocator
from modules.ai_video_studio.ai_video_generator.render_controller import RenderController, get_render_controller
from modules.ai_video_studio.ai_video_generator.pipeline_builder import PipelineBuilder, get_pipeline_builder
from modules.ai_video_studio.ai_video_generator.task_dispatcher import TaskDispatcher, get_task_dispatcher
from modules.ai_video_studio.ai_video_generator.inference_manager import InferenceManager, get_inference_manager
from modules.ai_video_studio.ai_video_generator.checkpoint_manager import CheckpointManager, get_checkpoint_manager

__all__ = [
    "VideoEngine",
    "get_video_engine",
    "GenerationManager",
    "get_generation_manager",
    "GenerationScheduler",
    "get_generation_scheduler",
    "GenerationOptimizer",
    "get_generation_optimizer",
    "GenerationStatistics",
    "get_generation_statistics",
    "GenerationMemory",
    "get_generation_memory",
    "GenerationCache",
    "get_generation_cache",
    "GenerationLogger",
    "get_generation_logger",
    "QualityController",
    "get_quality_controller",
    "ModelRouter",
    "get_model_router",
    "ModelRegistry",
    "get_model_registry",
    "GPUAllocator",
    "get_gpu_allocator",
    "CPUAllocator",
    "get_cpu_allocator",
    "RenderController",
    "get_render_controller",
    "PipelineBuilder",
    "get_pipeline_builder",
    "TaskDispatcher",
    "get_task_dispatcher",
    "InferenceManager",
    "get_inference_manager",
    "CheckpointManager",
    "get_checkpoint_manager",
]
