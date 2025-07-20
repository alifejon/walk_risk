"""
Chart pattern models and recognition system
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import random
import math

from ...utils.logger import logger


class PatternType(Enum):
    """차트 패턴 유형"""
    # 반전 패턴
    HEAD_AND_SHOULDERS = "head_and_shoulders"
    INVERSE_HEAD_AND_SHOULDERS = "inverse_head_and_shoulders"
    DOUBLE_TOP = "double_top"
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_TOP = "triple_top"
    TRIPLE_BOTTOM = "triple_bottom"
    
    # 지속 패턴
    ASCENDING_TRIANGLE = "ascending_triangle"
    DESCENDING_TRIANGLE = "descending_triangle"
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    FLAG = "flag"
    PENNANT = "pennant"
    WEDGE_RISING = "wedge_rising"
    WEDGE_FALLING = "wedge_falling"
    
    # 기타 패턴
    CUP_AND_HANDLE = "cup_and_handle"
    RECTANGLE = "rectangle"
    CHANNEL = "channel"


class PatternSignal(Enum):
    """패턴 신호"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    BREAKOUT_UP = "breakout_up"
    BREAKOUT_DOWN = "breakout_down"
    BREAKDOWN = "breakdown"


@dataclass
class PatternPoint:
    """패턴의 주요 포인트"""
    timestamp: datetime
    price: float
    point_type: str  # peak, trough, support, resistance, breakout
    importance: float = 1.0  # 0.0 ~ 1.0


@dataclass
class ChartPattern:
    """차트 패턴 정의"""
    pattern_type: PatternType
    signal: PatternSignal
    confidence: float  # 0.0 ~ 1.0
    
    # 패턴 구성 요소
    key_points: List[PatternPoint] = field(default_factory=list)
    support_levels: List[float] = field(default_factory=list)
    resistance_levels: List[float] = field(default_factory=list)
    
    # 패턴 메타데이터
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_days: Optional[int] = None
    height: Optional[float] = None  # 패턴의 높이 (가격 범위)
    
    # 예측 정보
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    probability: Optional[float] = None
    
    # 교육용 정보
    description: str = ""
    characteristics: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    trading_tips: List[str] = field(default_factory=list)
    
    def calculate_risk_reward_ratio(self) -> Optional[float]:
        """리스크 리워드 비율 계산"""
        if not (self.target_price and self.stop_loss):
            return None
        
        current_price = self.key_points[-1].price if self.key_points else None
        if not current_price:
            return None
        
        reward = abs(self.target_price - current_price)
        risk = abs(current_price - self.stop_loss)
        
        return reward / risk if risk > 0 else None
    
    def get_pattern_completion_percentage(self) -> float:
        """패턴 완성도 계산"""
        required_points = self._get_required_points_count()
        current_points = len(self.key_points)
        return min(1.0, current_points / required_points)
    
    def _get_required_points_count(self) -> int:
        """패턴별 필요한 포인트 수"""
        pattern_requirements = {
            PatternType.HEAD_AND_SHOULDERS: 5,  # left shoulder, head, right shoulder, neckline breaks
            PatternType.DOUBLE_TOP: 4,  # first peak, trough, second peak, breakdown
            PatternType.DOUBLE_BOTTOM: 4,
            PatternType.ASCENDING_TRIANGLE: 6,  # at least 3 highs, 3 lows
            PatternType.FLAG: 4,  # pole start, pole end, flag start, flag end
            PatternType.CUP_AND_HANDLE: 6  # cup formation + handle
        }
        return pattern_requirements.get(self.pattern_type, 3)
    
    def is_pattern_complete(self) -> bool:
        """패턴이 완성되었는지 확인"""
        return self.get_pattern_completion_percentage() >= 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'pattern_type': self.pattern_type.value,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'completion_percentage': self.get_pattern_completion_percentage(),
            'risk_reward_ratio': self.calculate_risk_reward_ratio(),
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'probability': self.probability,
            'description': self.description,
            'characteristics': self.characteristics,
            'trading_tips': self.trading_tips,
            'key_points_count': len(self.key_points),
            'duration_days': self.duration_days
        }


