"""
AI guide and mentor system
"""

from .mentor_personas import (
    MentorLibrary,
    MentorPersona,
    InvestmentStyle,
    MentorPersonality,
    MentorQuote,
    InvestmentPrinciple
)

from .ai_guide_engine import (
    AIGuideEngine,
    GuidanceRequest,
    GuidanceResponse,
    GuideContext,
    GuidanceType
)

from .ai_guide_manager import (
    AIGuideManager,
    AIGuideConfig
)

__all__ = [
    # Mentor personas
    'MentorLibrary',
    'MentorPersona',
    'InvestmentStyle',
    'MentorPersonality',
    'MentorQuote',
    'InvestmentPrinciple',
    
    # AI guide engine
    'AIGuideEngine',
    'GuidanceRequest',
    'GuidanceResponse',
    'GuideContext',
    'GuidanceType',
    
    # AI guide manager
    'AIGuideManager',
    'AIGuideConfig'
]