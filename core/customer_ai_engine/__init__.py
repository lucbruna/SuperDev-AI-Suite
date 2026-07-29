"""
Autonomous Customer Experience & Omnichannel AI Engine

Enterprise customer intelligence system providing:
- Intelligent chatbot & conversational support
- Voice recognition & call management
- Omnichannel integration (WhatsApp, email, web, social)
- AI-powered sales & lead analysis
- Customer support & ticket management
- Personalization & behavior analysis
- Sentiment detection & emotional analysis
- Loyalty, rewards & retention management
- Automated campaigns & workflows
"""

from .customer_engine import CustomerEngine, EngineConfig, EngineState, EngineMetrics
from .experience_manager import ExperienceManager, ManagerConfig
from .customer_context import CustomerContext
from .customer_events import CustomerEventBus, CustomerEvent, EventType
from .customer_metrics import CustomerMetrics, KPICalculator
from .customer_security import CustomerSecurityManager
from .customer_models import *
from .customer_config import CustomerConfig

from .chatbot import ChatbotEngine, ConversationManager, IntentClassifier, ResponseGenerator, KnowledgeConnector
from .voice import VoiceCustomerEngine, SpeechRecognition, VoiceResponse, CallManager
from .omnichannel import OmnichannelEngine, ChannelManager, WhatsAppConnector, EmailConnector, WebchatConnector, SocialConnector
from .sales import SalesAIEngine, LeadAnalyzer, RecommendationEngine, OfferGenerator, ConversionPredictor
from .support import SupportEngine, TicketManager, ProblemClassifier, SolutionRecommender, EscalationManager
from .personalization import PersonalizationEngine, BehaviorAnalysis, PersonalizationRecommender
from .sentiment import SentimentEngine, EmotionDetector, SatisfactionAnalysis, FeedbackProcessor
from .loyalty import LoyaltyEngine, RewardManager, CustomerScore, RetentionManager
from .automation import CustomerAutomation, CampaignEngine, TriggerManager, WorkflowEngine

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

__all__ = [
    "CustomerEngine", "EngineConfig", "EngineState", "EngineMetrics",
    "ExperienceManager", "ManagerConfig",
    "CustomerContext", "CustomerEventBus", "CustomerEvent", "EventType",
    "CustomerMetrics", "KPICalculator", "CustomerSecurityManager",
    "CustomerConfig",
    "ChatbotEngine", "ConversationManager", "IntentClassifier",
    "ResponseGenerator", "KnowledgeConnector",
    "VoiceCustomerEngine", "SpeechRecognition", "VoiceResponse", "CallManager",
    "OmnichannelEngine", "ChannelManager", "WhatsAppConnector",
    "EmailConnector", "WebchatConnector", "SocialConnector",
    "SalesAIEngine", "LeadAnalyzer", "RecommendationEngine", "OfferGenerator", "ConversionPredictor",
    "SupportEngine", "TicketManager", "ProblemClassifier", "SolutionRecommender", "EscalationManager",
    "PersonalizationEngine", "CustomerProfile", "BehaviorAnalysis", "PersonalizationRecommender",
    "SentimentEngine", "EmotionDetector", "SatisfactionAnalysis", "FeedbackProcessor",
    "LoyaltyEngine", "RewardManager", "CustomerScore", "RetentionManager",
    "CustomerAutomation", "CampaignEngine", "TriggerManager", "WorkflowEngine",
]
