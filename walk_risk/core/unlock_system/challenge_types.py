"""
Specific challenge implementations for different risk types
"""
import random
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from ...models.risk.base import Risk, RiskCategory
from ...models.player.base import Player
from .unlock_engine import UnlockChallenge


class ChallengeLibrary:
    """Library of pre-built challenges for different scenarios"""
    
    @staticmethod
    def create_market_crash_challenge(severity: float = 0.8) -> UnlockChallenge:
        """Create a market crash scenario challenge"""
        crash_magnitude = -0.2 * severity  # Up to -20% crash
        
        return UnlockChallenge(
            challenge_type="market_crash_response",
            description=f"시장이 {abs(crash_magnitude):.1%} 급락했습니다. 다음 중 가장 적절한 대응은?",
            difficulty=severity,
            time_limit=180,
            hints=[
                "공포에 휩쓸리지 말고 냉정하게 판단하세요",
                "장기 투자 관점을 유지하세요",
                "기회로 볼 수도 있습니다"
            ],
            correct_answer="maintain_discipline"
        )
    
    @staticmethod
    def create_volatility_spike_challenge(vix_level: float = 40.0) -> UnlockChallenge:
        """Create volatility spike challenge"""
        return UnlockChallenge(
            challenge_type="volatility_management",
            description=f"VIX 지수가 {vix_level:.1f}로 급등했습니다. 변동성이 포트폴리오에 미치는 영향을 분석하세요.",
            difficulty=min(1.0, vix_level / 50.0),
            time_limit=240,
            hints=[
                "VIX는 공포 지수라고도 불립니다",
                "높은 변동성은 기회이자 위험입니다",
                "옵션 가격에도 영향을 미칩니다"
            ],
            correct_answer=vix_level
        )
    
    @staticmethod
    def create_interest_rate_challenge(rate_change: float = 0.02) -> UnlockChallenge:
        """Create interest rate change challenge"""
        direction = "인상" if rate_change > 0 else "인하"
        
        return UnlockChallenge(
            challenge_type="interest_rate_impact",
            description=f"중앙은행이 기준금리를 {abs(rate_change):.1%}p {direction}했습니다. 각 자산군에 미치는 영향을 예측하세요.",
            difficulty=0.6,
            time_limit=300,
            hints=[
                "채권과 주식에 미치는 영향이 다릅니다",
                "금리 민감 섹터들을 고려하세요",
                "통화 가치 변화도 중요합니다"
            ],
            correct_answer={
                "bonds": "negative" if rate_change > 0 else "positive",
                "stocks": "mixed",
                "currency": "positive" if rate_change > 0 else "negative"
            }
        )
    
    @staticmethod
    def create_earnings_surprise_challenge(surprise: float = 0.15) -> UnlockChallenge:
        """Create earnings surprise challenge"""
        direction = "상향" if surprise > 0 else "하향"
        
        return UnlockChallenge(
            challenge_type="earnings_analysis",
            description=f"주요 기업의 실적이 예상보다 {abs(surprise):.1%} {direction} 발표되었습니다. 주가 반응을 예측하고 투자 전략을 수립하세요.",
            difficulty=0.5,
            time_limit=200,
            hints=[
                "실적 서프라이즈의 크기를 고려하세요",
                "가이던스 변화도 중요합니다",
                "섹터 전체에 미치는 영향을 생각해보세요"
            ],
            correct_answer=surprise
        )


