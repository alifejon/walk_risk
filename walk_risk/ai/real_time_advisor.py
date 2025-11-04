"""Real-time Investment Advisor - 실시간 투자 조언 시스템"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .mentor_personas import BuffettPersona
from ..models.portfolio.real_portfolio import RealPortfolio, PortfolioPosition
from ..data.market_data.yahoo_finance import yahoo_finance, MarketSummary, StockData
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class AdviceType(Enum):
    """조언 유형"""
    MARKET_ANALYSIS = "market_analysis"  # 시장 분석
    PORTFOLIO_REVIEW = "portfolio_review"  # 포트폴리오 리뷰
    RISK_WARNING = "risk_warning"  # 리스크 경고
    OPPORTUNITY = "opportunity"  # 투자 기회
    EMOTIONAL_GUIDANCE = "emotional_guidance"  # 감정 가이드
    REBALANCING = "rebalancing"  # 리밸런싱 제안


class AdvicePriority(Enum):
    """조언 우선순위"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AdviceMessage:
    """조언 메시지"""
    id: str
    mentor_name: str
    advice_type: AdviceType
    priority: AdvicePriority
    title: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_read: bool = False
    
    @property
    def is_expired(self) -> bool:
        return self.expires_at and datetime.now() > self.expires_at
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "mentor_name": self.mentor_name,
            "advice_type": self.advice_type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_read": self.is_read
        }


