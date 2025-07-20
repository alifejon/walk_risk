"""
Base risk model definitions
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import uuid4


class RiskLevel(Enum):
    """Risk severity levels"""
    LOCKED = "locked"      # 🔒 아직 이해하지 못한 리스크
    UNLOCKING = "unlocking"  # 🔓 분석 중인 리스크
    UNLOCKED = "unlocked"    # 🔑 정복한 리스크
    MASTERED = "mastered"    # 💎 기회로 전환한 리스크


class RiskCategory(Enum):
    """Risk categories based on game design"""
    MARKET = "market"           # 시장 리스크
    CREDIT = "credit"           # 신용 리스크
    OPERATIONAL = "operational"  # 운영 리스크
    STRATEGIC = "strategic"     # 전략 리스크
    LIQUIDITY = "liquidity"     # 유동성 리스크
    GEOPOLITICAL = "geopolitical"  # 지정학적 리스크


@dataclass
class RiskKey:
    """Risk unlocking key"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    key_type: str = "knowledge"  # knowledge, experience, wisdom
    description: str = ""
    unlock_conditions: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RiskMetrics:
    """Risk measurement metrics"""
    volatility: float = 0.0
    correlation: float = 0.0
    var_95: float = 0.0  # Value at Risk 95%
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    beta: float = 1.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class Risk:
    """Base risk model"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    category: RiskCategory = RiskCategory.MARKET
    level: RiskLevel = RiskLevel.LOCKED
    description: str = ""
    
    # Risk characteristics
    severity: float = 0.0  # 0-1 scale
    complexity: float = 0.0  # 0-1 scale
    frequency: float = 0.0  # Expected frequency
    
    # Unlock requirements
    required_keys: List[RiskKey] = field(default_factory=list)
    minimum_keys: int = 1
    
    # Metrics and data
    metrics: RiskMetrics = field(default_factory=RiskMetrics)
    real_time_data: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    unlocked_at: Optional[datetime] = None
    
    def update_level(self, new_level: RiskLevel) -> None:
        """Update risk level and timestamp"""
        self.level = new_level
        self.updated_at = datetime.now()
        
        if new_level in [RiskLevel.UNLOCKED, RiskLevel.MASTERED]:
            self.unlocked_at = datetime.now()
    
    def calculate_unlock_difficulty(self) -> float:
        """Calculate unlock difficulty based on risk characteristics"""
        return (self.severity * 0.4 + self.complexity * 0.4 + 
                (len(self.required_keys) / 10) * 0.2)
    
    def is_unlockable(self, player_keys: List[RiskKey]) -> bool:
        """Check if risk can be unlocked with given keys"""
        matching_keys = [
            key for key in player_keys 
            if any(req.key_type == key.key_type for req in self.required_keys)
        ]
        return len(matching_keys) >= self.minimum_keys


class RiskAnalyzer(ABC):
    """Abstract base class for risk analysis"""
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Risk:
        """Analyze data and return Risk object"""
        pass
    
    @abstractmethod
    def calculate_metrics(self, data: Dict[str, Any]) -> RiskMetrics:
        """Calculate risk metrics from data"""
        pass
    
    @abstractmethod
    def determine_severity(self, metrics: RiskMetrics) -> float:
        """Determine risk severity from metrics"""
        pass