class InteractiveChallenge:
    """Interactive challenge with step-by-step guidance"""
    
    def __init__(self, challenge_type: str, risk: Risk):
        self.challenge_type = challenge_type
        self.risk = risk
        self.steps = []
        self.current_step = 0
        self.user_inputs = {}
        self.score = 0.0
    
    def add_step(self, step_description: str, expected_answer: Any, hints: List[str] = None):
        """Add a step to the interactive challenge"""
        self.steps.append({
            'description': step_description,
            'expected_answer': expected_answer,
            'hints': hints or [],
            'completed': False,
            'user_answer': None,
            'score': 0.0
        })
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get current step information"""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def submit_step_answer(self, answer: Any) -> bool:
        """Submit answer for current step"""
        if self.current_step >= len(self.steps):
            return False
        
        step = self.steps[self.current_step]
        step['user_answer'] = answer
        step['score'] = self._evaluate_step_answer(step, answer)
        step['completed'] = True
        
        self.current_step += 1
        return True
    
    def _evaluate_step_answer(self, step: Dict[str, Any], answer: Any) -> float:
        """Evaluate step answer"""
        expected = step['expected_answer']
        
        if isinstance(expected, (int, float)) and isinstance(answer, (int, float)):
            error = abs(answer - expected) / max(abs(expected), 1)
            return max(0, 1 - error)
        elif isinstance(expected, str) and isinstance(answer, str):
            return 1.0 if answer.lower().strip() == expected.lower().strip() else 0.0
        elif isinstance(expected, list) and answer in expected:
            return 1.0
        else:
            return 0.0
    
    def is_complete(self) -> bool:
        """Check if challenge is complete"""
        return self.current_step >= len(self.steps)
    
    def calculate_final_score(self) -> float:
        """Calculate final score for the challenge"""
        if not self.steps:
            return 0.0
        
        total_score = sum(step['score'] for step in self.steps)
        self.score = total_score / len(self.steps)
        return self.score


class PortfolioOptimizationChallenge(InteractiveChallenge):
    """Portfolio optimization interactive challenge"""
    
    def __init__(self, risk: Risk, portfolio_data: Dict[str, Any]):
        super().__init__("portfolio_optimization", risk)
        self.portfolio_data = portfolio_data
        self._setup_challenge()
    
    def _setup_challenge(self):
        """Setup portfolio optimization steps"""
        # Step 1: Analyze current allocation
        current_allocation = self.portfolio_data.get('allocation', {})
        self.add_step(
            f"현재 포트폴리오 구성을 분석하세요: {current_allocation}\n가장 큰 리스크는 무엇입니까?",
            self._identify_main_risk(current_allocation),
            ["집중도를 확인해보세요", "상관관계를 고려하세요"]
        )
        
        # Step 2: Calculate risk metrics
        portfolio_value = self.portfolio_data.get('total_value', 100000)
        volatility = self.portfolio_data.get('volatility', 0.15)
        var_95 = portfolio_value * volatility * 1.645
        
        self.add_step(
            f"포트폴리오 VaR(95%)을 계산하세요.\n포트폴리오 가치: ${portfolio_value:,.0f}\n변동성: {volatility:.1%}",
            round(var_95, -2),  # Round to nearest 100
            ["VaR = 가치 × 변동성 × Z-score", "95% 신뢰구간: Z = 1.645"]
        )
        
        # Step 3: Suggest rebalancing
        self.add_step(
            "리스크를 줄이기 위한 리밸런싱 방안을 제시하세요.",
            "diversify",
            ["분산투자를 고려하세요", "상관관계가 낮은 자산을 추가하세요"]
        )
    
    def _identify_main_risk(self, allocation: Dict[str, float]) -> str:
        """Identify main risk in portfolio allocation"""
        if not allocation:
            return "concentration"
        
        max_allocation = max(allocation.values())
        if max_allocation > 0.5:
            return "concentration"
        
        stock_allocation = allocation.get('stocks', 0) + allocation.get('etf', 0)
        if stock_allocation > 0.8:
            return "market_risk"
        
        return "correlation"


class BehavioralBiasChallenge(InteractiveChallenge):
    """Behavioral bias awareness challenge"""
    
    def __init__(self, risk: Risk, bias_type: str = None):
        super().__init__("behavioral_bias", risk)
        self.bias_type = bias_type or self._select_random_bias()
        self._setup_challenge()
    
    def _select_random_bias(self) -> str:
        """Select random bias type"""
        biases = [
            "confirmation_bias",
            "loss_aversion", 
            "anchoring",
            "overconfidence",
            "herding",
            "recency_bias"
        ]
        return random.choice(biases)
    
    def _setup_challenge(self):
        """Setup behavioral bias challenge steps"""
        if self.bias_type == "confirmation_bias":
            self._setup_confirmation_bias_challenge()
        elif self.bias_type == "loss_aversion":
            self._setup_loss_aversion_challenge()
        elif self.bias_type == "anchoring":
            self._setup_anchoring_challenge()
        # Add more bias types as needed
    
    def _setup_confirmation_bias_challenge(self):
        """Setup confirmation bias challenge"""
        self.add_step(
            "당신이 보유한 주식에 대한 부정적 뉴스를 접했습니다. 어떻게 반응하시겠습니까?",
            "investigate_objectively",
            [
                "감정적 반응을 피하세요",
                "객관적 분석이 중요합니다",
                "반대 의견도 고려하세요"
            ]
        )
        
        self.add_step(
            "확증편향을 피하기 위한 구체적인 방법을 제시하세요.",
            "seek_contrary_evidence",
            [
                "반대되는 정보를 적극적으로 찾으세요",
                "체크리스트를 활용하세요",
                "타인의 의견을 구하세요"
            ]
        )
    
    def _setup_loss_aversion_challenge(self):
        """Setup loss aversion challenge"""
        self.add_step(
            "10% 손실과 10% 이익 중 어느 것이 더 강하게 느껴지나요?",
            "loss_stronger",
            [
                "일반적으로 손실이 2배 더 강하게 느껴집니다",
                "이는 진화적 생존 본능입니다",
                "투자에서는 객관적 판단이 필요합니다"
            ]
        )
        
        self.add_step(
            "손실회피 편향을 극복하기 위한 방법은?",
            "systematic_approach",
            [
                "미리 정한 룰을 따르세요",
                "손익을 % 단위로 생각하세요",
                "장기적 관점을 유지하세요"
            ]
        )
    
    def _setup_anchoring_challenge(self):
        """Setup anchoring challenge"""
        anchor_price = random.uniform(50, 150)
        current_price = anchor_price * random.uniform(0.8, 1.2)
        
        self.add_step(
            f"주식을 ${anchor_price:.2f}에 매수했습니다. 현재가는 ${current_price:.2f}입니다. 매수가가 투자 판단에 영향을 주어야 할까요?",
            "no",
            [
                "과거 가격은 현재 가치와 무관합니다",
                "펀더멘털에 집중하세요",
                "미래 전망이 더 중요합니다"
            ]
        )


class RealTimeMarketChallenge:
    """Real-time market event challenge"""
    
    def __init__(self, market_data: Dict[str, Any]):
        self.market_data = market_data
        self.challenge_start = datetime.now()
        self.time_limit = timedelta(minutes=5)
        self.events = []
        
    def generate_event_challenge(self) -> UnlockChallenge:
        """Generate challenge based on real market events"""
        current_vix = self.market_data.get('vix', 20)
        market_change = self.market_data.get('market_change', 0)
        
        if current_vix > 30:
            return self._create_high_volatility_challenge(current_vix)
        elif abs(market_change) > 0.02:
            return self._create_market_movement_challenge(market_change)
        else:
            return self._create_normal_market_challenge()
    
    def _create_high_volatility_challenge(self, vix: float) -> UnlockChallenge:
        """Create challenge for high volatility environment"""
        return UnlockChallenge(
            challenge_type="real_time_volatility",
            description=f"실시간 시장 상황: VIX {vix:.1f}, 높은 변동성 환경\n이런 상황에서의 최적 전략은?",
            difficulty=min(1.0, vix / 40),
            time_limit=300,
            hints=[
                "변동성이 높을 때는 조심스럽게 접근하세요",
                "헤징 전략을 고려하세요",
                "기회를 찾되 리스크 관리를 우선하세요"
            ],
            correct_answer="hedge_and_wait"
        )
    
    def _create_market_movement_challenge(self, change: float) -> UnlockChallenge:
        """Create challenge for significant market movement"""
        direction = "상승" if change > 0 else "하락"
        
        return UnlockChallenge(
            challenge_type="real_time_movement",
            description=f"실시간 시장 상황: 시장이 {abs(change):.1%} {direction}\n이 움직임이 지속될 가능성과 대응 방안은?",
            difficulty=min(1.0, abs(change) * 10),
            time_limit=240,
            hints=[
                "추세의 지속성을 판단하세요",
                "거래량을 확인하세요",
                "뉴스와 펀더멘털을 고려하세요"
            ],
            correct_answer={
                "trend_continuation": random.choice([True, False]),
                "action": "cautious_positioning"
            }
        )
    
    def _create_normal_market_challenge(self) -> UnlockChallenge:
        """Create challenge for normal market conditions"""
        return UnlockChallenge(
            challenge_type="normal_market_strategy",
            description="평온한 시장 상황입니다. 이런 환경에서의 최적 전략은?",
            difficulty=0.3,
            time_limit=180,
            hints=[
                "지루한 시장도 기회입니다",
                "포트폴리오 점검 시간입니다",
                "다음 변화를 준비하세요"
            ],
            correct_answer="portfolio_optimization"
        )
    
    def is_expired(self) -> bool:
        """Check if challenge has expired"""
        return datetime.now() - self.challenge_start > self.time_limit


class AdaptiveChallengeGenerator:
    """Generates challenges that adapt to player skill level"""
    
    def __init__(self):
        self.player_performance_history = {}
        
    def generate_adaptive_challenge(
        self, 
        player: Player, 
        risk: Risk, 
        performance_history: List[float]
    ) -> UnlockChallenge:
        """Generate challenge adapted to player skill level"""
        
        # Calculate player skill level
        avg_performance = sum(performance_history) / len(performance_history) if performance_history else 0.5
        skill_level = min(1.0, max(0.1, avg_performance))
        
        # Adjust challenge difficulty
        base_difficulty = risk.complexity
        adjusted_difficulty = base_difficulty * (0.5 + skill_level * 0.5)
        
        # Select challenge type based on player strengths/weaknesses
        challenge_type = self._select_challenge_type_for_player(player, performance_history)
        
        # Generate appropriate challenge
        if challenge_type == "calculation_focused":
            return self._generate_calculation_challenge(adjusted_difficulty)
        elif challenge_type == "pattern_focused":
            return self._generate_pattern_challenge(adjusted_difficulty)
        elif challenge_type == "behavioral_focused":
            return self._generate_behavioral_challenge(adjusted_difficulty)
        else:
            return self._generate_mixed_challenge(adjusted_difficulty)
    
    def _select_challenge_type_for_player(
        self, 
        player: Player, 
        performance_history: List[float]
    ) -> str:
        """Select challenge type based on player characteristics"""
        
        # Simple logic - can be made more sophisticated
        if player.stats.level < 10:
            return "calculation_focused"  # Start with basics
        elif player.stats.level < 25:
            return "pattern_focused"      # Move to pattern recognition
        else:
            return "behavioral_focused"   # Advanced behavioral concepts
    
    def _generate_calculation_challenge(self, difficulty: float) -> UnlockChallenge:
        """Generate calculation-focused challenge"""
        # Implementation similar to existing calculation challenges
        # but with adjusted difficulty
        pass
    
    def _generate_pattern_challenge(self, difficulty: float) -> UnlockChallenge:
        """Generate pattern recognition challenge"""
        # Implementation for pattern challenges
        pass
    
    def _generate_behavioral_challenge(self, difficulty: float) -> UnlockChallenge:
        """Generate behavioral bias challenge"""
        # Implementation for behavioral challenges
        pass
    
    def _generate_mixed_challenge(self, difficulty: float) -> UnlockChallenge:
        """Generate mixed challenge combining multiple aspects"""
        # Implementation for comprehensive challenges
        pass