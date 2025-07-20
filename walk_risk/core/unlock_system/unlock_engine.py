"""
Risk unlock engine - Core mechanism for unlocking risks
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...models.risk.base import Risk, RiskLevel, RiskKey, RiskCategory
from ...models.player.base import Player
from ...utils.logger import logger


class UnlockAttemptResult(Enum):
    """Results of unlock attempts"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    CRITICAL_SUCCESS = "critical_success"
    CRITICAL_FAILURE = "critical_failure"


class UnlockMethod(Enum):
    """Methods for unlocking risks"""
    ANALYSIS = "analysis"          # 분석을 통한 언락
    EXPERIENCE = "experience"      # 경험을 통한 언락
    INTUITION = "intuition"        # 직감을 통한 언락
    COLLABORATION = "collaboration" # 협력을 통한 언락
    SIMULATION = "simulation"      # 시뮬레이션을 통한 언락


@dataclass
class UnlockChallenge:
    """Individual unlock challenge"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    challenge_type: str = ""
    description: str = ""
    required_keys: List[str] = field(default_factory=list)
    difficulty: float = 0.5  # 0-1 scale
    time_limit: Optional[int] = None  # seconds
    hints: List[str] = field(default_factory=list)
    correct_answer: Any = None
    player_answer: Any = None
    completed: bool = False
    score: float = 0.0


@dataclass
class UnlockAttempt:
    """Record of an unlock attempt"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    player_id: str = ""
    risk_id: str = ""
    method: UnlockMethod = UnlockMethod.ANALYSIS
    keys_used: List[RiskKey] = field(default_factory=list)
    challenges: List[UnlockChallenge] = field(default_factory=list)
    
    # Results
    result: UnlockAttemptResult = UnlockAttemptResult.FAILURE
    success_rate: float = 0.0
    experience_gained: int = 0
    new_keys_earned: List[RiskKey] = field(default_factory=list)
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    
    # Feedback
    feedback: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    
    def complete_attempt(self, result: UnlockAttemptResult) -> None:
        """Complete the unlock attempt"""
        self.end_time = datetime.now()
        self.duration = self.end_time - self.start_time
        self.result = result
        
        # Calculate overall success rate
        if self.challenges:
            self.success_rate = sum(c.score for c in self.challenges) / len(self.challenges)
        
        # Generate feedback based on result
        self._generate_feedback()
    
    def _generate_feedback(self) -> None:
        """Generate feedback based on performance"""
        if self.result == UnlockAttemptResult.CRITICAL_SUCCESS:
            self.feedback = "완벽한 분석! 리스크의 본질을 완전히 이해했습니다."
        elif self.result == UnlockAttemptResult.SUCCESS:
            self.feedback = "훌륭한 성과입니다. 리스크를 성공적으로 언락했습니다."
        elif self.result == UnlockAttemptResult.PARTIAL_SUCCESS:
            self.feedback = "부분적으로 성공했습니다. 추가 학습이 필요합니다."
        elif self.result == UnlockAttemptResult.FAILURE:
            self.feedback = "이번에는 실패했지만, 귀중한 경험을 얻었습니다."
        elif self.result == UnlockAttemptResult.CRITICAL_FAILURE:
            self.feedback = "큰 실수가 있었습니다. 기본기부터 다시 점검해보세요."


