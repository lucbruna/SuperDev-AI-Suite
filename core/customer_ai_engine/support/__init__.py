"""Support AI - Intelligent customer support and ticket management."""

from .support_engine import SupportEngine
from .ticket_manager import TicketManager
from .problem_classifier import ProblemClassifier
from .solution_recommender import SolutionRecommender
from .escalation import EscalationManager

__all__ = ["SupportEngine", "TicketManager", "ProblemClassifier", "SolutionRecommender", "EscalationManager"]
