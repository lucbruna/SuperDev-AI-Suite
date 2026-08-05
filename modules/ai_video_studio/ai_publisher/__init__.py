"""AI Publisher — multi-platform content publishing and distribution (Volume 7).

Orchestrates publishing pipelines for YouTube, TikTok, Instagram, Facebook,
LinkedIn and X, with scheduling, queueing, optimization, learning,
statistics, history, reports and notifications. Real logic, simulated
platform clients when credentials are absent.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_publisher.publisher_engine import PublisherEngine, get_publisher_engine
from modules.ai_video_studio.ai_publisher.publisher_manager import PublisherManager, get_publisher_manager
from modules.ai_video_studio.ai_publisher.publisher_scheduler import PublisherScheduler, get_publisher_scheduler
from modules.ai_video_studio.ai_publisher.publisher_queue import PublisherQueue, get_publisher_queue
from modules.ai_video_studio.ai_publisher.publisher_optimizer import PublisherOptimizer, get_publisher_optimizer
from modules.ai_video_studio.ai_publisher.publisher_learning import PublisherLearning, get_publisher_learning
from modules.ai_video_studio.ai_publisher.publisher_statistics import PublisherStatistics, get_publisher_statistics
from modules.ai_video_studio.ai_publisher.publisher_logger import PublisherLogger, get_publisher_logger
from modules.ai_video_studio.ai_publisher.publisher_history import PublisherHistory, get_publisher_history
from modules.ai_video_studio.ai_publisher.publisher_reports import PublisherReports, get_publisher_reports
from modules.ai_video_studio.ai_publisher.publisher_notifications import PublisherNotifications, get_publisher_notifications

__all__ = [
    "PublisherEngine",
    "get_publisher_engine",
    "PublisherManager",
    "get_publisher_manager",
    "PublisherScheduler",
    "get_publisher_scheduler",
    "PublisherQueue",
    "get_publisher_queue",
    "PublisherOptimizer",
    "get_publisher_optimizer",
    "PublisherLearning",
    "get_publisher_learning",
    "PublisherStatistics",
    "get_publisher_statistics",
    "PublisherLogger",
    "get_publisher_logger",
    "PublisherHistory",
    "get_publisher_history",
    "PublisherReports",
    "get_publisher_reports",
    "PublisherNotifications",
    "get_publisher_notifications",
]