class UnlockEngine:
    """Core engine for risk unlock mechanics"""
    
    def __init__(self):
        self.active_attempts: Dict[str, UnlockAttempt] = {}
        self.completed_attempts: List[UnlockAttempt] = []
        self.challenge_generators: Dict[str, callable] = {}
        
        # Initialize challenge generators
        self._initialize_challenge_generators()
        
        # Unlock statistics
        self.stats = {
            'total_attempts': 0,
            'successful_unlocks': 0,
            'critical_successes': 0,
            'failure_rate': 0.0,
            'average_attempt_time': 0.0
        }
    
    def _initialize_challenge_generators(self) -> None:
        """Initialize challenge generation functions"""
        self.challenge_generators = {
            'volatility_analysis': self._generate_volatility_challenge,
            'correlation_detection': self._generate_correlation_challenge,
            'pattern_recognition': self._generate_pattern_challenge,
            'risk_calculation': self._generate_calculation_challenge,
            'scenario_analysis': self._generate_scenario_challenge,
            'behavioral_bias': self._generate_bias_challenge
        }
    
    async def initiate_unlock_attempt(
        self, 
        player: Player, 
        risk: Risk, 
        method: UnlockMethod = UnlockMethod.ANALYSIS
    ) -> UnlockAttempt:
        """Initiate a new unlock attempt"""
        attempt = UnlockAttempt(
            player_id=player.id,
            risk_id=risk.id,
            method=method
        )
        
        # Generate challenges based on risk type and method
        challenges = await self._generate_challenges(risk, method, player)
        attempt.challenges = challenges
        
        # Store active attempt
        self.active_attempts[attempt.id] = attempt
        
        logger.info(f"Unlock attempt initiated: {attempt.id} for risk {risk.name}")
        return attempt
    
    async def _generate_challenges(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> List[UnlockChallenge]:
        """Generate challenges for unlock attempt"""
        challenges = []
        
        # Determine challenge types based on risk category
        challenge_types = self._get_challenge_types_for_risk(risk)
        
        # Generate 2-4 challenges based on risk complexity
        num_challenges = min(4, max(2, int(risk.complexity * 4)))
        
        for i in range(num_challenges):
            challenge_type = random.choice(challenge_types)
            
            if challenge_type in self.challenge_generators:
                challenge = await self.challenge_generators[challenge_type](risk, method, player)
                if challenge:
                    challenges.append(challenge)
        
        return challenges
    
    def _get_challenge_types_for_risk(self, risk: Risk) -> List[str]:
        """Get appropriate challenge types for risk category"""
        base_challenges = ['scenario_analysis', 'behavioral_bias']
        
        if risk.category == RiskCategory.MARKET:
            return base_challenges + ['volatility_analysis', 'correlation_detection', 'pattern_recognition']
        elif risk.category == RiskCategory.LIQUIDITY:
            return base_challenges + ['risk_calculation', 'pattern_recognition']
        elif risk.category == RiskCategory.CREDIT:
            return base_challenges + ['risk_calculation', 'scenario_analysis']
        elif risk.category == RiskCategory.OPERATIONAL:
            return base_challenges + ['scenario_analysis', 'pattern_recognition']
        else:
            return base_challenges + ['risk_calculation']
    
    async def _generate_volatility_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate volatility analysis challenge"""
        
        # Generate sample price data
        base_price = 100
        price_data = []
        for i in range(20):
            change = random.uniform(-0.05, 0.05) * (1 + risk.severity)
            base_price *= (1 + change)
            price_data.append(round(base_price, 2))
        
        # Calculate actual volatility
        returns = [(price_data[i] - price_data[i-1]) / price_data[i-1] for i in range(1, len(price_data))]
        actual_volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5
        
        challenge = UnlockChallenge(
            challenge_type="volatility_analysis",
            description=f"다음 가격 데이터의 변동성을 분석하세요:\n{price_data[:10]}...",
            difficulty=risk.complexity,
            time_limit=300,  # 5 minutes
            hints=[
                "일일 수익률을 먼저 계산해보세요",
                "표준편차를 구하면 변동성을 알 수 있습니다",
                "높은 변동성은 높은 리스크를 의미합니다"
            ],
            correct_answer=actual_volatility
        )
        
        return challenge
    
    async def _generate_correlation_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate correlation analysis challenge"""
        
        # Generate correlated data
        correlation = random.uniform(-0.8, 0.8)
        asset_a = [random.uniform(-0.05, 0.05) for _ in range(20)]
        asset_b = []
        
        for return_a in asset_a:
            correlated_return = correlation * return_a + (1 - abs(correlation)) * random.uniform(-0.05, 0.05)
            asset_b.append(correlated_return)
        
        challenge = UnlockChallenge(
            challenge_type="correlation_detection",
            description=f"두 자산의 상관관계를 분석하세요:\n자산 A: {[round(r, 3) for r in asset_a[:5]]}...\n자산 B: {[round(r, 3) for r in asset_b[:5]]}...",
            difficulty=risk.complexity,
            time_limit=240,
            hints=[
                "상관계수는 -1에서 1 사이의 값입니다",
                "양의 상관관계는 같은 방향으로 움직임을 의미합니다",
                "분산투자 효과를 고려해보세요"
            ],
            correct_answer=correlation
        )
        
        return challenge
    
    async def _generate_pattern_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate pattern recognition challenge"""
        
        patterns = [
            "상승 추세",
            "하락 추세", 
            "횡보 추세",
            "V자 반등",
            "역V자 하락",
            "헤드앤숄더",
            "더블탑",
            "더블바텀"
        ]
        
        selected_pattern = random.choice(patterns)
        
        challenge = UnlockChallenge(
            challenge_type="pattern_recognition",
            description=f"차트 패턴을 식별하세요. 다음 중 어떤 패턴이 나타나고 있습니까?\n옵션: {', '.join(patterns)}",
            difficulty=risk.complexity,
            time_limit=180,
            hints=[
                "최근 가격 움직임의 방향을 관찰하세요",
                "지지선과 저항선을 찾아보세요",
                "거래량도 함께 고려하세요"
            ],
            correct_answer=selected_pattern
        )
        
        return challenge
    
    async def _generate_calculation_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate risk calculation challenge"""
        
        # Generate portfolio data
        portfolio_value = random.uniform(50000, 200000)
        confidence_level = 0.95
        volatility = random.uniform(0.15, 0.35)
        
        # Calculate VaR
        var_95 = portfolio_value * volatility * 1.645  # Normal distribution approximation
        
        challenge = UnlockChallenge(
            challenge_type="risk_calculation",
            description=f"포트폴리오 VaR을 계산하세요:\n포트폴리오 가치: ${portfolio_value:,.0f}\n연간 변동성: {volatility:.1%}\n신뢰구간: {confidence_level:.0%}",
            difficulty=risk.complexity,
            time_limit=360,
            hints=[
                "VaR = 포트폴리오 가치 × 변동성 × Z-score",
                "95% 신뢰구간의 Z-score는 1.645입니다",
                "일반적으로 포트폴리오의 최대 예상 손실을 의미합니다"
            ],
            correct_answer=var_95
        )
        
        return challenge
    
    async def _generate_scenario_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate scenario analysis challenge"""
        
        scenarios = [
            {
                "name": "금리 상승",
                "description": "중앙은행이 금리를 2% 인상했습니다",
                "effects": ["채권 가격 하락", "주식 가치 재평가", "대출 비용 증가"],
                "correct_action": "채권 비중 축소, 금리 민감 주식 매도"
            },
            {
                "name": "경기 침체",
                "description": "GDP 성장률이 2분기 연속 마이너스를 기록했습니다",
                "effects": ["소비 감소", "기업 실적 악화", "실업률 증가"],
                "correct_action": "방어주 비중 확대, 현금 보유 증가"
            },
            {
                "name": "지정학적 위기",
                "description": "주요 경제국가 간 무역 분쟁이 격화되었습니다",
                "effects": ["글로벌 공급망 차질", "변동성 증가", "안전자산 선호"],
                "correct_action": "금, 국채 등 안전자산 확대"
            }
        ]
        
        scenario = random.choice(scenarios)
        
        challenge = UnlockChallenge(
            challenge_type="scenario_analysis",
            description=f"시나리오: {scenario['name']}\n{scenario['description']}\n\n가능한 효과들: {', '.join(scenario['effects'])}\n\n어떤 투자 전략을 취하시겠습니까?",
            difficulty=risk.complexity,
            time_limit=300,
            hints=[
                "각 자산 클래스에 미치는 영향을 고려하세요",
                "리스크 온/오프 성향을 파악하세요",
                "분산투자의 효과를 생각해보세요"
            ],
            correct_answer=scenario["correct_action"]
        )
        
        return challenge
    
    async def _generate_bias_challenge(
        self, 
        risk: Risk, 
        method: UnlockMethod, 
        player: Player
    ) -> Optional[UnlockChallenge]:
        """Generate behavioral bias challenge"""
        
        biases = [
            {
                "name": "확증편향",
                "description": "자신의 믿음을 확인해주는 정보만 찾는 경향",
                "example": "좋아하는 주식의 긍정적 뉴스만 읽는다",
                "solution": "반대 의견도 적극적으로 찾아보기"
            },
            {
                "name": "손실회피",
                "description": "같은 크기의 이익보다 손실을 더 크게 느끼는 경향", 
                "example": "10% 손실을 10% 이익보다 2배 크게 느낀다",
                "solution": "객관적인 손익 기준 설정하기"
            },
            {
                "name": "앵커링",
                "description": "처음 접한 정보에 과도하게 의존하는 경향",
                "example": "매수가격을 기준으로만 판단한다",
                "solution": "현재 펀더멘털에 집중하기"
            }
        ]
        
        bias = random.choice(biases)
        
        challenge = UnlockChallenge(
            challenge_type="behavioral_bias",
            description=f"다음 상황에서 어떤 인지편향이 작용하고 있습니까?\n\n상황: {bias['example']}\n\n이를 극복하는 방법은 무엇입니까?",
            difficulty=risk.complexity * 0.8,  # Slightly easier
            time_limit=240,
            hints=[
                "투자자의 심리적 함정을 생각해보세요",
                "객관적 분석을 방해하는 요소는 무엇인가요?",
                "체계적인 접근법이 해답일 수 있습니다"
            ],
            correct_answer={
                "bias": bias["name"],
                "solution": bias["solution"]
            }
        )
        
        return challenge
    
    async def submit_challenge_answer(
        self, 
        attempt_id: str, 
        challenge_id: str, 
        answer: Any
    ) -> bool:
        """Submit answer for a challenge"""
        attempt = self.active_attempts.get(attempt_id)
        if not attempt:
            return False
        
        # Find the challenge
        challenge = None
        for c in attempt.challenges:
            if c.id == challenge_id:
                challenge = c
                break
        
        if not challenge:
            return False
        
        # Record answer
        challenge.player_answer = answer
        
        # Evaluate answer
        score = await self._evaluate_answer(challenge)
        challenge.score = score
        challenge.completed = True
        
        logger.info(f"Challenge answer submitted: {challenge_id} (score: {score})")
        return True
    
    async def _evaluate_answer(self, challenge: UnlockChallenge) -> float:
        """Evaluate challenge answer and return score (0-1)"""
        if challenge.challenge_type == "volatility_analysis":
            if isinstance(challenge.player_answer, (int, float)):
                error = abs(challenge.player_answer - challenge.correct_answer)
                relative_error = error / challenge.correct_answer
                return max(0, 1 - relative_error * 2)  # Full score if <50% error
        
        elif challenge.challenge_type == "correlation_detection":
            if isinstance(challenge.player_answer, (int, float)):
                error = abs(challenge.player_answer - challenge.correct_answer)
                return max(0, 1 - error)  # Score based on absolute error
        
        elif challenge.challenge_type == "pattern_recognition":
            if challenge.player_answer == challenge.correct_answer:
                return 1.0
            else:
                return 0.3  # Partial credit for attempt
        
        elif challenge.challenge_type == "risk_calculation":
            if isinstance(challenge.player_answer, (int, float)):
                error = abs(challenge.player_answer - challenge.correct_answer)
                relative_error = error / challenge.correct_answer
                return max(0, 1 - relative_error)
        
        elif challenge.challenge_type in ["scenario_analysis", "behavioral_bias"]:
            # Text-based answers - simple keyword matching for now
            if isinstance(challenge.player_answer, str) and isinstance(challenge.correct_answer, str):
                answer_lower = challenge.player_answer.lower()
                correct_lower = challenge.correct_answer.lower()
                
                # Check for key concepts
                key_words = correct_lower.split()[:3]  # First 3 words
                matches = sum(1 for word in key_words if word in answer_lower)
                return matches / len(key_words)
        
        return 0.0  # Default score for unrecognized formats
    
    async def complete_unlock_attempt(self, attempt_id: str) -> UnlockAttemptResult:
        """Complete an unlock attempt and determine result"""
        attempt = self.active_attempts.get(attempt_id)
        if not attempt:
            return UnlockAttemptResult.FAILURE
        
        # Calculate overall performance
        completed_challenges = [c for c in attempt.challenges if c.completed]
        if not completed_challenges:
            result = UnlockAttemptResult.FAILURE
        else:
            avg_score = sum(c.score for c in completed_challenges) / len(completed_challenges)
            
            # Determine result based on score
            if avg_score >= 0.95:
                result = UnlockAttemptResult.CRITICAL_SUCCESS
            elif avg_score >= 0.75:
                result = UnlockAttemptResult.SUCCESS
            elif avg_score >= 0.5:
                result = UnlockAttemptResult.PARTIAL_SUCCESS
            elif avg_score >= 0.25:
                result = UnlockAttemptResult.FAILURE
            else:
                result = UnlockAttemptResult.CRITICAL_FAILURE
        
        # Complete the attempt
        attempt.complete_attempt(result)
        
        # Calculate experience and rewards
        await self._calculate_rewards(attempt)
        
        # Move to completed attempts
        self.completed_attempts.append(attempt)
        del self.active_attempts[attempt_id]
        
        # Update statistics
        self._update_statistics()
        
        logger.info(f"Unlock attempt completed: {attempt_id} with result {result.value}")
        return result
    
    async def _calculate_rewards(self, attempt: UnlockAttempt) -> None:
        """Calculate experience and key rewards for attempt"""
        base_exp = 100
        
        # Experience based on performance
        if attempt.result == UnlockAttemptResult.CRITICAL_SUCCESS:
            attempt.experience_gained = int(base_exp * 2.0)
        elif attempt.result == UnlockAttemptResult.SUCCESS:
            attempt.experience_gained = int(base_exp * 1.5)
        elif attempt.result == UnlockAttemptResult.PARTIAL_SUCCESS:
            attempt.experience_gained = int(base_exp * 1.0)
        elif attempt.result == UnlockAttemptResult.FAILURE:
            attempt.experience_gained = int(base_exp * 0.5)
        else:  # Critical failure
            attempt.experience_gained = int(base_exp * 0.2)
        
        # Generate new keys based on challenges completed
        for challenge in attempt.challenges:
            if challenge.completed and challenge.score > 0.7:
                key = RiskKey(
                    name=f"{challenge.challenge_type}_mastery",
                    key_type="experience",
                    description=f"Mastery of {challenge.challenge_type} gained through practice"
                )
                attempt.new_keys_earned.append(key)
        
        # Bonus keys for exceptional performance
        if attempt.result == UnlockAttemptResult.CRITICAL_SUCCESS:
            bonus_key = RiskKey(
                name="perfect_analysis",
                key_type="wisdom",
                description="Perfect understanding through flawless analysis"
            )
            attempt.new_keys_earned.append(bonus_key)
    
    def _update_statistics(self) -> None:
        """Update unlock engine statistics"""
        if not self.completed_attempts:
            return
        
        self.stats['total_attempts'] = len(self.completed_attempts)
        self.stats['successful_unlocks'] = len([
            a for a in self.completed_attempts 
            if a.result in [UnlockAttemptResult.SUCCESS, UnlockAttemptResult.CRITICAL_SUCCESS]
        ])
        self.stats['critical_successes'] = len([
            a for a in self.completed_attempts 
            if a.result == UnlockAttemptResult.CRITICAL_SUCCESS
        ])
        
        if self.stats['total_attempts'] > 0:
            self.stats['failure_rate'] = 1 - (self.stats['successful_unlocks'] / self.stats['total_attempts'])
        
        # Calculate average attempt time
        durations = [a.duration.total_seconds() for a in self.completed_attempts if a.duration]
        if durations:
            self.stats['average_attempt_time'] = sum(durations) / len(durations)
    
    def get_attempt_history(self, player_id: str) -> List[UnlockAttempt]:
        """Get unlock attempt history for player"""
        return [a for a in self.completed_attempts if a.player_id == player_id]
    
    def get_active_attempt(self, player_id: str) -> Optional[UnlockAttempt]:
        """Get active attempt for player"""
        for attempt in self.active_attempts.values():
            if attempt.player_id == player_id:
                return attempt
        return None
    
    def get_unlock_statistics(self) -> Dict[str, Any]:
        """Get unlock engine statistics"""
        return {
            **self.stats,
            'active_attempts': len(self.active_attempts),
            'completed_attempts': len(self.completed_attempts),
            'success_rate': self.stats['successful_unlocks'] / max(1, self.stats['total_attempts']),
            'critical_success_rate': self.stats['critical_successes'] / max(1, self.stats['total_attempts'])
        }
    
    async def provide_hint(self, attempt_id: str, challenge_id: str) -> Optional[str]:
        """Provide hint for a challenge"""
        attempt = self.active_attempts.get(attempt_id)
        if not attempt:
            return None
        
        for challenge in attempt.challenges:
            if challenge.id == challenge_id and challenge.hints:
                # Return first unused hint
                return challenge.hints[0] if challenge.hints else None
        
        return None
    
    def generate_unlock_report(self, attempt: UnlockAttempt) -> Dict[str, Any]:
        """Generate detailed report for unlock attempt"""
        return {
            'attempt_id': attempt.id,
            'result': attempt.result.value,
            'success_rate': attempt.success_rate,
            'duration': attempt.duration.total_seconds() if attempt.duration else 0,
            'experience_gained': attempt.experience_gained,
            'challenges_completed': len([c for c in attempt.challenges if c.completed]),
            'total_challenges': len(attempt.challenges),
            'new_keys_earned': len(attempt.new_keys_earned),
            'feedback': attempt.feedback,
            'lessons_learned': attempt.lessons_learned,
            'challenge_details': [
                {
                    'type': c.challenge_type,
                    'score': c.score,
                    'completed': c.completed
                }
                for c in attempt.challenges
            ]
        }