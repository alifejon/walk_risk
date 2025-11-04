"""Risk base models"""

from enum import Enum


class RiskType(Enum):
    """리스크 유형"""
    MARKET = "market"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    
    
class RiskLevel(Enum):
    """리스크 레벨"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"