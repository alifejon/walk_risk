"""
Pattern recognition game engine for educational trading patterns
"""
import random
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid

from .chart_patterns import ChartPattern, PatternType, PatternRecognizer, ChartPatternLibrary
from .technical_indicators import TechnicalIndicator, IndicatorType, IndicatorCalculator, IndicatorLibrary
from ...utils.logger import logger


class PatternDifficulty(Enum):
    """패턴 게임 난이도"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class GameMode(Enum):
    """게임 모드"""
    PATTERN_RECOGNITION = "pattern_recognition"    # 패턴 인식하기
    PATTERN_COMPLETION = "pattern_completion"      # 패턴 완성 예측
    INDICATOR_ANALYSIS = "indicator_analysis"      # 지표 분석
    SIGNAL_TIMING = "signal_timing"                # 신호 타이밍 맞추기
    DIVERGENCE_DETECTION = "divergence_detection"  # 다이버전스 찾기
    MULTI_TIMEFRAME = "multi_timeframe"            # 멀티 타임프레임 분석
    REAL_TIME_DECISION = "real_time_decision"      # 실시간 의사결정


class ChallengeType(Enum):
    """챌린지 유형"""
    MULTIPLE_CHOICE = "multiple_choice"
    DRAG_AND_DROP = "drag_and_drop"
    DRAWING = "drawing"
    TIMING = "timing"
    PREDICTION = "prediction"
    ANALYSIS = "analysis"


@dataclass
class PatternGameResult:
    """패턴 게임 결과"""
    challenge_id: str
    player_id: str
    
    # 점수 정보
    score: float  # 0-100
    accuracy: float  # 0-1
    speed_bonus: float = 0.0
    difficulty_multiplier: float = 1.0
    
    # 상세 결과
    correct_answers: int = 0
    total_answers: int = 0
    time_taken: float = 0.0  # seconds
    
    # 학습 분석
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    
    # 보상
    experience_gained: int = 0
    badges_earned: List[str] = field(default_factory=list)
    
    # 메타데이터
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_final_score(self) -> float:
        """최종 점수 계산"""
        base_score = self.score * self.accuracy
        speed_adjusted = base_score + self.speed_bonus
        final_score = speed_adjusted * self.difficulty_multiplier
        return min(100.0, max(0.0, final_score))
    
    def get_performance_grade(self) -> str:
        """성과 등급 반환"""
        final_score = self.calculate_final_score()
        
        if final_score >= 90:
            return "S"
        elif final_score >= 80:
            return "A"
        elif final_score >= 70:
            return "B"
        elif final_score >= 60:
            return "C"
        elif final_score >= 50:
            return "D"
        else:
            return "F"
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'challenge_id': self.challenge_id,
            'player_id': self.player_id,
            'final_score': self.calculate_final_score(),
            'grade': self.get_performance_grade(),
            'accuracy': self.accuracy,
            'speed_bonus': self.speed_bonus,
            'time_taken': self.time_taken,
            'correct_answers': self.correct_answers,
            'total_answers': self.total_answers,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'improvement_suggestions': self.improvement_suggestions,
            'experience_gained': self.experience_gained,
            'badges_earned': self.badges_earned,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PatternChallenge:
    """패턴 인식 챌린지"""
    id: str
    title: str
    description: str
    
    # 게임 설정
    game_mode: GameMode
    challenge_type: ChallengeType
    difficulty: PatternDifficulty
    time_limit: Optional[int] = None  # seconds
    
    # 데이터
    chart_data: pd.DataFrame = field(default_factory=pd.DataFrame)
    patterns: List[ChartPattern] = field(default_factory=list)
    indicators: List[TechnicalIndicator] = field(default_factory=list)
    
    # 문제 설정
    questions: List[Dict[str, Any]] = field(default_factory=list)
    correct_answers: List[Any] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    
    # 학습 목표
    learning_objectives: List[str] = field(default_factory=list)
    prerequisite_knowledge: List[str] = field(default_factory=list)
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    estimated_duration: int = 300  # seconds
    
    def get_difficulty_multiplier(self) -> float:
        """난이도 배수 반환"""
        multipliers = {
            PatternDifficulty.BEGINNER: 1.0,
            PatternDifficulty.INTERMEDIATE: 1.2,
            PatternDifficulty.ADVANCED: 1.5,
            PatternDifficulty.EXPERT: 2.0
        }
        return multipliers.get(self.difficulty, 1.0)
    
    def add_question(self, question: str, correct_answer: Any, options: List[Any] = None, explanation: str = ""):
        """질문 추가"""
        self.questions.append({
            'question': question,
            'options': options or [],
            'explanation': explanation,
            'type': self.challenge_type.value
        })
        self.correct_answers.append(correct_answer)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'game_mode': self.game_mode.value,
            'challenge_type': self.challenge_type.value,
            'difficulty': self.difficulty.value,
            'time_limit': self.time_limit,
            'questions_count': len(self.questions),
            'learning_objectives': self.learning_objectives,
            'tags': self.tags,
            'estimated_duration': self.estimated_duration,
            'difficulty_multiplier': self.get_difficulty_multiplier()
        }


class PatternGameEngine:
    """패턴 인식 게임 엔진"""
    
    def __init__(self):
        self.pattern_library = ChartPatternLibrary()
        self.indicator_library = IndicatorLibrary()
        self.pattern_recognizer = PatternRecognizer(self.pattern_library)
        self.indicator_calculator = IndicatorCalculator()
        
        # 게임 상태
        self.active_challenges: Dict[str, PatternChallenge] = {}
        self.completed_results: Dict[str, PatternGameResult] = {}
        
        # 난이도 조절 시스템
        self.player_performance_history: Dict[str, List[float]] = {}
        
    def create_pattern_recognition_challenge(
        self, 
        pattern_types: List[PatternType], 
        difficulty: PatternDifficulty = PatternDifficulty.BEGINNER,
        player_id: Optional[str] = None
    ) -> PatternChallenge:
        """패턴 인식 챌린지 생성"""
        
        challenge_id = str(uuid.uuid4())
        
        # 난이도에 따른 설정 조정
        noise_level = self._get_noise_level(difficulty)
        pattern_clarity = self._get_pattern_clarity(difficulty)
        
        # 랜덤하게 패턴 선택
        selected_pattern = random.choice(pattern_types)
        
        # 합성 차트 데이터 생성
        chart_data, actual_pattern = self.pattern_recognizer.generate_synthetic_pattern(
            selected_pattern, 
            difficulty=self._difficulty_to_float(difficulty)
        )
        
        # 노이즈 추가 (난이도 증가)
        if noise_level > 0:
            chart_data = self._add_market_noise(chart_data, noise_level)
        
        # 챌린지 생성
        challenge = PatternChallenge(
            id=challenge_id,
            title=f"{selected_pattern.value} 패턴 인식 챌린지",
            description=f"{difficulty.value} 난이도의 {selected_pattern.value} 패턴을 찾고 분석하세요.",
            game_mode=GameMode.PATTERN_RECOGNITION,
            challenge_type=ChallengeType.MULTIPLE_CHOICE,
            difficulty=difficulty,
            time_limit=self._get_time_limit(difficulty),
            chart_data=chart_data,
            patterns=[actual_pattern],
            learning_objectives=[
                f"{selected_pattern.value} 패턴의 특징 이해",
                "차트에서 패턴 식별 능력 향상",
                "패턴 기반 투자 신호 해석"
            ]
        )
        
        # 질문 생성
        self._generate_pattern_questions(challenge, actual_pattern)
        
        # 활성 챌린지에 추가
        self.active_challenges[challenge_id] = challenge
        
        logger.info(f"패턴 인식 챌린지 생성: {challenge_id} ({selected_pattern.value}, {difficulty.value})")
        
        return challenge
    
    def create_indicator_analysis_challenge(
        self, 
        indicator_types: List[IndicatorType], 
        difficulty: PatternDifficulty = PatternDifficulty.BEGINNER
    ) -> PatternChallenge:
        """지표 분석 챌린지 생성"""
        
        challenge_id = str(uuid.uuid4())
        
        # 기본 가격 데이터 생성
        chart_data = self._generate_market_data(days=60, volatility=0.02)
        
        # 지표 계산
        indicators = []
        for indicator_type in indicator_types:
            indicator = self._calculate_indicator(indicator_type, chart_data)
            if indicator:
                indicators.append(indicator)
        
        challenge = PatternChallenge(
            id=challenge_id,
            title="기술적 지표 분석 챌린지",
            description=f"{len(indicator_types)}개 지표를 분석하여 투자 신호를 찾으세요.",
            game_mode=GameMode.INDICATOR_ANALYSIS,
            challenge_type=ChallengeType.MULTIPLE_CHOICE,
            difficulty=difficulty,
            time_limit=self._get_time_limit(difficulty) * 2,  # 지표 분석은 더 많은 시간 필요
            chart_data=chart_data,
            indicators=indicators,
            learning_objectives=[
                "기술적 지표 해석 능력 향상",
                "지표 신호의 신뢰성 판단",
                "복합 지표 분석 기법 습득"
            ]
        )
        
        # 지표 분석 질문 생성
        self._generate_indicator_questions(challenge, indicators)
        
        self.active_challenges[challenge_id] = challenge
        
        logger.info(f"지표 분석 챌린지 생성: {challenge_id} ({len(indicator_types)}개 지표)")
        
        return challenge
    
    def create_signal_timing_challenge(
        self, 
        difficulty: PatternDifficulty = PatternDifficulty.INTERMEDIATE
    ) -> PatternChallenge:
        """신호 타이밍 챌린지 생성"""
        
        challenge_id = str(uuid.uuid4())
        
        # 트렌드 변화가 있는 데이터 생성
        chart_data = self._generate_trending_data(days=40, trend_changes=2)
        
        # 여러 지표 계산
        indicators = []
        indicator_types = [IndicatorType.RSI, IndicatorType.MACD, IndicatorType.MOVING_AVERAGE]
        
        for indicator_type in indicator_types:
            indicator = self._calculate_indicator(indicator_type, chart_data)
            if indicator:
                indicators.append(indicator)
        
        challenge = PatternChallenge(
            id=challenge_id,
            title="매매 신호 타이밍 챌린지",
            description="최적의 매수/매도 타이밍을 찾아보세요.",
            game_mode=GameMode.SIGNAL_TIMING,
            challenge_type=ChallengeType.TIMING,
            difficulty=difficulty,
            time_limit=self._get_time_limit(difficulty) * 1.5,
            chart_data=chart_data,
            indicators=indicators,
            learning_objectives=[
                "최적 진입/청산 타이밍 판단",
                "지표 신호 조합 분석",
                "리스크 관리 타이밍 습득"
            ]
        )
        
        # 타이밍 질문 생성
        self._generate_timing_questions(challenge, chart_data, indicators)
        
        self.active_challenges[challenge_id] = challenge
        
        return challenge
    
    def create_divergence_detection_challenge(
        self, 
        difficulty: PatternDifficulty = PatternDifficulty.ADVANCED
    ) -> PatternChallenge:
        """다이버전스 탐지 챌린지 생성"""
        
        challenge_id = str(uuid.uuid4())
        
        # 다이버전스가 있는 데이터 생성
        chart_data = self._generate_divergence_data()
        
        # RSI 계산 (다이버전스 탐지용)
        rsi_indicator = self.indicator_calculator.calculate_rsi(chart_data['close'])
        
        # 다이버전스 탐지
        divergences = self.indicator_calculator.detect_divergence(
            chart_data['close'], 
            pd.Series([v.value for v in rsi_indicator.values], 
                     index=[v.timestamp for v in rsi_indicator.values])
        )
        
        challenge = PatternChallenge(
            id=challenge_id,
            title="다이버전스 탐지 챌린지",
            description="가격과 지표 간의 다이버전스를 찾아 추세 전환을 예측하세요.",
            game_mode=GameMode.DIVERGENCE_DETECTION,
            challenge_type=ChallengeType.ANALYSIS,
            difficulty=difficulty,
            time_limit=self._get_time_limit(difficulty) * 2,
            chart_data=chart_data,
            indicators=[rsi_indicator],
            learning_objectives=[
                "다이버전스 패턴 이해",
                "추세 전환 신호 탐지",
                "고급 기술적 분석 기법"
            ]
        )
        
        # 다이버전스 질문 생성
        self._generate_divergence_questions(challenge, divergences)
        
        self.active_challenges[challenge_id] = challenge
        
        return challenge
    
    def submit_challenge_answer(
        self, 
        challenge_id: str, 
        player_id: str, 
        answers: List[Any], 
        time_taken: float
    ) -> PatternGameResult:
        """챌린지 답안 제출 및 채점"""
        
        challenge = self.active_challenges.get(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge not found: {challenge_id}")
        
        # 채점
        correct_count = 0
        total_questions = len(challenge.correct_answers)
        
        for i, (submitted_answer, correct_answer) in enumerate(zip(answers, challenge.correct_answers)):
            if self._is_answer_correct(submitted_answer, correct_answer, challenge.challenge_type):
                correct_count += 1
        
        # 정확도 계산
        accuracy = correct_count / total_questions if total_questions > 0 else 0
        
        # 기본 점수 계산 (정확도 기반)
        base_score = accuracy * 100
        
        # 속도 보너스 계산
        speed_bonus = self._calculate_speed_bonus(time_taken, challenge.time_limit)
        
        # 난이도 배수
        difficulty_multiplier = challenge.get_difficulty_multiplier()
        
        # 결과 객체 생성
        result = PatternGameResult(
            challenge_id=challenge_id,
            player_id=player_id,
            score=base_score,
            accuracy=accuracy,
            speed_bonus=speed_bonus,
            difficulty_multiplier=difficulty_multiplier,
            correct_answers=correct_count,
            total_answers=total_questions,
            time_taken=time_taken
        )
        
        # 성과 분석
        self._analyze_performance(result, challenge, answers)
        
        # 경험치 및 보상 계산
        self._calculate_rewards(result, challenge)
        
        # 플레이어 성과 기록 업데이트
        self._update_player_performance(player_id, result.calculate_final_score())
        
        # 결과 저장
        self.completed_results[f"{challenge_id}_{player_id}"] = result
        
        logger.info(f"챌린지 완료: {challenge_id}, 플레이어: {player_id}, 점수: {result.calculate_final_score():.1f}")
        
        return result
    
    def get_adaptive_difficulty(self, player_id: str) -> PatternDifficulty:
        """플레이어 성과에 따른 적응형 난이도 반환"""
        
        history = self.player_performance_history.get(player_id, [])
        
        if len(history) < 3:
            return PatternDifficulty.BEGINNER
        
        recent_avg = sum(history[-5:]) / min(len(history), 5)
        
        if recent_avg >= 85:
            return PatternDifficulty.EXPERT
        elif recent_avg >= 75:
            return PatternDifficulty.ADVANCED
        elif recent_avg >= 65:
            return PatternDifficulty.INTERMEDIATE
        else:
            return PatternDifficulty.BEGINNER
    
    def get_recommended_challenges(self, player_id: str) -> List[Dict[str, Any]]:
        """플레이어 맞춤 챌린지 추천"""
        
        difficulty = self.get_adaptive_difficulty(player_id)
        
        recommendations = []
        
        # 기본 패턴 인식 챌린지
        basic_patterns = [PatternType.HEAD_AND_SHOULDERS, PatternType.DOUBLE_TOP, PatternType.ASCENDING_TRIANGLE]
        for pattern in basic_patterns:
            recommendations.append({
                'type': 'pattern_recognition',
                'pattern': pattern.value,
                'difficulty': difficulty.value,
                'estimated_duration': 300,
                'learning_value': 'high'
            })
        
        # 지표 분석 챌린지
        indicator_combinations = [
            [IndicatorType.RSI],
            [IndicatorType.MACD],
            [IndicatorType.RSI, IndicatorType.MACD],
            [IndicatorType.BOLLINGER_BANDS, IndicatorType.RSI]
        ]
        
        for indicators in indicator_combinations:
            recommendations.append({
                'type': 'indicator_analysis',
                'indicators': [ind.value for ind in indicators],
                'difficulty': difficulty.value,
                'estimated_duration': 400,
                'learning_value': 'medium'
            })
        
        # 고급 챌린지 (성과가 좋은 플레이어만)
        if difficulty in [PatternDifficulty.ADVANCED, PatternDifficulty.EXPERT]:
            recommendations.extend([
                {
                    'type': 'divergence_detection',
                    'difficulty': difficulty.value,
                    'estimated_duration': 600,
                    'learning_value': 'very_high'
                },
                {
                    'type': 'signal_timing',
                    'difficulty': difficulty.value,
                    'estimated_duration': 450,
                    'learning_value': 'high'
                }
            ])
        
        return recommendations
    
    # Helper methods
    
    def _get_noise_level(self, difficulty: PatternDifficulty) -> float:
        """난이도별 노이즈 레벨"""
        levels = {
            PatternDifficulty.BEGINNER: 0.01,
            PatternDifficulty.INTERMEDIATE: 0.02,
            PatternDifficulty.ADVANCED: 0.03,
            PatternDifficulty.EXPERT: 0.04
        }
        return levels.get(difficulty, 0.02)
    
    def _get_pattern_clarity(self, difficulty: PatternDifficulty) -> float:
        """난이도별 패턴 명확도"""
        clarity = {
            PatternDifficulty.BEGINNER: 0.9,
            PatternDifficulty.INTERMEDIATE: 0.7,
            PatternDifficulty.ADVANCED: 0.5,
            PatternDifficulty.EXPERT: 0.3
        }
        return clarity.get(difficulty, 0.7)
    
    def _get_time_limit(self, difficulty: PatternDifficulty) -> int:
        """난이도별 제한 시간 (초)"""
        times = {
            PatternDifficulty.BEGINNER: 600,      # 10분
            PatternDifficulty.INTERMEDIATE: 480,  # 8분
            PatternDifficulty.ADVANCED: 360,      # 6분
            PatternDifficulty.EXPERT: 300         # 5분
        }
        return times.get(difficulty, 480)
    
    def _difficulty_to_float(self, difficulty: PatternDifficulty) -> float:
        """난이도를 float 값으로 변환"""
        mapping = {
            PatternDifficulty.BEGINNER: 0.2,
            PatternDifficulty.INTERMEDIATE: 0.5,
            PatternDifficulty.ADVANCED: 0.7,
            PatternDifficulty.EXPERT: 0.9
        }
        return mapping.get(difficulty, 0.5)
    
    def _add_market_noise(self, data: pd.DataFrame, noise_level: float) -> pd.DataFrame:
        """시장 노이즈 추가"""
        noisy_data = data.copy()
        
        for col in ['open', 'high', 'low', 'close']:
            if col in noisy_data.columns:
                noise = np.random.normal(0, noise_level, len(noisy_data))
                noisy_data[col] *= (1 + noise)
        
        return noisy_data
    
    def _generate_market_data(self, days: int = 60, volatility: float = 0.02, base_price: float = 100) -> pd.DataFrame:
        """기본 시장 데이터 생성"""
        
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        
        # 랜덤 워크 기반 가격 생성
        returns = np.random.normal(0, volatility, days)
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # OHLC 데이터 생성
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            open_price = prices[i-1] if i > 0 else close
            high = close * random.uniform(1.001, 1.02)
            low = close * random.uniform(0.98, 0.999)
            volume = random.randint(100000, 1000000)
            
            data.append({
                'open': open_price,
                'high': max(high, open_price, close),
                'low': min(low, open_price, close),
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data, index=dates)
    
    def _generate_trending_data(self, days: int = 40, trend_changes: int = 2) -> pd.DataFrame:
        """트렌드 변화가 있는 데이터 생성"""
        
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        
        # 트렌드 구간 나누기
        segment_length = days // (trend_changes + 1)
        trends = [random.choice([0.001, -0.001, 0.002, -0.002]) for _ in range(trend_changes + 1)]
        
        prices = [100]  # 시작 가격
        
        for day in range(1, days):
            segment = day // segment_length
            if segment >= len(trends):
                segment = len(trends) - 1
            
            trend = trends[segment]
            noise = random.uniform(-0.02, 0.02)
            
            new_price = prices[-1] * (1 + trend + noise)
            prices.append(new_price)
        
        # OHLC 데이터 생성
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            open_price = prices[i-1] if i > 0 else close
            high = close * random.uniform(1.001, 1.015)
            low = close * random.uniform(0.985, 0.999)
            volume = random.randint(100000, 1000000)
            
            data.append({
                'open': open_price,
                'high': max(high, open_price, close),
                'low': min(low, open_price, close),
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data, index=dates)
    
    def _generate_divergence_data(self) -> pd.DataFrame:
        """다이버전스가 있는 데이터 생성"""
        
        days = 50
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        
        # 가격은 상승하지만 모멘텀은 약화되는 패턴
        base_prices = []
        momentum_strength = []
        
        for i in range(days):
            # 가격 추세 (전체적으로 상승)
            base_trend = 0.002
            cycle_effect = 0.01 * np.sin(i * 2 * np.pi / 15)  # 15일 주기
            
            if i == 0:
                price = 100
            else:
                price_change = base_trend + cycle_effect + random.uniform(-0.01, 0.01)
                price = base_prices[-1] * (1 + price_change)
            
            base_prices.append(price)
            
            # 모멘텀 강도 (점차 약화 - 다이버전스 발생)
            momentum = 1.0 - (i / days) * 0.8 + random.uniform(-0.1, 0.1)
            momentum_strength.append(max(0.2, momentum))
        
        # OHLC 데이터 생성
        data = []
        for i, (date, close) in enumerate(zip(dates, base_prices)):
            open_price = base_prices[i-1] if i > 0 else close
            
            # 모멘텀 강도에 따라 변동성 조절
            volatility = 0.01 * momentum_strength[i]
            high = close * (1 + random.uniform(0.001, volatility))
            low = close * (1 - random.uniform(0.001, volatility))
            volume = random.randint(100000, 1000000)
            
            data.append({
                'open': open_price,
                'high': max(high, open_price, close),
                'low': min(low, open_price, close),
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data, index=dates)
    
    def _calculate_indicator(self, indicator_type: IndicatorType, data: pd.DataFrame) -> Optional[TechnicalIndicator]:
        """지표 계산"""
        
        try:
            if indicator_type == IndicatorType.RSI:
                return self.indicator_calculator.calculate_rsi(data['close'])
            elif indicator_type == IndicatorType.MACD:
                return self.indicator_calculator.calculate_macd(data['close'])
            elif indicator_type == IndicatorType.BOLLINGER_BANDS:
                return self.indicator_calculator.calculate_bollinger_bands(data['close'])
            elif indicator_type == IndicatorType.MOVING_AVERAGE:
                return self.indicator_calculator.calculate_moving_average(data['close'])
            elif indicator_type == IndicatorType.STOCHASTIC:
                return self.indicator_calculator.calculate_stochastic(data['high'], data['low'], data['close'])
            elif indicator_type == IndicatorType.ATR:
                return self.indicator_calculator.calculate_atr(data['high'], data['low'], data['close'])
            
        except Exception as e:
            logger.error(f"지표 계산 실패 ({indicator_type.value}): {e}")
            return None
        
        return None
    
    def _generate_pattern_questions(self, challenge: PatternChallenge, pattern: ChartPattern):
        """패턴 관련 질문 생성"""
        
        # 패턴 식별 질문
        options = [pattern.pattern_type.value] + random.sample(
            [pt.value for pt in PatternType if pt != pattern.pattern_type], 3
        )
        random.shuffle(options)
        
        challenge.add_question(
            "차트에서 발견되는 패턴은 무엇입니까?",
            pattern.pattern_type.value,
            options,
            f"이 패턴은 {pattern.description}의 특징을 보입니다."
        )
        
        # 신호 방향 질문
        signal_options = ["상승", "하락", "중립"]
        correct_signal = "상승" if pattern.signal.value == "bullish" else "하락" if pattern.signal.value == "bearish" else "중립"
        
        challenge.add_question(
            "이 패턴이 나타내는 신호는?",
            correct_signal,
            signal_options,
            f"이 패턴은 일반적으로 {correct_signal} 신호로 해석됩니다."
        )
        
        # 목표가 질문 (있는 경우)
        if pattern.target_price:
            current_price = challenge.chart_data['close'].iloc[-1]
            price_change = ((pattern.target_price - current_price) / current_price) * 100
            
            target_options = [
                f"{price_change:.1f}%",
                f"{price_change * 0.5:.1f}%",
                f"{price_change * 1.5:.1f}%",
                f"{price_change * 2:.1f}%"
            ]
            
            challenge.add_question(
                "이 패턴의 예상 목표 수익률은?",
                f"{price_change:.1f}%",
                target_options,
                f"패턴의 높이를 기준으로 계산한 목표가입니다."
            )
    
    def _generate_indicator_questions(self, challenge: PatternChallenge, indicators: List[TechnicalIndicator]):
        """지표 관련 질문 생성"""
        
        for indicator in indicators:
            latest_value = indicator.get_latest_value()
            if not latest_value:
                continue
            
            if indicator.indicator_type == IndicatorType.RSI:
                rsi_val = latest_value.value
                
                if rsi_val >= 70:
                    correct_answer = "과매수"
                    options = ["과매수", "과매도", "중립", "강세"]
                elif rsi_val <= 30:
                    correct_answer = "과매도"
                    options = ["과매도", "과매수", "중립", "약세"]
                else:
                    correct_answer = "중립"
                    options = ["중립", "과매수", "과매도", "추세 없음"]
                
                challenge.add_question(
                    f"현재 RSI({rsi_val:.1f})는 어떤 상태를 나타냅니까?",
                    correct_answer,
                    options,
                    f"RSI {rsi_val:.1f}는 {correct_answer} 구간입니다."
                )
            
            elif indicator.indicator_type == IndicatorType.MACD:
                macd_data = latest_value.value
                if isinstance(macd_data, dict):
                    macd_line = macd_data.get('macd', 0)
                    signal_line = macd_data.get('signal', 0)
                    
                    if macd_line > signal_line:
                        correct_answer = "매수 신호"
                        options = ["매수 신호", "매도 신호", "관망", "중립"]
                    else:
                        correct_answer = "매도 신호"
                        options = ["매도 신호", "매수 신호", "관망", "중립"]
                    
                    challenge.add_question(
                        "현재 MACD 신호는?",
                        correct_answer,
                        options,
                        f"MACD 선이 신호선을 {'상향' if macd_line > signal_line else '하향'} 돌파했습니다."
                    )
    
    def _generate_timing_questions(self, challenge: PatternChallenge, data: pd.DataFrame, indicators: List[TechnicalIndicator]):
        """타이밍 관련 질문 생성"""
        
        # 최적 매수 시점 찾기
        best_buy_points = []
        
        # 가격 데이터에서 저점들 찾기
        for i in range(5, len(data) - 5):
            if data['close'].iloc[i] == data['close'].iloc[i-5:i+6].min():
                best_buy_points.append(i)
        
        if best_buy_points:
            correct_timing = random.choice(best_buy_points)
            wrong_timings = random.sample(range(10, len(data) - 10), 3)
            
            timing_options = [correct_timing] + wrong_timings
            random.shuffle(timing_options)
            
            challenge.add_question(
                "차트에서 가장 적절한 매수 타이밍은 언제입니까? (차트 상의 날짜 인덱스)",
                correct_timing,
                timing_options,
                f"지표 신호와 가격 패턴을 종합적으로 고려한 최적 타이밍입니다."
            )
    
    def _generate_divergence_questions(self, challenge: PatternChallenge, divergences: List[Dict[str, Any]]):
        """다이버전스 관련 질문 생성"""
        
        if divergences:
            # 다이버전스 존재 여부
            challenge.add_question(
                "차트에서 가격과 지표 간 다이버전스가 관찰됩니까?",
                "예",
                ["예", "아니오"],
                f"{len(divergences)}개의 다이버전스 패턴이 발견되었습니다."
            )
            
            # 다이버전스 유형
            if divergences:
                div_type = divergences[0]['type']
                type_name = "강세 다이버전스" if "bullish" in div_type else "약세 다이버전스"
                
                challenge.add_question(
                    "발견된 다이버전스의 유형은?",
                    type_name,
                    ["강세 다이버전스", "약세 다이버전스", "히든 다이버전스", "다이버전스 없음"],
                    divergences[0]['description']
                )
        else:
            challenge.add_question(
                "차트에서 가격과 지표 간 다이버전스가 관찰됩니까?",
                "아니오",
                ["예", "아니오"],
                "명확한 다이버전스 패턴이 발견되지 않습니다."
            )
    
    def _is_answer_correct(self, submitted: Any, correct: Any, challenge_type: ChallengeType) -> bool:
        """답안 정확성 확인"""
        
        if challenge_type == ChallengeType.TIMING:
            # 타이밍 문제는 허용 오차 범위 내에서 정답 처리
            if isinstance(submitted, (int, float)) and isinstance(correct, (int, float)):
                return abs(submitted - correct) <= 2  # ±2일 허용
        
        return str(submitted).lower().strip() == str(correct).lower().strip()
    
    def _calculate_speed_bonus(self, time_taken: float, time_limit: Optional[int]) -> float:
        """속도 보너스 계산"""
        
        if not time_limit or time_taken >= time_limit:
            return 0.0
        
        # 제한 시간의 50% 이내 완료 시 최대 10점 보너스
        time_ratio = time_taken / time_limit
        if time_ratio <= 0.5:
            return 10.0
        elif time_ratio <= 0.7:
            return 5.0
        elif time_ratio <= 0.8:
            return 2.0
        else:
            return 0.0
    
    def _analyze_performance(self, result: PatternGameResult, challenge: PatternChallenge, answers: List[Any]):
        """성과 분석 및 피드백 생성"""
        
        # 강점과 약점 분석
        if result.accuracy >= 0.8:
            result.strengths.append("패턴 인식 능력 우수")
        if result.accuracy >= 0.9:
            result.strengths.append("정확한 분석 능력")
        if result.speed_bonus > 0:
            result.strengths.append("빠른 판단력")
        
        if result.accuracy < 0.6:
            result.weaknesses.append("기본 패턴 학습 필요")
        if result.speed_bonus == 0 and challenge.time_limit:
            result.weaknesses.append("의사결정 속도 개선 필요")
        
        # 개선 제안
        if challenge.game_mode == GameMode.PATTERN_RECOGNITION and result.accuracy < 0.7:
            result.improvement_suggestions.append("차트 패턴 기초 학습을 더 진행해보세요")
            result.improvement_suggestions.append("패턴의 핵심 특징에 집중하세요")
        
        if challenge.game_mode == GameMode.INDICATOR_ANALYSIS and result.accuracy < 0.7:
            result.improvement_suggestions.append("기술적 지표의 기본 개념을 복습하세요")
            result.improvement_suggestions.append("지표 간 상호작용을 이해해보세요")
    
    def _calculate_rewards(self, result: PatternGameResult, challenge: PatternChallenge):
        """보상 계산"""
        
        final_score = result.calculate_final_score()
        
        # 기본 경험치
        base_exp = 50
        accuracy_bonus = int(result.accuracy * 50)
        difficulty_bonus = int((challenge.get_difficulty_multiplier() - 1) * 30)
        speed_bonus_exp = int(result.speed_bonus)
        
        result.experience_gained = base_exp + accuracy_bonus + difficulty_bonus + speed_bonus_exp
        
        # 배지 획득
        if final_score >= 95:
            result.badges_earned.append("완벽주의자")
        if final_score >= 90:
            result.badges_earned.append("패턴 마스터")
        if result.speed_bonus >= 10:
            result.badges_earned.append("빛의 속도")
        if challenge.difficulty == PatternDifficulty.EXPERT and final_score >= 80:
            result.badges_earned.append("전문가")
    
    def _update_player_performance(self, player_id: str, score: float):
        """플레이어 성과 기록 업데이트"""
        
        if player_id not in self.player_performance_history:
            self.player_performance_history[player_id] = []
        
        self.player_performance_history[player_id].append(score)
        
        # 최근 20개 기록만 유지
        if len(self.player_performance_history[player_id]) > 20:
            self.player_performance_history[player_id] = self.player_performance_history[player_id][-20:]
    
    def get_challenge_statistics(self) -> Dict[str, Any]:
        """챌린지 통계 반환"""
        
        total_challenges = len(self.completed_results)
        if total_challenges == 0:
            return {'total_challenges': 0}
        
        scores = [result.calculate_final_score() for result in self.completed_results.values()]
        accuracy_rates = [result.accuracy for result in self.completed_results.values()]
        
        return {
            'total_challenges': total_challenges,
            'average_score': sum(scores) / len(scores),
            'average_accuracy': sum(accuracy_rates) / len(accuracy_rates),
            'completion_rate': total_challenges / len(self.active_challenges) if self.active_challenges else 1.0,
            'difficulty_distribution': self._get_difficulty_distribution(),
            'popular_game_modes': self._get_popular_game_modes()
        }
    
    def _get_difficulty_distribution(self) -> Dict[str, int]:
        """난이도별 분포"""
        distribution = {}
        for result in self.completed_results.values():
            challenge = self.active_challenges.get(result.challenge_id)
            if challenge:
                difficulty = challenge.difficulty.value
                distribution[difficulty] = distribution.get(difficulty, 0) + 1
        return distribution
    
    def _get_popular_game_modes(self) -> Dict[str, int]:
        """인기 게임 모드"""
        modes = {}
        for result in self.completed_results.values():
            challenge = self.active_challenges.get(result.challenge_id)
            if challenge:
                mode = challenge.game_mode.value
                modes[mode] = modes.get(mode, 0) + 1
        return modes