class ChartPatternLibrary:
    """차트 패턴 라이브러리"""
    
    def __init__(self):
        self.patterns: Dict[PatternType, Dict] = {}
        self._initialize_pattern_definitions()
    
    def _initialize_pattern_definitions(self):
        """패턴 정의 초기화"""
        
        # Head and Shoulders 패턴
        self.patterns[PatternType.HEAD_AND_SHOULDERS] = {
            'name': '헤드 앤 숄더',
            'description': '상승 추세의 끝에서 나타나는 강력한 반전 신호',
            'signal': PatternSignal.BEARISH,
            'characteristics': [
                '세 개의 봉우리가 연속으로 나타남',
                '가운데 봉우리(헤드)가 가장 높음',
                '양쪽 어깨는 비슷한 높이',
                '네크라인 돌파 시 확정'
            ],
            'formation_rules': {
                'min_duration': 20,  # 최소 20일
                'max_duration': 200,  # 최대 200일
                'head_prominence': 1.05,  # 헤드가 어깨보다 5% 이상 높아야 함
                'shoulder_symmetry': 0.1,  # 어깨 높이 차이 10% 이내
                'volume_pattern': 'decreasing'  # 거래량은 감소 패턴
            },
            'trading_rules': {
                'entry': 'neckline_break',
                'target': 'neckline_minus_head_height',
                'stop_loss': 'above_right_shoulder'
            },
            'success_rate': 0.75,
            'common_mistakes': [
                '가짜 돌파에 속아 조기 진입',
                '볼륨 확인 없이 진입',
                '목표가 도달 전 성급한 청산'
            ]
        }
        
        # Double Top 패턴
        self.patterns[PatternType.DOUBLE_TOP] = {
            'name': '더블 탑',
            'description': '상승 추세의 끝에서 나타나는 반전 패턴',
            'signal': PatternSignal.BEARISH,
            'characteristics': [
                '두 개의 비슷한 높이의 고점',
                '중간에 명확한 저점',
                '거래량은 두 번째 고점에서 감소',
                '지지선 이탈 시 확정'
            ],
            'formation_rules': {
                'min_duration': 15,
                'max_duration': 150,
                'peak_similarity': 0.03,  # 두 고점 차이 3% 이내
                'valley_depth': 0.1,  # 중간 저점이 고점 대비 10% 이상 하락
                'volume_pattern': 'second_peak_lower'
            },
            'trading_rules': {
                'entry': 'support_break',
                'target': 'support_minus_pattern_height',
                'stop_loss': 'above_second_peak'
            },
            'success_rate': 0.65,
            'common_mistakes': [
                '패턴 미완성 시 조기 진입',
                '거래량 무시',
                '목표가 너무 욕심내기'
            ]
        }
        
        # Ascending Triangle 패턴
        self.patterns[PatternType.ASCENDING_TRIANGLE] = {
            'name': '상승 삼각형',
            'description': '상승 지속 패턴으로 강세 신호',
            'signal': PatternSignal.BULLISH,
            'characteristics': [
                '수평 저항선과 상승 지지선',
                '고점들이 비슷한 수준',
                '저점들이 점차 상승',
                '거래량은 돌파 시 증가'
            ],
            'formation_rules': {
                'min_duration': 10,
                'max_duration': 100,
                'resistance_tolerance': 0.02,  # 저항선 허용 오차 2%
                'support_slope': 'positive',  # 지지선은 상승
                'min_touches': 3  # 각 선에 최소 3번 터치
            },
            'trading_rules': {
                'entry': 'resistance_breakout',
                'target': 'resistance_plus_pattern_height',
                'stop_loss': 'below_last_low'
            },
            'success_rate': 0.70,
            'common_mistakes': [
                '거짓 돌파 구별 실패',
                '볼륨 증가 확인 없이 진입',
                '패턴 높이 측정 오류'
            ]
        }
        
        # Flag 패턴
        self.patterns[PatternType.FLAG] = {
            'name': '깃발형',
            'description': '급격한 움직임 후 짧은 조정을 거쳐 재개되는 지속 패턴',
            'signal': PatternSignal.BULLISH,  # 또는 BEARISH (방향에 따라)
            'characteristics': [
                '급격한 가격 상승(깃대)',
                '짧은 기간의 소폭 하락 조정',
                '평행한 추세선으로 형성',
                '작은 거래량으로 조정'
            ],
            'formation_rules': {
                'pole_min_move': 0.15,  # 깃대는 최소 15% 움직임
                'flag_duration': (3, 20),  # 깃발은 3-20일
                'flag_retracement': (0.25, 0.5),  # 깃발은 깃대의 25-50% 되돌림
                'volume_pattern': 'decreasing_in_flag'
            },
            'trading_rules': {
                'entry': 'flag_breakout',
                'target': 'pole_height_projection',
                'stop_loss': 'below_flag_low'
            },
            'success_rate': 0.80,
            'common_mistakes': [
                '깃대 높이 측정 실수',
                '조정 기간 너무 길게 기다림',
                '거래량 패턴 무시'
            ]
        }
        
        # Cup and Handle 패턴
        self.patterns[PatternType.CUP_AND_HANDLE] = {
            'name': '컵 앤 핸들',
            'description': 'William O\'Neil이 개발한 강력한 상승 지속 패턴',
            'signal': PatternSignal.BULLISH,
            'characteristics': [
                'U자형 컵 모양의 조정',
                '컵 오른쪽에 작은 핸들 형성',
                '핸들은 컵 깊이의 1/3 이하',
                '강한 기업의 주식에서 자주 나타남'
            ],
            'formation_rules': {
                'cup_duration': (7, 65),  # 컵은 7주-65주
                'cup_depth': (0.15, 0.5),  # 컵 깊이 15-50%
                'handle_duration': (1, 5),  # 핸들은 1-5주
                'handle_depth': 0.15,  # 핸들 깊이 최대 15%
                'volume_pattern': 'dry_up_in_handle'
            },
            'trading_rules': {
                'entry': 'handle_breakout',
                'target': 'cup_depth_projection',
                'stop_loss': 'below_handle_low'
            },
            'success_rate': 0.85,
            'common_mistakes': [
                '핸들 깊이가 너무 깊음',
                '거래량 확인 없이 진입',
                '기업 펀더멘털 무시'
            ]
        }
        
        logger.info(f"차트 패턴 라이브러리 초기화 완료: {len(self.patterns)}개 패턴")
    
    def get_pattern_definition(self, pattern_type: PatternType) -> Dict:
        """패턴 정의 반환"""
        return self.patterns.get(pattern_type, {})
    
    def get_all_patterns(self) -> Dict[PatternType, Dict]:
        """모든 패턴 반환"""
        return self.patterns.copy()
    
    def get_patterns_by_signal(self, signal: PatternSignal) -> List[PatternType]:
        """신호별 패턴 목록 반환"""
        return [
            pattern_type for pattern_type, definition in self.patterns.items()
            if definition.get('signal') == signal
        ]
    
    def calculate_pattern_probability(self, pattern_type: PatternType, market_context: Dict) -> float:
        """시장 상황을 고려한 패턴 성공 확률 계산"""
        base_success_rate = self.patterns[pattern_type].get('success_rate', 0.5)
        
        # 시장 상황 조정 팩터
        trend_factor = market_context.get('trend_strength', 1.0)
        volume_factor = market_context.get('volume_confirmation', 1.0)
        volatility_factor = market_context.get('volatility_level', 1.0)
        
        # 조정된 확률 계산
        adjusted_probability = base_success_rate * trend_factor * volume_factor * volatility_factor
        
        # 0과 1 사이로 클램프
        return max(0.1, min(0.9, adjusted_probability))


