"""
Risk factory for creating and managing different types of risks
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum

from ...models.risk.base import Risk, RiskCategory, RiskLevel, RiskKey, RiskAnalyzer
from ...data.sources.base import MarketData
from .risk_analyzer import MarketRiskAnalyzer, LiquidityRiskAnalyzer, RiskEventDetector, RiskAlert
from ...utils.logger import logger


class RiskFactoryType(Enum):
    """Types of risk factories"""
    MARKET = "market"
    CREDIT = "credit"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    LIQUIDITY = "liquidity"
    GEOPOLITICAL = "geopolitical"


@dataclass
class RiskTemplate:
    """Template for creating risks"""
    name: str
    category: RiskCategory
    base_severity: float = 0.5
    base_complexity: float = 0.5
    required_keys: List[str] = field(default_factory=list)
    description_template: str = ""
    
    def create_keys(self) -> List[RiskKey]:
        """Create required keys for this risk template"""
        keys = []
        for key_name in self.required_keys:
            key = RiskKey(
                name=key_name,
                key_type=self._determine_key_type(key_name),
                description=f"{key_name}에 대한 이해"
            )
            keys.append(key)
        return keys
    
    def _determine_key_type(self, key_name: str) -> str:
        """Determine key type based on name"""
        knowledge_keys = ['theory', 'analysis', 'calculation', 'pattern']
        experience_keys = ['survival', 'precision', 'speed', 'defense']
        wisdom_keys = ['patience', 'foresight', 'balance', 'master']
        
        key_lower = key_name.lower()
        
        for kw in knowledge_keys:
            if kw in key_lower:
                return 'knowledge'
        
        for kw in experience_keys:
            if kw in key_lower:
                return 'experience'
        
        for kw in wisdom_keys:
            if kw in key_lower:
                return 'wisdom'
        
        return 'knowledge'  # Default


class RiskFactory:
    """Factory for creating and managing risks"""
    
    def __init__(self):
        self.analyzers: Dict[RiskCategory, RiskAnalyzer] = {}
        self.event_detector = RiskEventDetector()
        self.risk_templates: Dict[str, RiskTemplate] = {}
        self.active_risks: Dict[str, Risk] = {}
        
        # Initialize analyzers
        self.analyzers[RiskCategory.MARKET] = MarketRiskAnalyzer()
        self.analyzers[RiskCategory.LIQUIDITY] = LiquidityRiskAnalyzer()
        
        # Initialize risk templates
        self._initialize_risk_templates()
    
    def _initialize_risk_templates(self) -> None:
        """Initialize predefined risk templates"""
        
        # Market Risk Templates
        self.risk_templates["volatility_risk"] = RiskTemplate(
            name="변동성 리스크",
            category=RiskCategory.MARKET,
            base_severity=0.6,
            base_complexity=0.4,
            required_keys=["volatility_analysis", "pattern_recognition"],
            description_template="시장 변동성으로 인한 가격 불확실성 리스크"
        )
        
        self.risk_templates["correlation_risk"] = RiskTemplate(
            name="상관관계 리스크",
            category=RiskCategory.MARKET,
            base_severity=0.5,
            base_complexity=0.7,
            required_keys=["correlation_analysis", "portfolio_theory"],
            description_template="자산 간 상관관계 변화로 인한 리스크"
        )
        
        self.risk_templates["momentum_risk"] = RiskTemplate(
            name="모멘텀 리스크",
            category=RiskCategory.MARKET,
            base_severity=0.4,
            base_complexity=0.6,
            required_keys=["trend_analysis", "momentum_calculation"],
            description_template="가격 모멘텀 변화로 인한 리스크"
        )
        
        # Liquidity Risk Templates
        self.risk_templates["liquidity_shortage"] = RiskTemplate(
            name="유동성 부족 리스크",
            category=RiskCategory.LIQUIDITY,
            base_severity=0.7,
            base_complexity=0.5,
            required_keys=["volume_analysis", "market_depth"],
            description_template="거래량 부족으로 인한 유동성 리스크"
        )
        
        self.risk_templates["bid_ask_spread"] = RiskTemplate(
            name="스프레드 리스크",
            category=RiskCategory.LIQUIDITY,
            base_severity=0.4,
            base_complexity=0.3,
            required_keys=["spread_analysis", "market_making"],
            description_template="매수-매도 스프레드 확대 리스크"
        )
        
        # Credit Risk Templates (placeholders for future implementation)
        self.risk_templates["counterparty_risk"] = RiskTemplate(
            name="거래상대방 리스크",
            category=RiskCategory.CREDIT,
            base_severity=0.8,
            base_complexity=0.8,
            required_keys=["credit_analysis", "default_probability"],
            description_template="거래상대방 신용도 악화 리스크"
        )
        
        # Operational Risk Templates
        self.risk_templates["system_failure"] = RiskTemplate(
            name="시스템 장애 리스크",
            category=RiskCategory.OPERATIONAL,
            base_severity=0.9,
            base_complexity=0.7,
            required_keys=["system_analysis", "failure_recovery"],
            description_template="거래 시스템 장애로 인한 운영 리스크"
        )
        
        # Strategic Risk Templates
        self.risk_templates["regulatory_change"] = RiskTemplate(
            name="규제 변화 리스크",
            category=RiskCategory.STRATEGIC,
            base_severity=0.6,
            base_complexity=0.9,
            required_keys=["regulatory_analysis", "policy_impact"],
            description_template="규제 환경 변화로 인한 전략적 리스크"
        )
    
    async def create_risk_from_market_data(
        self, 
        symbol: str, 
        market_data: MarketData, 
        historical_data: List[MarketData] = None,
        risk_category: RiskCategory = RiskCategory.MARKET
    ) -> Optional[Risk]:
        """Create risk from market data"""
        try:
            # Get appropriate analyzer
            analyzer = self.analyzers.get(risk_category)
            if not analyzer:
                logger.warning(f"No analyzer found for category: {risk_category}")
                return None
            
            # Prepare data for analysis
            analysis_data = {
                'symbol': symbol,
                'market_data': market_data,
                'historical_data': historical_data or []
            }
            
            # Analyze and create risk
            risk = await analyzer.analyze(analysis_data)
            
            # Store active risk
            self.active_risks[risk.id] = risk
            
            logger.info(f"리스크 생성: {risk.name} (심각도: {risk.severity:.2f})")
            return risk
            
        except Exception as e:
            logger.error(f"리스크 생성 실패: {e}")
            return None
    
    async def create_risk_from_template(
        self, 
        template_name: str, 
        symbol: str = "", 
        custom_data: Dict[str, Any] = None
    ) -> Optional[Risk]:
        """Create risk from predefined template"""
        try:
            template = self.risk_templates.get(template_name)
            if not template:
                logger.warning(f"Risk template not found: {template_name}")
                return None
            
            # Create risk from template
            risk = Risk(
                name=f"{template.name} - {symbol}" if symbol else template.name,
                category=template.category,
                description=template.description_template,
                severity=template.base_severity,
                complexity=template.base_complexity,
                required_keys=template.create_keys()
            )
            
            # Apply custom data if provided
            if custom_data:
                if 'severity' in custom_data:
                    risk.severity = custom_data['severity']
                if 'complexity' in custom_data:
                    risk.complexity = custom_data['complexity']
                if 'description' in custom_data:
                    risk.description = custom_data['description']
            
            # Store active risk
            self.active_risks[risk.id] = risk
            
            logger.info(f"템플릿 리스크 생성: {risk.name}")
            return risk
            
        except Exception as e:
            logger.error(f"템플릿 리스크 생성 실패: {e}")
            return None
    
    async def detect_risk_events(
        self, 
        symbol: str, 
        current_data: MarketData, 
        historical_data: List[MarketData] = None
    ) -> List[RiskAlert]:
        """Detect risk events from market data"""
        try:
            alerts = await self.event_detector.detect_events(
                symbol, 
                current_data, 
                historical_data or []
            )
            
            # Create risks from alerts if severity is high enough
            for alert in alerts:
                if alert.severity > 0.7:  # High severity threshold
                    await self._create_risk_from_alert(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"리스크 이벤트 감지 실패: {e}")
            return []
    
    async def _create_risk_from_alert(self, alert: RiskAlert) -> Optional[Risk]:
        """Create risk from alert"""
        try:
            # Determine risk category based on alert type
            category_mapping = {
                'volatility_spike': RiskCategory.MARKET,
                'price_crash': RiskCategory.MARKET,
                'volume_anomaly': RiskCategory.LIQUIDITY,
                'liquidity_crisis': RiskCategory.LIQUIDITY,
                'flash_crash': RiskCategory.MARKET
            }
            
            category = category_mapping.get(alert.event_type.value, RiskCategory.MARKET)
            
            # Create risk
            risk = Risk(
                name=f"Event Risk - {alert.event_type.value}",
                category=category,
                description=alert.description,
                severity=alert.severity,
                complexity=min(alert.severity + 0.2, 1.0),
                frequency=0.1,  # Event-based risks are typically low frequency
                real_time_data=alert.data
            )
            
            # Set appropriate level based on severity
            if alert.severity > 0.8:
                risk.level = RiskLevel.UNLOCKED
            elif alert.severity > 0.5:
                risk.level = RiskLevel.UNLOCKING
            else:
                risk.level = RiskLevel.LOCKED
            
            # Store active risk
            self.active_risks[risk.id] = risk
            
            logger.info(f"알림 기반 리스크 생성: {risk.name} (심각도: {risk.severity:.2f})")
            return risk
            
        except Exception as e:
            logger.error(f"알림 기반 리스크 생성 실패: {e}")
            return None
    
    def get_active_risks(self, category: Optional[RiskCategory] = None) -> List[Risk]:
        """Get active risks, optionally filtered by category"""
        risks = list(self.active_risks.values())
        
        if category:
            risks = [risk for risk in risks if risk.category == category]
        
        return sorted(risks, key=lambda r: r.severity, reverse=True)
    
    def get_risk_by_id(self, risk_id: str) -> Optional[Risk]:
        """Get specific risk by ID"""
        return self.active_risks.get(risk_id)
    
    def update_risk_level(self, risk_id: str, new_level: RiskLevel) -> bool:
        """Update risk level"""
        risk = self.active_risks.get(risk_id)
        if risk:
            risk.update_level(new_level)
            logger.info(f"리스크 레벨 업데이트: {risk.name} -> {new_level.value}")
            return True
        return False
    
    def remove_risk(self, risk_id: str) -> bool:
        """Remove risk from active risks"""
        if risk_id in self.active_risks:
            risk = self.active_risks.pop(risk_id)
            logger.info(f"리스크 제거: {risk.name}")
            return True
        return False
    
    def get_risk_statistics(self) -> Dict[str, Any]:
        """Get statistics about active risks"""
        if not self.active_risks:
            return {
                'total_risks': 0,
                'by_category': {},
                'by_level': {},
                'avg_severity': 0.0,
                'avg_complexity': 0.0
            }
        
        risks = list(self.active_risks.values())
        
        # Count by category
        by_category = {}
        for category in RiskCategory:
            count = sum(1 for r in risks if r.category == category)
            by_category[category.value] = count
        
        # Count by level
        by_level = {}
        for level in RiskLevel:
            count = sum(1 for r in risks if r.level == level)
            by_level[level.value] = count
        
        # Calculate averages
        avg_severity = sum(r.severity for r in risks) / len(risks)
        avg_complexity = sum(r.complexity for r in risks) / len(risks)
        
        return {
            'total_risks': len(risks),
            'by_category': by_category,
            'by_level': by_level,
            'avg_severity': avg_severity,
            'avg_complexity': avg_complexity,
            'highest_severity': max(r.severity for r in risks),
            'most_complex': max(r.complexity for r in risks)
        }
    
    def get_recent_alerts(self, hours: int = 24) -> List[RiskAlert]:
        """Get recent risk alerts"""
        return self.event_detector.get_recent_alerts(hours)
    
    def get_alerts_by_symbol(self, symbol: str, hours: int = 24) -> List[RiskAlert]:
        """Get alerts for specific symbol"""
        return self.event_detector.get_alerts_by_symbol(symbol, hours)
    
    async def cleanup_old_risks(self, max_age_hours: int = 72) -> int:
        """Clean up old risks"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_risk_ids = []
        
        for risk_id, risk in self.active_risks.items():
            if risk.created_at < cutoff_time and risk.level == RiskLevel.LOCKED:
                old_risk_ids.append(risk_id)
        
        # Remove old risks
        for risk_id in old_risk_ids:
            self.remove_risk(risk_id)
        
        logger.info(f"오래된 리스크 {len(old_risk_ids)}개 정리")
        return len(old_risk_ids)
    
    def add_risk_template(self, name: str, template: RiskTemplate) -> None:
        """Add custom risk template"""
        self.risk_templates[name] = template
        logger.info(f"리스크 템플릿 추가: {name}")
    
    def list_risk_templates(self) -> List[str]:
        """List available risk templates"""
        return list(self.risk_templates.keys())
    
    def get_risk_template(self, name: str) -> Optional[RiskTemplate]:
        """Get risk template by name"""
        return self.risk_templates.get(name)