class RealTimeAdvisor:
    """
    실시간 투자 조언 시스템
    
    실시간 시장 데이터와 포트폴리오 상태를 분석하여
    적절한 투자 조언을 제공합니다.
    """
    
    def __init__(self):
        self.buffett = BuffettPersona()
        self.advice_history: List[AdviceMessage] = []
        self.last_market_check = datetime.now() - timedelta(hours=1)
        self.last_portfolio_check = datetime.now() - timedelta(hours=1)
        
        # 조언 설정
        self.market_volatility_threshold = 0.03  # 3% 이상 변동 시 알림
        self.position_loss_threshold = -0.10  # -10% 이상 손실 시 알림
        self.concentration_threshold = 0.30  # 30% 이상 집중 시 경고
        
    async def analyze_and_advise(
        self, 
        portfolio: RealPortfolio,
        force_analysis: bool = False
    ) -> List[AdviceMessage]:
        """포트폴리오와 시장 분석 후 조언 생성"""
        new_advice = []
        current_time = datetime.now()
        
        try:
            # 시장 분석 (매 30분마다 또는 강제 실행)
            if (current_time - self.last_market_check).seconds > 1800 or force_analysis:
                market_advice = await self._analyze_market_conditions(portfolio)
                new_advice.extend(market_advice)
                self.last_market_check = current_time
                
            # 포트폴리오 분석 (매 1시간마다 또는 강제 실행)
            if (current_time - self.last_portfolio_check).seconds > 3600 or force_analysis:
                portfolio_advice = await self._analyze_portfolio(portfolio)
                new_advice.extend(portfolio_advice)
                self.last_portfolio_check = current_time
                
            # 새로운 조언만 반환
            self.advice_history.extend(new_advice)
            
            # 오래된 조언 정리 (100개 이상 시 오래된 것 제거)
            if len(self.advice_history) > 100:
                self.advice_history = self.advice_history[-100:]
                
            return new_advice
            
        except Exception as e:
            logger.error(f"실시간 분석 오류: {e}")
            return []
            
    async def _analyze_market_conditions(self, portfolio: RealPortfolio) -> List[AdviceMessage]:
        """시장 상황 분석"""
        advice_list = []
        
        try:
            # 시장 지수 정보 수집
            market_summary = await yahoo_finance.get_market_summary()
            if not market_summary:
                return advice_list
                
            # 시장 변동성 분석
            kospi_volatility = abs(market_summary.kospi_change_percent) / 100
            kosdaq_volatility = abs(market_summary.kosdaq_change_percent) / 100
            avg_volatility = (kospi_volatility + kosdaq_volatility) / 2
            
            # 고변동성 경고
            if avg_volatility > self.market_volatility_threshold:
                if market_summary.market_sentiment == "bearish":
                    advice = self._create_market_fear_advice(market_summary, avg_volatility)
                elif market_summary.market_sentiment == "bullish":
                    advice = self._create_market_greed_advice(market_summary, avg_volatility)
                else:
                    advice = self._create_market_neutral_advice(market_summary, avg_volatility)
                    
                advice_list.append(advice)
                
            # 시장 기회 발견
            opportunity_advice = await self._find_market_opportunities(portfolio, market_summary)
            if opportunity_advice:
                advice_list.append(opportunity_advice)
                
        except Exception as e:
            logger.error(f"시장 분석 오류: {e}")
            
        return advice_list
        
    async def _analyze_portfolio(self, portfolio: RealPortfolio) -> List[AdviceMessage]:
        """포트폴리오 분석"""
        advice_list = []
        
        try:
            # 포트폴리오 가격 업데이트
            await portfolio.update_all_prices()
            
            # 대형 손실 경고
            loss_advice = self._check_major_losses(portfolio)
            if loss_advice:
                advice_list.append(loss_advice)
                
            # 집중도 분석
            concentration_advice = self._check_concentration_risk(portfolio)
            if concentration_advice:
                advice_list.append(concentration_advice)
                
            # 리밸런싱 제안
            rebalancing_advice = self._suggest_rebalancing(portfolio)
            if rebalancing_advice:
                advice_list.append(rebalancing_advice)
                
            # 성과 칭찬
            performance_advice = self._review_performance(portfolio)
            if performance_advice:
                advice_list.append(performance_advice)
                
        except Exception as e:
            logger.error(f"포트폴리오 분석 오류: {e}")
            
        return advice_list
        
    def _create_market_fear_advice(self, market_summary: MarketSummary, volatility: float) -> AdviceMessage:
        """시장 공포 상황 조언"""
        return AdviceMessage(
            id=f"market_fear_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mentor_name=self.buffett.name,
            advice_type=AdviceType.EMOTIONAL_GUIDANCE,
            priority=AdvicePriority.HIGH,
            title="🚨 시장 공포 상황 - 기회를 찾으세요",
            message=f"""
🏛️ {self.buffett.name}: "다른 사람들이 두려워할 때 탐욕스럽게 행동하세요."

현재 시장 상황:
• KOSPI: {market_summary.kospi_change_percent:+.2f}%
• KOSDAQ: {market_summary.kosdaq_change_percent:+.2f}%
• 변동성: {volatility*100:.1f}%

이런 때일수록 냉정을 유지하고 좋은 기업의 주가가 저렴할 때 매수 기회를 찾아보세요.
            """.strip(),
            context={
                "kospi_change": market_summary.kospi_change_percent,
                "kosdaq_change": market_summary.kosdaq_change_percent,
                "volatility": volatility,
                "sentiment": "bearish"
            },
            expires_at=datetime.now() + timedelta(hours=6)
        )
        
    def _create_market_greed_advice(self, market_summary: MarketSummary, volatility: float) -> AdviceMessage:
        """시장 과열 상황 조언"""
        return AdviceMessage(
            id=f"market_greed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mentor_name=self.buffett.name,
            advice_type=AdviceType.RISK_WARNING,
            priority=AdvicePriority.MEDIUM,
            title="⚠️ 시장 과열 - 주의깊게 지켜보세요",
            message=f"""
🏛️ {self.buffett.name}: "탐욕스러울 때 두려워하세요."

현재 시장이 과도하게 상승하고 있습니다:
• KOSPI: {market_summary.kospi_change_percent:+.2f}%
• KOSDAQ: {market_summary.kosdaq_change_percent:+.2f}%

이럴 때일수록 신중해야 합니다. 이익을 실현할 기회를 고려해보고, 새로운 투자는 신중하게 결정하세요.
            """.strip(),
            context={
                "kospi_change": market_summary.kospi_change_percent,
                "kosdaq_change": market_summary.kosdaq_change_percent,
                "volatility": volatility,
                "sentiment": "bullish"
            },
            expires_at=datetime.now() + timedelta(hours=4)
        )
        
    def _create_market_neutral_advice(self, market_summary: MarketSummary, volatility: float) -> AdviceMessage:
        """시장 중립 상황 조언"""
        return AdviceMessage(
            id=f"market_neutral_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            mentor_name=self.buffett.name,
            advice_type=AdviceType.MARKET_ANALYSIS,
            priority=AdvicePriority.LOW,
            title="📊 시장 변동성 증가 - 원칙을 지키세요",
            message=f"""
🏛️ {self.buffett.name}: "변동성이 클 때일수록 원칙에 충실해야 합니다."

시장에 변동성이 증가하고 있습니다 ({volatility*100:.1f}%).
이럴 때일수록:
• 계획된 투자 전략을 고수하세요
• 감정에 휩싸리지 마세요
• 기본에 충실한 기업을 찾으세요
            """.strip(),
            context={
                "volatility": volatility,
                "sentiment": "neutral"
            },
            expires_at=datetime.now() + timedelta(hours=2)
        )
        
    async def _find_market_opportunities(self, portfolio: RealPortfolio, market_summary: MarketSummary) -> Optional[AdviceMessage]:
        """시장 기회 발견"""
        # 하락장에서 좋은 기업 찾기
        if market_summary.market_sentiment == "bearish":
            return AdviceMessage(
                id=f"opportunity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mentor_name=self.buffett.name,
                advice_type=AdviceType.OPPORTUNITY,
                priority=AdvicePriority.MEDIUM,
                title="🔍 투자 기회 발견",
                message=f"""
🏛️ {self.buffett.name}: "위기는 기회의 다른 이름입니다."

현재 시장 하락으로 우량 기업들의 주가가 저렴해지고 있습니다.

고려할 만한 우량 기업들:
• 삼성전자: 글로벌 반도체 리더
• POSCO홀딩스: 철강 업계 1위
• KB금융: 안정적인 배당 수익

하지만 충분한 분석 후 신중하게 결정하세요.
                """.strip(),
                context={
                    "market_sentiment": "bearish",
                    "suggested_stocks": ["005930.KS", "005490.KS", "105560.KS"]
                },
                expires_at=datetime.now() + timedelta(hours=12)
            )
        return None
        
    def _check_major_losses(self, portfolio: RealPortfolio) -> Optional[AdviceMessage]:
        """대형 손실 체크"""
        major_loss_positions = []
        
        for symbol, position in portfolio.positions.items():
            if position.unrealized_pnl_percent < self.position_loss_threshold * 100:
                major_loss_positions.append({
                    "symbol": symbol,
                    "name": position.name,
                    "loss_percent": position.unrealized_pnl_percent
                })
                
        if major_loss_positions:
            loss_details = "\n".join([
                f"• {pos['name']}: {pos['loss_percent']:+.1f}%" 
                for pos in major_loss_positions
            ])
            
            return AdviceMessage(
                id=f"major_loss_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mentor_name=self.buffett.name,
                advice_type=AdviceType.RISK_WARNING,
                priority=AdvicePriority.HIGH,
                title="🚨 대형 손실 발생",
                message=f"""
🏛️ {self.buffett.name}: "손실이 발생했을 때 가장 중요한 것은 상황을 냉정하게 분석하는 것입니다."

현재 대형 손실을 기록하고 있는 종목들:
{loss_details}

다음 사항을 검토해보세요:
1. 해당 기업의 펼더멘털이 변했나요?
2. 일시적인 시장 상황인가요?
3. 손절매가 필요한 상황인가요?

급한 결정보다는 신중한 분석이 중요합니다.
                """.strip(),
                context={
                    "major_losses": major_loss_positions
                },
                expires_at=datetime.now() + timedelta(hours=24)
            )
        return None
        
    def _check_concentration_risk(self, portfolio: RealPortfolio) -> Optional[AdviceMessage]:
        """집중도 리스크 체크"""
        if not portfolio.positions:
            return None
            
        allocation = portfolio.asset_allocation
        concentrated_positions = []
        
        for symbol, percentage in allocation.items():
            if symbol != "cash" and percentage > self.concentration_threshold * 100:
                position = portfolio.positions.get(symbol)
                if position:
                    concentrated_positions.append({
                        "symbol": symbol,
                        "name": position.name,
                        "allocation": percentage
                    })
                    
        if concentrated_positions:
            concentration_details = "\n".join([
                f"• {pos['name']}: {pos['allocation']:.1f}%" 
                for pos in concentrated_positions
            ])
            
            return AdviceMessage(
                id=f"concentration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mentor_name=self.buffett.name,
                advice_type=AdviceType.RISK_WARNING,
                priority=AdvicePriority.MEDIUM,
                title="⚠️ 포트폴리오 집중도 경고",
                message=f"""
🏛️ {self.buffett.name}: "계란을 한 바구니에 담지 마세요."

현재 포트폴리오가 특정 종목에 과도하게 집중되어 있습니다:
{concentration_details}

분산투자를 고려해보세요:
• 다른 업종으로 분산
• ETF를 통한 간접 분산
• 일부 이익 실현 고려

리스크 대비 수익을 최적화하는 것이 핵심입니다.
                """.strip(),
                context={
                    "concentrated_positions": concentrated_positions
                },
                expires_at=datetime.now() + timedelta(days=1)
            )
        return None
        
    def _suggest_rebalancing(self, portfolio: RealPortfolio) -> Optional[AdviceMessage]:
        """리밸런싱 제안"""
        # 간단한 리밸런싱 로직 (포트폴리오가 충분히 성장했을 때)
        if portfolio.total_return_percent > 20 and len(portfolio.positions) > 0:
            return AdviceMessage(
                id=f"rebalancing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mentor_name=self.buffett.name,
                advice_type=AdviceType.REBALANCING,
                priority=AdvicePriority.LOW,
                title="🔄 리밸런싱 고려 시기",
                message=f"""
🏛️ {self.buffett.name}: "정기적인 리밸런싱은 좋은 투자 습관입니다."

현재 총 수익률: {portfolio.total_return_percent:+.1f}%

포트폴리오가 좋은 성과를 보이고 있습니다. 이제 다음을 고려해보세요:

• 이익이 많이 난 종목의 일부 매도
• 새로운 투자 기회 탐색
• 현금 비중 조정

성공적인 투자일수록 계속 학습하고 개선해나가야 합니다.
                """.strip(),
                context={
                    "total_return": portfolio.total_return_percent
                },
                expires_at=datetime.now() + timedelta(days=3)
            )
        return None
        
    def _review_performance(self, portfolio: RealPortfolio) -> Optional[AdviceMessage]:
        """성과 리뷰"""
        # 좋은 성과에 대한 격려
        if portfolio.total_return_percent > 10:
            return AdviceMessage(
                id=f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                mentor_name=self.buffett.name,
                advice_type=AdviceType.PORTFOLIO_REVIEW,
                priority=AdvicePriority.LOW,
                title="🎉 좋은 투자 성과!",
                message=f"""
🏛️ {self.buffett.name}: "훌륭합니다! 하지만 방심하지 마세요."

현재 수익률: {portfolio.total_return_percent:+.1f}%
총 자산: {portfolio.total_portfolio_value:,.0f}원

좋은 성과를 보이고 있습니다. 이제 다음 단계를 준비하세요:

• 성공 요인 분석
• 지속 가능한 전략 수립
• 다음 목표 설정

기억하세요: 진정한 투자자는 단기 성과보다 장기 성장에 집중합니다.
                """.strip(),
                context={
                    "total_return": portfolio.total_return_percent,
                    "total_value": portfolio.total_portfolio_value
                },
                expires_at=datetime.now() + timedelta(days=7)
            )
        return None
        
    def get_recent_advice(self, limit: int = 10) -> List[AdviceMessage]:
        """최근 조언 조회"""
        # 만료되지 않은 조언만 반환
        valid_advice = [
            advice for advice in self.advice_history 
            if not advice.is_expired
        ]
        
        return valid_advice[-limit:] if limit > 0 else valid_advice
        
    def mark_advice_read(self, advice_id: str) -> bool:
        """조언 읽음 처리"""
        for advice in self.advice_history:
            if advice.id == advice_id:
                advice.is_read = True
                return True
        return False
        
    def get_advice_summary(self) -> Dict[str, Any]:
        """조언 요약 정보"""
        recent_advice = self.get_recent_advice()
        
        return {
            "total_advice_count": len(self.advice_history),
            "recent_advice_count": len(recent_advice),
            "unread_count": len([a for a in recent_advice if not a.is_read]),
            "urgent_count": len([a for a in recent_advice if a.priority == AdvicePriority.URGENT]),
            "high_priority_count": len([a for a in recent_advice if a.priority == AdvicePriority.HIGH]),
            "last_advice_time": self.advice_history[-1].created_at.isoformat() if self.advice_history else None
        }


# 전역 인스턴스
real_time_advisor = RealTimeAdvisor()