class PatternRecognizer:
    """차트 패턴 인식 엔진"""
    
    def __init__(self, pattern_library: ChartPatternLibrary):
        self.pattern_library = pattern_library
        self.detection_sensitivity = 0.7  # 패턴 감지 민감도
    
    def detect_patterns(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """가격 데이터에서 패턴 감지"""
        detected_patterns = []
        
        # 각 패턴 타입별로 감지 시도
        for pattern_type in PatternType:
            patterns = self._detect_specific_pattern(pattern_type, price_data, volume_data)
            detected_patterns.extend(patterns)
        
        # 신뢰도 순으로 정렬
        detected_patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return detected_patterns
    
    def _detect_specific_pattern(self, pattern_type: PatternType, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """특정 패턴 감지"""
        
        if pattern_type == PatternType.HEAD_AND_SHOULDERS:
            return self._detect_head_and_shoulders(price_data, volume_data)
        elif pattern_type == PatternType.DOUBLE_TOP:
            return self._detect_double_top(price_data, volume_data)
        elif pattern_type == PatternType.ASCENDING_TRIANGLE:
            return self._detect_ascending_triangle(price_data, volume_data)
        elif pattern_type == PatternType.FLAG:
            return self._detect_flag_pattern(price_data, volume_data)
        elif pattern_type == PatternType.CUP_AND_HANDLE:
            return self._detect_cup_and_handle(price_data, volume_data)
        
        return []
    
    def _detect_head_and_shoulders(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """헤드 앤 숄더 패턴 감지"""
        patterns = []
        
        # 고점 찾기
        peaks = self._find_peaks(price_data['high'])
        if len(peaks) < 3:
            return patterns
        
        # 연속된 3개 고점에 대해 H&S 패턴 확인
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]
            
            # H&S 조건 확인
            if self._is_valid_head_and_shoulders(left_shoulder, head, right_shoulder, price_data):
                pattern = self._create_head_and_shoulders_pattern(left_shoulder, head, right_shoulder, price_data)
                patterns.append(pattern)
        
        return patterns
    
    def _detect_double_top(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """더블 탑 패턴 감지"""
        patterns = []
        
        peaks = self._find_peaks(price_data['high'])
        if len(peaks) < 2:
            return patterns
        
        # 연속된 2개 고점에 대해 더블 탑 확인
        for i in range(len(peaks) - 1):
            first_peak = peaks[i]
            second_peak = peaks[i + 1]
            
            if self._is_valid_double_top(first_peak, second_peak, price_data):
                pattern = self._create_double_top_pattern(first_peak, second_peak, price_data)
                patterns.append(pattern)
        
        return patterns
    
    def _detect_ascending_triangle(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """상승 삼각형 패턴 감지"""
        patterns = []
        
        # 고점과 저점 찾기
        peaks = self._find_peaks(price_data['high'])
        troughs = self._find_troughs(price_data['low'])
        
        if len(peaks) < 3 or len(troughs) < 3:
            return patterns
        
        # 상승 삼각형 조건 확인
        if self._is_valid_ascending_triangle(peaks, troughs, price_data):
            pattern = self._create_ascending_triangle_pattern(peaks, troughs, price_data)
            patterns.append(pattern)
        
        return patterns
    
    def _detect_flag_pattern(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """깃발형 패턴 감지"""
        patterns = []
        
        # 급격한 움직임(깃대) 찾기
        potential_poles = self._find_strong_moves(price_data)
        
        for pole_start, pole_end in potential_poles:
            # 깃발 부분 확인
            flag_pattern = self._check_flag_formation(pole_start, pole_end, price_data)
            if flag_pattern:
                patterns.append(flag_pattern)
        
        return patterns
    
    def _detect_cup_and_handle(self, price_data: pd.DataFrame, volume_data: pd.DataFrame = None) -> List[ChartPattern]:
        """컵 앤 핸들 패턴 감지"""
        patterns = []
        
        # 컵 모양 찾기
        potential_cups = self._find_cup_formations(price_data)
        
        for cup_start, cup_bottom, cup_end in potential_cups:
            # 핸들 부분 확인
            handle_pattern = self._check_handle_formation(cup_start, cup_bottom, cup_end, price_data)
            if handle_pattern:
                patterns.append(handle_pattern)
        
        return patterns
    
    # Helper methods for pattern detection
    
    def _find_peaks(self, data: pd.Series, prominence: float = 0.02) -> List[int]:
        """고점 찾기"""
        peaks = []
        for i in range(1, len(data) - 1):
            if (data.iloc[i] > data.iloc[i-1] and 
                data.iloc[i] > data.iloc[i+1] and
                data.iloc[i] / min(data.iloc[i-1], data.iloc[i+1]) > (1 + prominence)):
                peaks.append(i)
        return peaks
    
    def _find_troughs(self, data: pd.Series, prominence: float = 0.02) -> List[int]:
        """저점 찾기"""
        troughs = []
        for i in range(1, len(data) - 1):
            if (data.iloc[i] < data.iloc[i-1] and 
                data.iloc[i] < data.iloc[i+1] and
                max(data.iloc[i-1], data.iloc[i+1]) / data.iloc[i] > (1 + prominence)):
                troughs.append(i)
        return troughs
    
    def _is_valid_head_and_shoulders(self, left_shoulder: int, head: int, right_shoulder: int, price_data: pd.DataFrame) -> bool:
        """헤드 앤 숄더 유효성 검증"""
        left_price = price_data['high'].iloc[left_shoulder]
        head_price = price_data['high'].iloc[head]
        right_price = price_data['high'].iloc[right_shoulder]
        
        # 헤드가 양쪽 어깨보다 높아야 함
        if head_price <= max(left_price, right_price):
            return False
        
        # 어깨들이 비슷한 높이여야 함
        shoulder_diff = abs(left_price - right_price) / max(left_price, right_price)
        if shoulder_diff > 0.1:  # 10% 이상 차이 나면 무효
            return False
        
        # 헤드가 어깨보다 충분히 높아야 함
        head_prominence = head_price / max(left_price, right_price)
        if head_prominence < 1.05:  # 5% 이상 높아야 함
            return False
        
        return True
    
    def _is_valid_double_top(self, first_peak: int, second_peak: int, price_data: pd.DataFrame) -> bool:
        """더블 탑 유효성 검증"""
        first_price = price_data['high'].iloc[first_peak]
        second_price = price_data['high'].iloc[second_peak]
        
        # 두 고점이 비슷한 높이여야 함
        price_diff = abs(first_price - second_price) / max(first_price, second_price)
        if price_diff > 0.03:  # 3% 이상 차이 나면 무효
            return False
        
        # 중간에 충분한 하락이 있어야 함
        valley_start = first_peak
        valley_end = second_peak
        valley_low = price_data['low'].iloc[valley_start:valley_end+1].min()
        valley_depth = (max(first_price, second_price) - valley_low) / max(first_price, second_price)
        
        if valley_depth < 0.1:  # 10% 이상 하락해야 함
            return False
        
        return True
    
    def _is_valid_ascending_triangle(self, peaks: List[int], troughs: List[int], price_data: pd.DataFrame) -> bool:
        """상승 삼각형 유효성 검증"""
        if len(peaks) < 3 or len(troughs) < 3:
            return False
        
        # 고점들이 비슷한 수준인지 확인 (수평 저항선)
        peak_prices = [price_data['high'].iloc[p] for p in peaks[-3:]]
        peak_variance = np.var(peak_prices) / np.mean(peak_prices)
        if peak_variance > 0.01:  # 분산이 너무 크면 무효
            return False
        
        # 저점들이 상승하는지 확인
        trough_prices = [price_data['low'].iloc[t] for t in troughs[-3:]]
        if not all(trough_prices[i] < trough_prices[i+1] for i in range(len(trough_prices)-1)):
            return False
        
        return True
    
    def _create_head_and_shoulders_pattern(self, left_shoulder: int, head: int, right_shoulder: int, price_data: pd.DataFrame) -> ChartPattern:
        """헤드 앤 숄더 패턴 객체 생성"""
        
        # 키 포인트 생성
        key_points = [
            PatternPoint(price_data.index[left_shoulder], price_data['high'].iloc[left_shoulder], "left_shoulder"),
            PatternPoint(price_data.index[head], price_data['high'].iloc[head], "head"),
            PatternPoint(price_data.index[right_shoulder], price_data['high'].iloc[right_shoulder], "right_shoulder")
        ]
        
        # 네크라인 계산 (왼쪽 어깨와 오른쪽 어깨 사이의 저점들로 구성)
        neckline_level = self._calculate_neckline(left_shoulder, right_shoulder, price_data)
        
        # 목표가 계산 (네크라인에서 헤드 높이만큼 빼기)
        head_height = price_data['high'].iloc[head] - neckline_level
        target_price = neckline_level - head_height
        
        # 손절가 계산 (오른쪽 어깨 위)
        stop_loss = price_data['high'].iloc[right_shoulder] * 1.02
        
        pattern_def = self.pattern_library.get_pattern_definition(PatternType.HEAD_AND_SHOULDERS)
        
        return ChartPattern(
            pattern_type=PatternType.HEAD_AND_SHOULDERS,
            signal=PatternSignal.BEARISH,
            confidence=0.8,  # 임시값, 추후 정교한 계산 필요
            key_points=key_points,
            resistance_levels=[price_data['high'].iloc[head]],
            support_levels=[neckline_level],
            start_time=price_data.index[left_shoulder],
            end_time=price_data.index[right_shoulder],
            target_price=target_price,
            stop_loss=stop_loss,
            description=pattern_def.get('description', ''),
            characteristics=pattern_def.get('characteristics', []),
            trading_tips=pattern_def.get('common_mistakes', [])
        )
    
    def _create_double_top_pattern(self, first_peak: int, second_peak: int, price_data: pd.DataFrame) -> ChartPattern:
        """더블 탑 패턴 객체 생성"""
        
        key_points = [
            PatternPoint(price_data.index[first_peak], price_data['high'].iloc[first_peak], "first_peak"),
            PatternPoint(price_data.index[second_peak], price_data['high'].iloc[second_peak], "second_peak")
        ]
        
        # 중간 저점 찾기
        valley_idx = price_data['low'].iloc[first_peak:second_peak+1].idxmin()
        valley_price = price_data['low'].loc[valley_idx]
        key_points.insert(1, PatternPoint(valley_idx, valley_price, "valley"))
        
        # 목표가 계산
        pattern_height = max(price_data['high'].iloc[first_peak], price_data['high'].iloc[second_peak]) - valley_price
        target_price = valley_price - pattern_height
        
        # 손절가 계산
        stop_loss = max(price_data['high'].iloc[first_peak], price_data['high'].iloc[second_peak]) * 1.02
        
        pattern_def = self.pattern_library.get_pattern_definition(PatternType.DOUBLE_TOP)
        
        return ChartPattern(
            pattern_type=PatternType.DOUBLE_TOP,
            signal=PatternSignal.BEARISH,
            confidence=0.7,
            key_points=key_points,
            resistance_levels=[max(price_data['high'].iloc[first_peak], price_data['high'].iloc[second_peak])],
            support_levels=[valley_price],
            start_time=price_data.index[first_peak],
            end_time=price_data.index[second_peak],
            target_price=target_price,
            stop_loss=stop_loss,
            description=pattern_def.get('description', ''),
            characteristics=pattern_def.get('characteristics', []),
            trading_tips=pattern_def.get('common_mistakes', [])
        )
    
    def _create_ascending_triangle_pattern(self, peaks: List[int], troughs: List[int], price_data: pd.DataFrame) -> ChartPattern:
        """상승 삼각형 패턴 객체 생성"""
        
        key_points = []
        
        # 최근 3개 고점과 저점 사용
        recent_peaks = peaks[-3:]
        recent_troughs = troughs[-3:]
        
        for peak in recent_peaks:
            key_points.append(PatternPoint(price_data.index[peak], price_data['high'].iloc[peak], "resistance_touch"))
        
        for trough in recent_troughs:
            key_points.append(PatternPoint(price_data.index[trough], price_data['low'].iloc[trough], "support_touch"))
        
        # 저항선 (수평)
        resistance_level = np.mean([price_data['high'].iloc[p] for p in recent_peaks])
        
        # 목표가 계산 (패턴 높이만큼 더하기)
        pattern_height = resistance_level - min([price_data['low'].iloc[t] for t in recent_troughs])
        target_price = resistance_level + pattern_height
        
        # 손절가 계산 (최근 저점 아래)
        stop_loss = min([price_data['low'].iloc[t] for t in recent_troughs]) * 0.98
        
        pattern_def = self.pattern_library.get_pattern_definition(PatternType.ASCENDING_TRIANGLE)
        
        return ChartPattern(
            pattern_type=PatternType.ASCENDING_TRIANGLE,
            signal=PatternSignal.BULLISH,
            confidence=0.75,
            key_points=key_points,
            resistance_levels=[resistance_level],
            support_levels=[min([price_data['low'].iloc[t] for t in recent_troughs])],
            start_time=price_data.index[min(recent_peaks + recent_troughs)],
            end_time=price_data.index[max(recent_peaks + recent_troughs)],
            target_price=target_price,
            stop_loss=stop_loss,
            description=pattern_def.get('description', ''),
            characteristics=pattern_def.get('characteristics', []),
            trading_tips=pattern_def.get('common_mistakes', [])
        )
    
    def _calculate_neckline(self, left_shoulder: int, right_shoulder: int, price_data: pd.DataFrame) -> float:
        """네크라인 계산"""
        # 왼쪽 어깨와 오른쪽 어깨 사이의 저점들의 평균
        valley_data = price_data['low'].iloc[left_shoulder:right_shoulder+1]
        return valley_data.mean()
    
    def _find_strong_moves(self, price_data: pd.DataFrame) -> List[Tuple[int, int]]:
        """강한 움직임(깃대) 찾기"""
        moves = []
        min_move = 0.15  # 15% 이상 움직임
        
        for i in range(len(price_data) - 5):
            for j in range(i + 3, min(i + 20, len(price_data))):
                move_size = abs(price_data['close'].iloc[j] - price_data['close'].iloc[i]) / price_data['close'].iloc[i]
                if move_size >= min_move:
                    moves.append((i, j))
        
        return moves
    
    def _check_flag_formation(self, pole_start: int, pole_end: int, price_data: pd.DataFrame) -> Optional[ChartPattern]:
        """깃발 형성 확인"""
        # 구현 예정
        return None
    
    def _find_cup_formations(self, price_data: pd.DataFrame) -> List[Tuple[int, int, int]]:
        """컵 형성 찾기"""
        # 구현 예정
        return []
    
    def _check_handle_formation(self, cup_start: int, cup_bottom: int, cup_end: int, price_data: pd.DataFrame) -> Optional[ChartPattern]:
        """핸들 형성 확인"""
        # 구현 예정
        return None
    
    def generate_synthetic_pattern(self, pattern_type: PatternType, difficulty: float = 0.5) -> Tuple[pd.DataFrame, ChartPattern]:
        """교육용 합성 패턴 생성"""
        
        if pattern_type == PatternType.HEAD_AND_SHOULDERS:
            return self._generate_synthetic_head_and_shoulders(difficulty)
        elif pattern_type == PatternType.DOUBLE_TOP:
            return self._generate_synthetic_double_top(difficulty)
        elif pattern_type == PatternType.ASCENDING_TRIANGLE:
            return self._generate_synthetic_ascending_triangle(difficulty)
        else:
            # 기본 패턴 생성
            return self._generate_basic_synthetic_pattern(pattern_type, difficulty)
    
    def _generate_synthetic_head_and_shoulders(self, difficulty: float) -> Tuple[pd.DataFrame, ChartPattern]:
        """합성 헤드 앤 숄더 패턴 생성"""
        
        # 기본 설정
        base_price = 100
        days = 60
        noise_level = 0.02 * (1 + difficulty)  # 난이도에 따른 노이즈
        
        # 시간 인덱스 생성
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        
        # 가격 데이터 생성
        prices = []
        
        # 왼쪽 어깨 (0-15일)
        left_shoulder_peak = base_price * 1.1
        for i in range(15):
            if i < 7:
                price = base_price + (left_shoulder_peak - base_price) * (i / 7)
            else:
                price = left_shoulder_peak - (left_shoulder_peak - base_price * 0.95) * ((i - 7) / 8)
            
            # 노이즈 추가
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 헤드 (15-35일)
        head_peak = base_price * 1.2
        valley_price = base_price * 0.95
        for i in range(20):
            if i < 10:
                price = valley_price + (head_peak - valley_price) * (i / 10)
            else:
                price = head_peak - (head_peak - valley_price) * ((i - 10) / 10)
            
            # 노이즈 추가
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 오른쪽 어깨 (35-50일)
        right_shoulder_peak = base_price * 1.08  # 왼쪽보다 약간 낮게
        for i in range(15):
            if i < 7:
                price = valley_price + (right_shoulder_peak - valley_price) * (i / 7)
            else:
                price = right_shoulder_peak - (right_shoulder_peak - valley_price) * ((i - 7) / 8)
            
            # 노이즈 추가
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 네크라인 돌파 (50-60일)
        neckline = valley_price
        target_price = neckline - (head_peak - neckline)
        for i in range(10):
            price = neckline - (neckline - target_price) * (i / 10)
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # OHLC 데이터 생성
        ohlc_data = []
        for i, close in enumerate(prices):
            high = close * random.uniform(1.001, 1.01)
            low = close * random.uniform(0.99, 0.999)
            open_price = prices[i-1] if i > 0 else close
            
            ohlc_data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': random.randint(100000, 1000000)
            })
        
        df = pd.DataFrame(ohlc_data, index=dates[:len(prices)])
        
        # 패턴 객체 생성
        key_points = [
            PatternPoint(dates[7], left_shoulder_peak, "left_shoulder"),
            PatternPoint(dates[25], head_peak, "head"),
            PatternPoint(dates[42], right_shoulder_peak, "right_shoulder"),
            PatternPoint(dates[50], neckline, "neckline_break")
        ]
        
        pattern = ChartPattern(
            pattern_type=PatternType.HEAD_AND_SHOULDERS,
            signal=PatternSignal.BEARISH,
            confidence=0.9,
            key_points=key_points,
            resistance_levels=[head_peak],
            support_levels=[neckline],
            start_time=dates[0],
            end_time=dates[50],
            target_price=target_price,
            stop_loss=right_shoulder_peak * 1.02,
            description="교육용 헤드 앤 숄더 패턴",
            characteristics=[
                "세 개의 봉우리 중 가운데가 가장 높음",
                "양쪽 어깨는 비슷한 높이",
                "네크라인 돌파 시 하락 신호"
            ]
        )
        
        return df, pattern
    
    def _generate_synthetic_double_top(self, difficulty: float) -> Tuple[pd.DataFrame, ChartPattern]:
        """합성 더블 탑 패턴 생성"""
        
        base_price = 100
        days = 40
        noise_level = 0.02 * (1 + difficulty)
        
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        prices = []
        
        # 첫 번째 고점 (0-12일)
        first_peak = base_price * 1.15
        for i in range(12):
            if i < 6:
                price = base_price + (first_peak - base_price) * (i / 6)
            else:
                price = first_peak - (first_peak - base_price * 0.92) * ((i - 6) / 6)
            
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 중간 저점 유지 (12-16일)
        valley_price = base_price * 0.92
        for i in range(4):
            price = valley_price * (1 + random.uniform(-noise_level/2, noise_level/2))
            prices.append(price)
        
        # 두 번째 고점 (16-28일)
        second_peak = base_price * 1.14  # 첫 번째와 비슷하지만 약간 낮게
        for i in range(12):
            if i < 6:
                price = valley_price + (second_peak - valley_price) * (i / 6)
            else:
                price = second_peak - (second_peak - valley_price) * ((i - 6) / 6)
            
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 지지선 돌파 (28-40일)
        target_price = valley_price - (first_peak - valley_price)
        for i in range(12):
            price = valley_price - (valley_price - target_price) * (i / 12)
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # OHLC 데이터 생성
        ohlc_data = []
        for i, close in enumerate(prices):
            high = close * random.uniform(1.001, 1.008)
            low = close * random.uniform(0.992, 0.999)
            open_price = prices[i-1] if i > 0 else close
            
            ohlc_data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': random.randint(100000, 1000000)
            })
        
        df = pd.DataFrame(ohlc_data, index=dates[:len(prices)])
        
        key_points = [
            PatternPoint(dates[6], first_peak, "first_peak"),
            PatternPoint(dates[14], valley_price, "valley"),
            PatternPoint(dates[22], second_peak, "second_peak"),
            PatternPoint(dates[28], valley_price, "support_break")
        ]
        
        pattern = ChartPattern(
            pattern_type=PatternType.DOUBLE_TOP,
            signal=PatternSignal.BEARISH,
            confidence=0.85,
            key_points=key_points,
            resistance_levels=[max(first_peak, second_peak)],
            support_levels=[valley_price],
            start_time=dates[0],
            end_time=dates[28],
            target_price=target_price,
            stop_loss=max(first_peak, second_peak) * 1.02,
            description="교육용 더블 탑 패턴",
            characteristics=[
                "두 개의 비슷한 높이 고점",
                "중간에 명확한 저점",
                "지지선 이탈 시 하락 신호"
            ]
        )
        
        return df, pattern
    
    def _generate_synthetic_ascending_triangle(self, difficulty: float) -> Tuple[pd.DataFrame, ChartPattern]:
        """합성 상승 삼각형 패턴 생성"""
        
        base_price = 100
        days = 30
        noise_level = 0.015 * (1 + difficulty)
        
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        prices = []
        
        resistance_level = base_price * 1.1
        initial_support = base_price * 0.95
        
        # 삼각형 패턴 생성
        for i in range(days):
            # 상승하는 지지선
            current_support = initial_support + (resistance_level - initial_support) * 0.6 * (i / days)
            
            # 삼각형 내에서 진동
            cycle_position = (i % 6) / 6  # 6일 주기
            if cycle_position < 0.5:
                # 상승 구간
                price = current_support + (resistance_level - current_support) * (cycle_position * 2)
            else:
                # 하락 구간
                price = resistance_level - (resistance_level - current_support) * ((cycle_position - 0.5) * 2)
            
            # 저항선에 가까워질수록 더 강한 저항
            if price > resistance_level * 0.98:
                price = resistance_level * random.uniform(0.97, 0.99)
            
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 돌파 구간 추가 (마지막 5일)
        breakout_days = 5
        breakout_target = resistance_level * 1.1
        for i in range(breakout_days):
            price = resistance_level + (breakout_target - resistance_level) * (i / breakout_days)
            price *= (1 + random.uniform(-noise_level, noise_level))
            prices.append(price)
        
        # 전체 날짜 업데이트
        total_days = days + breakout_days
        dates = pd.date_range(start='2024-01-01', periods=total_days, freq='D')
        
        # OHLC 데이터 생성
        ohlc_data = []
        for i, close in enumerate(prices):
            high = close * random.uniform(1.001, 1.005)
            low = close * random.uniform(0.995, 0.999)
            open_price = prices[i-1] if i > 0 else close
            
            ohlc_data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': random.randint(50000, 200000) if i < days else random.randint(200000, 500000)  # 돌파 시 거래량 증가
            })
        
        df = pd.DataFrame(ohlc_data, index=dates)
        
        # 키 포인트 찾기 (고점과 저점)
        key_points = []
        
        # 저항선 터치 포인트들
        for i in [6, 12, 18, 24]:
            if i < len(prices):
                key_points.append(PatternPoint(dates[i], prices[i], "resistance_touch"))
        
        # 지지선 터치 포인트들  
        for i in [3, 9, 15, 21, 27]:
            if i < len(prices):
                key_points.append(PatternPoint(dates[i], prices[i], "support_touch"))
        
        # 돌파 포인트
        key_points.append(PatternPoint(dates[days], resistance_level, "breakout"))
        
        pattern = ChartPattern(
            pattern_type=PatternType.ASCENDING_TRIANGLE,
            signal=PatternSignal.BULLISH,
            confidence=0.8,
            key_points=key_points,
            resistance_levels=[resistance_level],
            support_levels=[initial_support],
            start_time=dates[0],
            end_time=dates[days],
            target_price=breakout_target,
            stop_loss=initial_support * 0.98,
            description="교육용 상승 삼각형 패턴",
            characteristics=[
                "수평 저항선과 상승 지지선",
                "고점들이 비슷한 수준",
                "저점들이 점차 상승",
                "거래량은 돌파 시 증가"
            ]
        )
        
        return df, pattern
    
    def _generate_basic_synthetic_pattern(self, pattern_type: PatternType, difficulty: float) -> Tuple[pd.DataFrame, ChartPattern]:
        """기본 합성 패턴 생성 (임시)"""
        
        # 간단한 더미 데이터 생성
        days = 30
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        base_price = 100
        
        prices = [base_price + random.uniform(-5, 5) for _ in range(days)]
        
        ohlc_data = []
        for i, close in enumerate(prices):
            high = close * 1.01
            low = close * 0.99
            open_price = prices[i-1] if i > 0 else close
            
            ohlc_data.append({
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': random.randint(100000, 1000000)
            })
        
        df = pd.DataFrame(ohlc_data, index=dates)
        
        pattern = ChartPattern(
            pattern_type=pattern_type,
            signal=PatternSignal.NEUTRAL,
            confidence=0.5,
            key_points=[],
            start_time=dates[0],
            end_time=dates[-1],
            description=f"교육용 {pattern_type.value} 패턴"
        )
        
        return df, pattern


