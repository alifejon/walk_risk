"""Hypothesis System - 가설 수립 및 검증 시스템"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import random


class HypothesisType(Enum):
    BULLISH = "bullish"          # 상승 예상
    BEARISH = "bearish"          # 하락 예상
    NEUTRAL = "neutral"          # 중립/관망
    CONTRARIAN = "contrarian"    # 역발상


class ActionType(Enum):
    BUY = "buy"                  # 매수
    SELL = "sell"                # 매도
    HOLD = "hold"                # 보유
    WAIT = "wait"                # 관망
    SHORT = "short"              # 공매도


@dataclass
class Hypothesis:
    """플레이어가 세우는 가설"""

    hypothesis_id: str
    puzzle_id: str

    # 가설 내용
    statement: str                   # "삼성전자는 일시적 과매도 상태다"
    reasoning: str = ""              # "업종 전체 조정 + 펀더멘털 양호"
    hypothesis_type: HypothesisType = HypothesisType.NEUTRAL

    # 근거
    supporting_clues: List[str] = field(default_factory=list)      # 지지하는 단서 ID들
    contradicting_clues: List[str] = field(default_factory=list)   # 반대되는 단서 ID들
    confidence_level: float = 0.5          # 확신도 (0.0 ~ 1.0)

    # 예측
    predicted_outcome: str = ""           # "1주 내 5% 상승"
    time_horizon: int = 7                 # 예측 기간 (일)

    # 행동 계획
    recommended_action: ActionType = ActionType.HOLD
    position_size: float = 0.0            # 포지션 크기 (%)
    stop_loss: Optional[float] = None     # 손절 라인
    take_profit: Optional[float] = None   # 익절 라인

    # 메타데이터
    player_id: Optional[str] = None
    submission_time: datetime = field(default_factory=datetime.now)

    # 결과
    is_validated: bool = False
    actual_outcome: Optional[str] = None
    accuracy_score: Optional[float] = None
    validation_time: Optional[datetime] = None
    
    def calculate_risk_reward_ratio(self) -> float:
        """리스크 대비 수익 비율 계산"""
        if not (self.stop_loss and self.take_profit):
            return 0.0
        
        risk = abs(self.stop_loss)
        reward = self.take_profit
        
        if risk == 0:
            return float('inf')
        
        return reward / risk


class HypothesisValidator:
    """가설 검증 시스템"""
    
    def __init__(self):
        self.validation_history: List[Dict] = []
        self.market_scenarios = self._load_market_scenarios()
    
    def _load_market_scenarios(self) -> Dict:
        """시장 시나리오 데이터 로드"""
        return {
            "과매도_반등": {
                "conditions": ["RSI < 30", "업종 동반 하락", "펀더멘털 양호"],
                "outcome_probabilities": {
                    "strong_bounce": 0.3,    # 강한 반등
                    "mild_bounce": 0.5,      # 약한 반등
                    "continued_decline": 0.2  # 추가 하락
                }
            },
            "모멘텀_지속": {
                "conditions": ["상승 추세", "거래량 증가", "긍정적 뉴스"],
                "outcome_probabilities": {
                    "continued_rise": 0.6,
                    "consolidation": 0.3,
                    "reversal": 0.1
                }
            },
            "횡보_돌파": {
                "conditions": ["박스권 상단", "거래량 급증", "시장 강세"],
                "outcome_probabilities": {
                    "breakout": 0.4,
                    "false_breakout": 0.3,
                    "continued_range": 0.3
                }
            }
        }
    
    def validate_hypothesis(self,
                           hypothesis: Hypothesis,
                           market_data: Dict,
                           discovered_clues: List) -> Tuple[bool, float, str]:
        """가설 검증"""
        
        # 1. 논리적 일관성 검증
        logic_score = self._check_logical_consistency(hypothesis, discovered_clues)
        
        # 2. 시장 데이터와 대조
        market_alignment = self._check_market_alignment(hypothesis, market_data)
        
        # 3. 시나리오 매칭
        scenario_match = self._match_scenario(hypothesis, discovered_clues)
        
        # 4. 시뮬레이션 실행
        simulation_result = self._run_simulation(
            hypothesis,
            market_data,
            scenario_match
        )
        
        # 5. 최종 점수 계산
        accuracy_score = (
            logic_score * 0.3 +
            market_alignment * 0.3 +
            simulation_result['accuracy'] * 0.4
        )
        
        # 6. 피드백 생성
        feedback = self._generate_validation_feedback(
            hypothesis,
            accuracy_score,
            simulation_result
        )
        
        # 기록 저장
        self.validation_history.append({
            'timestamp': datetime.now(),
            'hypothesis_id': hypothesis.hypothesis_id,
            'accuracy_score': accuracy_score,
            'outcome': simulation_result['outcome']
        })
        
        # 가설 업데이트
        hypothesis.is_validated = True
        hypothesis.accuracy_score = accuracy_score
        hypothesis.actual_outcome = simulation_result['outcome']
        hypothesis.validation_time = datetime.now()
        
        success = accuracy_score >= 0.6
        
        return success, accuracy_score, feedback
    
    def _check_logical_consistency(self,
                                  hypothesis: Hypothesis,
                                  discovered_clues: List) -> float:
        """논리적 일관성 확인"""
        score = 0.5  # 기본 점수
        
        # 지지 단서가 많을수록 가점
        support_ratio = len(hypothesis.supporting_clues) / max(len(discovered_clues), 1)
        score += support_ratio * 0.3
        
        # 모순 단서가 많을수록 감점
        contradict_ratio = len(hypothesis.contradicting_clues) / max(len(discovered_clues), 1)
        score -= contradict_ratio * 0.2
        
        # 확신도와 증거의 균형
        evidence_strength = len(hypothesis.supporting_clues) / 10  # 최대 10개 가정
        if abs(hypothesis.confidence_level - evidence_strength) < 0.2:
            score += 0.2  # 확신도와 증거가 일치하면 가점
        
        return max(0.0, min(1.0, score))
    
    def _check_market_alignment(self,
                               hypothesis: Hypothesis,
                               market_data: Dict) -> float:
        """시장 데이터와의 정합성 확인"""
        score = 0.5
        
        market_sentiment = market_data.get('sentiment', 'neutral')
        current_trend = market_data.get('trend', 'sideways')
        
        # 가설과 시장 심리 일치도
        alignment_matrix = {
            (HypothesisType.BULLISH, 'bullish'): 0.8,
            (HypothesisType.BULLISH, 'neutral'): 0.5,
            (HypothesisType.BULLISH, 'bearish'): 0.2,
            (HypothesisType.BEARISH, 'bearish'): 0.8,
            (HypothesisType.BEARISH, 'neutral'): 0.5,
            (HypothesisType.BEARISH, 'bullish'): 0.2,
            (HypothesisType.NEUTRAL, 'neutral'): 0.8,
            (HypothesisType.CONTRARIAN, 'bearish'): 0.7,  # 역발상
            (HypothesisType.CONTRARIAN, 'bullish'): 0.7,
        }
        
        key = (hypothesis.hypothesis_type, market_sentiment)
        score = alignment_matrix.get(key, 0.5)
        
        # 리스크/보상 비율 고려
        rr_ratio = hypothesis.calculate_risk_reward_ratio()
        if rr_ratio >= 2.0:
            score += 0.1  # 좋은 리스크/보상 비율
        elif rr_ratio < 1.0:
            score -= 0.1  # 나쁜 리스크/보상 비율
        
        return max(0.0, min(1.0, score))
    
    def _match_scenario(self,
                       hypothesis: Hypothesis,
                       discovered_clues: List) -> Optional[str]:
        """가설과 매칭되는 시나리오 찾기"""
        best_match = None
        best_score = 0.0
        
        clue_contents = [clue.content.lower() for clue in discovered_clues]
        
        for scenario_name, scenario_data in self.market_scenarios.items():
            match_score = 0.0
            conditions = scenario_data['conditions']
            
            for condition in conditions:
                if any(condition.lower() in content for content in clue_contents):
                    match_score += 1.0 / len(conditions)
            
            if match_score > best_score:
                best_score = match_score
                best_match = scenario_name
        
        return best_match if best_score > 0.5 else None
    
    def _run_simulation(self,
                       hypothesis: Hypothesis,
                       market_data: Dict,
                       scenario: Optional[str]) -> Dict:
        """시뮬레이션 실행"""
        
        if scenario and scenario in self.market_scenarios:
            # 시나리오 기반 시뮬레이션
            probabilities = self.market_scenarios[scenario]['outcome_probabilities']
            
            # 확률적 결과 선택
            rand = random.random()
            cumulative = 0.0
            outcome = None
            
            for outcome_type, prob in probabilities.items():
                cumulative += prob
                if rand <= cumulative:
                    outcome = outcome_type
                    break
        else:
            # 기본 시뮬레이션
            if hypothesis.hypothesis_type == HypothesisType.BULLISH:
                outcomes = ['rise', 'flat', 'fall']
                weights = [0.5, 0.3, 0.2]
            elif hypothesis.hypothesis_type == HypothesisType.BEARISH:
                outcomes = ['fall', 'flat', 'rise']
                weights = [0.5, 0.3, 0.2]
            else:
                outcomes = ['flat', 'rise', 'fall']
                weights = [0.5, 0.25, 0.25]
            
            outcome = random.choices(outcomes, weights=weights)[0]
        
        # 결과 평가
        accuracy = self._evaluate_outcome(hypothesis, outcome)
        
        return {
            'outcome': outcome,
            'accuracy': accuracy,
            'scenario_used': scenario
        }
    
    def _evaluate_outcome(self, hypothesis: Hypothesis, outcome: str) -> float:
        """결과 평가"""
        outcome_map = {
            'rise': HypothesisType.BULLISH,
            'strong_bounce': HypothesisType.BULLISH,
            'mild_bounce': HypothesisType.BULLISH,
            'continued_rise': HypothesisType.BULLISH,
            'breakout': HypothesisType.BULLISH,
            
            'fall': HypothesisType.BEARISH,
            'continued_decline': HypothesisType.BEARISH,
            'reversal': HypothesisType.BEARISH,
            
            'flat': HypothesisType.NEUTRAL,
            'consolidation': HypothesisType.NEUTRAL,
            'continued_range': HypothesisType.NEUTRAL,
            'false_breakout': HypothesisType.NEUTRAL
        }
        
        expected_type = outcome_map.get(outcome, HypothesisType.NEUTRAL)
        
        if hypothesis.hypothesis_type == expected_type:
            return 1.0  # 완전 일치
        elif hypothesis.hypothesis_type == HypothesisType.CONTRARIAN:
            # 역발상은 다르게 평가
            if expected_type != HypothesisType.NEUTRAL:
                return 0.7
        elif expected_type == HypothesisType.NEUTRAL:
            return 0.5  # 부분 일치
        else:
            return 0.2  # 불일치
    
    def _generate_validation_feedback(self,
                                     hypothesis: Hypothesis,
                                     accuracy_score: float,
                                     simulation_result: Dict) -> str:
        """검증 피드백 생성"""
        
        outcome_descriptions = {
            'rise': "주가가 상승했습니다",
            'fall': "주가가 하락했습니다",
            'flat': "주가가 횡보했습니다",
            'strong_bounce': "강한 반등이 일어났습니다",
            'mild_bounce': "약한 반등이 있었습니다",
            'continued_decline': "추가 하락이 발생했습니다",
            'continued_rise': "상승세가 지속되었습니다",
            'consolidation': "조정 국면에 진입했습니다",
            'reversal': "추세가 반전되었습니다",
            'breakout': "박스권을 돌파했습니다",
            'false_breakout': "가짜 돌파였습니다",
            'continued_range': "박스권이 유지되었습니다"
        }
        
        outcome_desc = outcome_descriptions.get(
            simulation_result['outcome'],
            "예상치 못한 움직임이 있었습니다"
        )
        
        if accuracy_score >= 0.8:
            grade = "🏆 탁월한"
            comment = "시장을 정확히 읽었습니다!"
        elif accuracy_score >= 0.6:
            grade = "✅ 좋은"
            comment = "올바른 방향을 잡았습니다."
        elif accuracy_score >= 0.4:
            grade = "🤔 보통의"
            comment = "부분적으로 맞았습니다."
        else:
            grade = "❌ 아쉬운"
            comment = "이번엔 빗나갔지만 좋은 경험이었습니다."
        
        feedback = f"""