# 패턴 인식 정확도 측정을 위한 유틸리티
class PatternAccuracyEvaluator:
    """패턴 인식 정확도 평가"""
    
    def __init__(self):
        self.test_results = []
    
    def evaluate_pattern_recognition(self, recognized_patterns: List[ChartPattern], actual_patterns: List[ChartPattern]) -> Dict[str, float]:
        """패턴 인식 정확도 평가"""
        
        if not actual_patterns:
            return {'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0}
        
        true_positives = 0
        false_positives = 0
        false_negatives = len(actual_patterns)
        
        # 인식된 패턴과 실제 패턴 매칭
        for recognized in recognized_patterns:
            matched = False
            for actual in actual_patterns:
                if self._patterns_match(recognized, actual):
                    true_positives += 1
                    false_negatives -= 1
                    matched = True
                    break
            
            if not matched:
                false_positives += 1
        
        # 메트릭 계산
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }
    
    def _patterns_match(self, pattern1: ChartPattern, pattern2: ChartPattern, tolerance: float = 0.1) -> bool:
        """두 패턴이 같은지 확인"""
        
        # 패턴 타입이 같아야 함
        if pattern1.pattern_type != pattern2.pattern_type:
            return False
        
        # 시간 범위가 겹쳐야 함
        if pattern1.end_time < pattern2.start_time or pattern2.end_time < pattern1.start_time:
            return False
        
        # 신뢰도가 임계값 이상이어야 함
        if pattern1.confidence < 0.6 or pattern2.confidence < 0.6:
            return False
        
        return True