📊 가설 검증 결과

{grade} 분석이었습니다! (정확도: {accuracy_score:.1%})

📈 시장 결과: {outcome_desc}
💭 당신의 예측: {hypothesis.predicted_outcome}

{comment}

💡 교훈:
"""
        
        # 교훈 추가
        if accuracy_score >= 0.6:
            if hypothesis.supporting_clues:
                feedback += "• 단서를 잘 활용했습니다\n"
            if hypothesis.calculate_risk_reward_ratio() >= 2.0:
                feedback += "• 리스크 관리가 훌륭했습니다\n"
        else:
            if len(hypothesis.supporting_clues) < 3:
                feedback += "• 더 많은 단서를 수집해보세요\n"
            if hypothesis.confidence_level > 0.8 and accuracy_score < 0.4:
                feedback += "• 과신을 경계하세요\n"
            feedback += "• 시장의 다른 가능성도 고려해보세요\n"
        
        return feedback.strip()


@dataclass
class HypothesisValidationResult:
    """Hypothesis validation output for service layer"""

    is_correct: bool
    accuracy_score: float
    feedback: str
    correct_aspects: List[str] = field(default_factory=list)
    missed_aspects: List[str] = field(default_factory=list)


class HypothesisEngine:
    """서비스 레이어용 가설 엔진 래퍼"""

    def __init__(self):
        self.validator = HypothesisValidator()

    async def validate_hypothesis(
        self,
        hypothesis: Hypothesis,
        puzzle,
        discovered_clues: List
    ) -> HypothesisValidationResult:
        success, accuracy, feedback = self.validator.validate_hypothesis(
            hypothesis,
            puzzle.event_data,
            discovered_clues
        )

        correct_aspects: List[str] = []
        missed_aspects: List[str] = []

        if accuracy >= 0.6:
            correct_aspects.append("핵심 요인을 정확히 파악했습니다")
        else:
            missed_aspects.append("추가 단서를 수집하면 정확도가 높아집니다")

        if hypothesis.supporting_clues:
            correct_aspects.append("단서를 활용하여 가설을 뒷받침했습니다")
        else:
            missed_aspects.append("가설을 뒷받침할 단서가 부족합니다")

        return HypothesisValidationResult(
            is_correct=success,
            accuracy_score=accuracy,
            feedback=feedback,
            correct_aspects=correct_aspects,
            missed_aspects=missed_aspects
        )
