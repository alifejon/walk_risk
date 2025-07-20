"""
Technical indicators for pattern analysis and trading signals
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import math

from ...utils.logger import logger


class IndicatorType(Enum):
    """기술적 지표 유형"""
    # 추세 지표
    MOVING_AVERAGE = "moving_average"
    EMA = "exponential_moving_average"
    MACD = "macd"
    ADX = "average_directional_index"
    PARABOLIC_SAR = "parabolic_sar"
    
    # 모멘텀 지표
    RSI = "relative_strength_index"
    STOCHASTIC = "stochastic"
    WILLIAMS_R = "williams_r"
    ROC = "rate_of_change"
    MFI = "money_flow_index"
    
    # 변동성 지표
    BOLLINGER_BANDS = "bollinger_bands"
    ATR = "average_true_range"
    VOLATILITY = "volatility"
    
    # 거래량 지표
    OBV = "on_balance_volume"
    VOLUME_MA = "volume_moving_average"
    CHAIKIN_MF = "chaikin_money_flow"
    
    # 지지/저항 지표
    PIVOT_POINTS = "pivot_points"
    FIBONACCI = "fibonacci_retracement"


class IndicatorSignal(Enum):
    """지표 신호"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    OVERBOUGHT = "overbought"
    OVERSOLD = "oversold"
    BULLISH_DIVERGENCE = "bullish_divergence"
    BEARISH_DIVERGENCE = "bearish_divergence"
    BREAKOUT = "breakout"
    BREAKDOWN = "breakdown"


@dataclass
class IndicatorValue:
    """지표 값"""
    timestamp: datetime
    value: Union[float, Dict[str, float]]  # 단일 값 또는 여러 값 (예: MACD의 경우)
    signal: Optional[IndicatorSignal] = None
    confidence: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TechnicalIndicator:
    """기술적 지표 정의"""
    indicator_type: IndicatorType
    name: str
    description: str
    
    # 지표 설정
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # 지표 값들
    values: List[IndicatorValue] = field(default_factory=list)
    
    # 신호 생성 규칙
    signal_rules: Dict[str, Any] = field(default_factory=dict)
    
    # 교육 정보
    interpretation_guide: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)
    best_timeframes: List[str] = field(default_factory=list)
    
    def get_latest_value(self) -> Optional[IndicatorValue]:
        """최신 지표 값 반환"""
        return self.values[-1] if self.values else None
    
    def get_latest_signal(self) -> Optional[IndicatorSignal]:
        """최신 신호 반환"""
        latest = self.get_latest_value()
        return latest.signal if latest else None
    
    def get_value_at_time(self, timestamp: datetime) -> Optional[IndicatorValue]:
        """특정 시점의 지표 값 반환"""
        for value in reversed(self.values):
            if value.timestamp <= timestamp:
                return value
        return None
    
    def calculate_accuracy(self, actual_movements: List[float], lookback_days: int = 5) -> float:
        """지표 신호 정확도 계산"""
        if len(self.values) < lookback_days or len(actual_movements) < lookback_days:
            return 0.0
        
        correct_predictions = 0
        total_predictions = 0
        
        for i in range(len(self.values) - lookback_days):
            signal = self.values[i].signal
            if signal in [IndicatorSignal.BUY, IndicatorSignal.SELL]:
                future_movement = sum(actual_movements[i:i+lookback_days])
                
                if signal == IndicatorSignal.BUY and future_movement > 0:
                    correct_predictions += 1
                elif signal == IndicatorSignal.SELL and future_movement < 0:
                    correct_predictions += 1
                
                total_predictions += 1
        
        return correct_predictions / total_predictions if total_predictions > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'indicator_type': self.indicator_type.value,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'latest_value': self.get_latest_value().__dict__ if self.get_latest_value() else None,
            'latest_signal': self.get_latest_signal().value if self.get_latest_signal() else None,
            'values_count': len(self.values),
            'interpretation_guide': self.interpretation_guide,
            'best_timeframes': self.best_timeframes
        }


class IndicatorCalculator:
    """기술적 지표 계산기"""
    
    def __init__(self):
        self.calculated_indicators: Dict[str, TechnicalIndicator] = {}
    
    def calculate_moving_average(self, data: pd.Series, period: int = 20, type: str = "simple") -> TechnicalIndicator:
        """이동평균 계산"""
        
        if type == "simple":
            ma_values = data.rolling(window=period).mean()
        elif type == "exponential":
            ma_values = data.ewm(span=period).mean()
        else:
            raise ValueError(f"Unsupported MA type: {type}")
        
        # 신호 생성
        signals = []
        for i in range(len(data)):
            if i < period:
                signals.append(None)
                continue
            
            current_price = data.iloc[i]
            ma_value = ma_values.iloc[i]
            
            if current_price > ma_value and data.iloc[i-1] <= ma_values.iloc[i-1]:
                signal = IndicatorSignal.BUY
            elif current_price < ma_value and data.iloc[i-1] >= ma_values.iloc[i-1]:
                signal = IndicatorSignal.SELL
            else:
                signal = IndicatorSignal.HOLD
            
            signals.append(signal)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, (timestamp, value) in enumerate(ma_values.items()):
            if not pd.isna(value):
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value=value,
                    signal=signals[i],
                    confidence=0.6
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.MOVING_AVERAGE if type == "simple" else IndicatorType.EMA,
            name=f"{period}일 {'단순' if type == 'simple' else '지수'} 이동평균",
            description=f"{period}일간의 {'단순' if type == 'simple' else '지수'} 이동평균선",
            parameters={'period': period, 'type': type},
            values=indicator_values,
            interpretation_guide=[
                "가격이 이동평균선 위에 있으면 상승 추세",
                "가격이 이동평균선 아래에 있으면 하락 추세",
                "이동평균선의 기울기로 추세 강도 판단",
                "골든크로스: 단기MA가 장기MA 상향돌파 시 매수신호",
                "데드크로스: 단기MA가 장기MA 하향돌파 시 매도신호"
            ],
            common_mistakes=[
                "횡보장에서 많은 거짓 신호 발생",
                "단일 이동평균만으로 판단하는 실수",
                "기간 설정이 시장 특성과 맞지 않음"
            ],
            best_timeframes=["일봉", "4시간봉"]
        )
        
        return indicator
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> TechnicalIndicator:
        """RSI 계산"""
        
        delta = data.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi_values = 100 - (100 / (1 + rs))
        
        # 신호 생성
        signals = []
        for i, rsi in enumerate(rsi_values):
            if pd.isna(rsi):
                signals.append(None)
                continue
            
            if rsi >= 70:
                signal = IndicatorSignal.OVERBOUGHT
            elif rsi <= 30:
                signal = IndicatorSignal.OVERSOLD
            elif rsi > 50 and (i == 0 or rsi_values.iloc[i-1] <= 50):
                signal = IndicatorSignal.BUY
            elif rsi < 50 and (i == 0 or rsi_values.iloc[i-1] >= 50):
                signal = IndicatorSignal.SELL
            else:
                signal = IndicatorSignal.HOLD
            
            signals.append(signal)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, (timestamp, value) in enumerate(rsi_values.items()):
            if not pd.isna(value):
                confidence = 0.8 if signals[i] in [IndicatorSignal.OVERBOUGHT, IndicatorSignal.OVERSOLD] else 0.6
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value=value,
                    signal=signals[i],
                    confidence=confidence,
                    metadata={'is_extreme': value >= 70 or value <= 30}
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.RSI,
            name=f"RSI({period})",
            description="상대강도지수 - 과매수/과매도 판단 지표",
            parameters={'period': period},
            values=indicator_values,
            interpretation_guide=[
                "70 이상: 과매수 구간 (매도 고려)",
                "30 이하: 과매도 구간 (매수 고려)",
                "50 상향돌파: 상승 모멘텀 강화",
                "50 하향돌파: 하락 모멘텀 강화",
                "다이버전스 발생 시 추세 전환 신호"
            ],
            common_mistakes=[
                "강한 추세에서 과매수/과매도 신호만으로 거래",
                "다이버전스 무시하고 단순 수치만 보기",
                "적절한 기간 설정 실패"
            ],
            best_timeframes=["일봉", "4시간봉", "1시간봉"]
        )
        
        return indicator
    
    def calculate_macd(self, data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> TechnicalIndicator:
        """MACD 계산"""
        
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        # 신호 생성
        signals = []
        for i in range(len(macd_line)):
            if i < slow:  # 충분한 데이터가 없는 경우
                signals.append(None)
                continue
            
            current_macd = macd_line.iloc[i]
            current_signal = signal_line.iloc[i]
            prev_macd = macd_line.iloc[i-1] if i > 0 else current_macd
            prev_signal = signal_line.iloc[i-1] if i > 0 else current_signal
            
            # 골든크로스/데드크로스 확인
            if current_macd > current_signal and prev_macd <= prev_signal:
                signal_type = IndicatorSignal.BUY
            elif current_macd < current_signal and prev_macd >= prev_signal:
                signal_type = IndicatorSignal.SELL
            else:
                signal_type = IndicatorSignal.HOLD
            
            signals.append(signal_type)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, timestamp in enumerate(macd_line.index):
            if i >= slow:  # 유효한 값만
                macd_val = macd_line.iloc[i]
                signal_val = signal_line.iloc[i]
                hist_val = histogram.iloc[i]
                
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value={
                        'macd': macd_val,
                        'signal': signal_val,
                        'histogram': hist_val
                    },
                    signal=signals[i],
                    confidence=0.7,
                    metadata={
                        'crossover': signals[i] in [IndicatorSignal.BUY, IndicatorSignal.SELL],
                        'above_zero': macd_val > 0
                    }
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.MACD,
            name=f"MACD({fast},{slow},{signal})",
            description="MACD - 추세와 모멘텀을 동시에 분석하는 지표",
            parameters={'fast': fast, 'slow': slow, 'signal': signal},
            values=indicator_values,
            interpretation_guide=[
                "MACD선이 신호선 상향돌파: 매수신호",
                "MACD선이 신호선 하향돌파: 매도신호",
                "MACD가 0선 위: 상승추세",
                "MACD가 0선 아래: 하락추세",
                "히스토그램의 방향 변화로 모멘텀 변화 감지"
            ],
            common_mistakes=[
                "횡보장에서 많은 거짓 신호",
                "다이버전스 패턴 무시",
                "히스토그램 신호 간과"
            ],
            best_timeframes=["일봉", "4시간봉"]
        )
        
        return indicator
    
    def calculate_bollinger_bands(self, data: pd.Series, period: int = 20, std_dev: float = 2.0) -> TechnicalIndicator:
        """볼린저 밴드 계산"""
        
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # 밴드폭 계산
        band_width = (upper_band - lower_band) / sma * 100
        
        # %B 계산 (현재가가 밴드 내에서 어느 위치인지)
        percent_b = (data - lower_band) / (upper_band - lower_band)
        
        # 신호 생성
        signals = []
        for i in range(len(data)):
            if i < period:
                signals.append(None)
                continue
            
            current_price = data.iloc[i]
            current_upper = upper_band.iloc[i]
            current_lower = lower_band.iloc[i]
            current_sma = sma.iloc[i]
            current_width = band_width.iloc[i]
            current_pb = percent_b.iloc[i]
            
            # 볼린저 밴드 신호 해석
            if current_price >= current_upper:
                signal = IndicatorSignal.OVERBOUGHT
            elif current_price <= current_lower:
                signal = IndicatorSignal.OVERSOLD
            elif current_width < 10:  # 밴드 수축 (스퀴즈)
                signal = IndicatorSignal.HOLD  # 돌파 대기
            elif current_price > current_sma and current_pb > 0.8:
                signal = IndicatorSignal.SELL  # 상단 접근
            elif current_price < current_sma and current_pb < 0.2:
                signal = IndicatorSignal.BUY   # 하단 접근
            else:
                signal = IndicatorSignal.HOLD
            
            signals.append(signal)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, timestamp in enumerate(data.index):
            if i >= period:
                price = data.iloc[i]
                upper = upper_band.iloc[i]
                lower = lower_band.iloc[i]
                middle = sma.iloc[i]
                width = band_width.iloc[i]
                pb = percent_b.iloc[i]
                
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value={
                        'upper': upper,
                        'middle': middle,
                        'lower': lower,
                        'width': width,
                        'percent_b': pb
                    },
                    signal=signals[i],
                    confidence=0.6,
                    metadata={
                        'squeeze': width < 10,
                        'expansion': width > 20,
                        'position': 'upper' if pb > 0.8 else 'lower' if pb < 0.2 else 'middle'
                    }
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.BOLLINGER_BANDS,
            name=f"볼린저밴드({period},{std_dev})",
            description="볼린저 밴드 - 변동성과 과매수/과매도 판단 지표",
            parameters={'period': period, 'std_dev': std_dev},
            values=indicator_values,
            interpretation_guide=[
                "상단밴드 터치: 과매수 (매도 고려)",
                "하단밴드 터치: 과매도 (매수 고려)",
                "밴드 폭 축소(스퀴즈): 변동성 확대 전조",
                "밴드 폭 확대: 강한 트렌드 지속",
                "%B > 1: 상단밴드 이탈 (강한 상승)",
                "%B < 0: 하단밴드 이탈 (강한 하락)"
            ],
            common_mistakes=[
                "트렌드 시장에서 역행 매매",
                "밴드 터치만으로 즉시 매매",
                "스퀴즈 이후 방향성 예측 실패"
            ],
            best_timeframes=["일봉", "4시간봉", "1시간봉"]
        )
        
        return indicator
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> TechnicalIndicator:
        """스토캐스틱 계산"""
        
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k_percent = ((close - lowest_low) / (highest_high - lowest_low)) * 100
        d_percent = k_percent.rolling(window=d_period).mean()
        
        # 신호 생성
        signals = []
        for i in range(len(k_percent)):
            if i < k_period:
                signals.append(None)
                continue
            
            current_k = k_percent.iloc[i]
            current_d = d_percent.iloc[i]
            prev_k = k_percent.iloc[i-1] if i > 0 else current_k
            prev_d = d_percent.iloc[i-1] if i > 0 else current_d
            
            # 스토캐스틱 신호 해석
            if current_k >= 80 and current_d >= 80:
                signal = IndicatorSignal.OVERBOUGHT
            elif current_k <= 20 and current_d <= 20:
                signal = IndicatorSignal.OVERSOLD
            elif current_k > current_d and prev_k <= prev_d and current_k < 80:
                signal = IndicatorSignal.BUY
            elif current_k < current_d and prev_k >= prev_d and current_k > 20:
                signal = IndicatorSignal.SELL
            else:
                signal = IndicatorSignal.HOLD
            
            signals.append(signal)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, timestamp in enumerate(close.index):
            if i >= k_period:
                k_val = k_percent.iloc[i]
                d_val = d_percent.iloc[i]
                
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value={
                        'k_percent': k_val,
                        'd_percent': d_val
                    },
                    signal=signals[i],
                    confidence=0.7,
                    metadata={
                        'extreme_level': k_val >= 80 or k_val <= 20,
                        'bullish_cross': signals[i] == IndicatorSignal.BUY,
                        'bearish_cross': signals[i] == IndicatorSignal.SELL
                    }
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.STOCHASTIC,
            name=f"스토캐스틱(%K{k_period},%D{d_period})",
            description="스토캐스틱 - 과매수/과매도와 모멘텀 변화 탐지 지표",
            parameters={'k_period': k_period, 'd_period': d_period},
            values=indicator_values,
            interpretation_guide=[
                "80 이상: 과매수 구간",
                "20 이하: 과매도 구간",
                "%K선이 %D선 상향돌파: 매수신호",
                "%K선이 %D선 하향돌파: 매도신호",
                "20 이하에서 상향돌파: 강한 매수신호",
                "80 이상에서 하향돌파: 강한 매도신호"
            ],
            common_mistakes=[
                "강한 트렌드에서 과매수/과매도만 보고 역행매매",
                "노이즈가 많은 단기 차트에서 사용",
                "다른 지표와의 조합 없이 단독 사용"
            ],
            best_timeframes=["일봉", "4시간봉"]
        )
        
        return indicator
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> TechnicalIndicator:
        """ATR (Average True Range) 계산"""
        
        # True Range 계산
        high_low = high - low
        high_close_prev = np.abs(high - close.shift(1))
        low_close_prev = np.abs(low - close.shift(1))
        
        true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr_values = true_range.rolling(window=period).mean()
        
        # ATR 기반 신호 생성 (변동성 해석)
        signals = []
        atr_sma = atr_values.rolling(window=period).mean()
        
        for i in range(len(atr_values)):
            if i < period * 2:
                signals.append(None)
                continue
            
            current_atr = atr_values.iloc[i]
            avg_atr = atr_sma.iloc[i]
            
            if current_atr > avg_atr * 1.5:
                signal = IndicatorSignal.BREAKOUT  # 높은 변동성
            elif current_atr < avg_atr * 0.7:
                signal = IndicatorSignal.HOLD      # 낮은 변동성 (돌파 대기)
            else:
                signal = IndicatorSignal.HOLD      # 보통 변동성
            
            signals.append(signal)
        
        # IndicatorValue 객체들 생성
        indicator_values = []
        for i, timestamp in enumerate(close.index):
            if i >= period:
                atr_val = atr_values.iloc[i]
                avg_atr_val = atr_sma.iloc[i] if i >= period * 2 else atr_val
                
                # 가격 대비 ATR 비율 계산
                atr_percentage = (atr_val / close.iloc[i]) * 100
                
                indicator_values.append(IndicatorValue(
                    timestamp=timestamp,
                    value=atr_val,
                    signal=signals[i],
                    confidence=0.5,
                    metadata={
                        'atr_percentage': atr_percentage,
                        'high_volatility': atr_val > avg_atr_val * 1.5 if i >= period * 2 else False,
                        'low_volatility': atr_val < avg_atr_val * 0.7 if i >= period * 2 else False
                    }
                ))
        
        indicator = TechnicalIndicator(
            indicator_type=IndicatorType.ATR,
            name=f"ATR({period})",
            description="Average True Range - 시장 변동성 측정 지표",
            parameters={'period': period},
            values=indicator_values,
            interpretation_guide=[
                "ATR 증가: 변동성 확대 (트렌드 강화 가능성)",
                "ATR 감소: 변동성 축소 (조정 또는 돌파 준비)",
                "손절선 설정에 활용 (현재가 ± ATR)",
                "포지션 크기 결정에 활용",
                "돌파 신호 확인용으로 사용"
            ],
            common_mistakes=[
                "ATR을 방향성 지표로 잘못 해석",
                "변동성만으로 매매 결정",
                "적절한 배수 설정 실패"
            ],
            best_timeframes=["일봉", "4시간봉", "1시간봉"]
        )
        
        return indicator
    
    def detect_divergence(self, price_data: pd.Series, indicator_data: pd.Series, 
                         lookback: int = 20) -> List[Dict[str, Any]]:
        """다이버전스 탐지"""
        divergences = []
        
        # 고점과 저점 찾기
        price_peaks = self._find_peaks(price_data, lookback)
        price_troughs = self._find_troughs(price_data, lookback)
        indicator_peaks = self._find_peaks(indicator_data, lookback)
        indicator_troughs = self._find_troughs(indicator_data, lookback)
        
        # 강세 다이버전스 (가격 저점 하락, 지표 저점 상승)
        for i in range(1, len(price_troughs)):
            price_trough1 = price_troughs[i-1]
            price_trough2 = price_troughs[i]
            
            # 해당 기간에 지표 저점 찾기
            indicator_trough1 = self._find_nearest_trough(indicator_troughs, price_trough1)
            indicator_trough2 = self._find_nearest_trough(indicator_troughs, price_trough2)
            
            if indicator_trough1 and indicator_trough2:
                price_lower = price_data.iloc[price_trough2] < price_data.iloc[price_trough1]
                indicator_higher = indicator_data.iloc[indicator_trough2] > indicator_data.iloc[indicator_trough1]
                
                if price_lower and indicator_higher:
                    divergences.append({
                        'type': 'bullish_divergence',
                        'start_time': price_data.index[price_trough1],
                        'end_time': price_data.index[price_trough2],
                        'confidence': 0.7,
                        'description': '강세 다이버전스: 가격은 하락하지만 지표는 상승'
                    })
        
        # 약세 다이버전스 (가격 고점 상승, 지표 고점 하락)
        for i in range(1, len(price_peaks)):
            price_peak1 = price_peaks[i-1]
            price_peak2 = price_peaks[i]
            
            indicator_peak1 = self._find_nearest_peak(indicator_peaks, price_peak1)
            indicator_peak2 = self._find_nearest_peak(indicator_peaks, price_peak2)
            
            if indicator_peak1 and indicator_peak2:
                price_higher = price_data.iloc[price_peak2] > price_data.iloc[price_peak1]
                indicator_lower = indicator_data.iloc[indicator_peak2] < indicator_data.iloc[indicator_peak1]
                
                if price_higher and indicator_lower:
                    divergences.append({
                        'type': 'bearish_divergence',
                        'start_time': price_data.index[price_peak1],
                        'end_time': price_data.index[price_peak2],
                        'confidence': 0.7,
                        'description': '약세 다이버전스: 가격은 상승하지만 지표는 하락'
                    })
        
        return divergences
    
    def _find_peaks(self, data: pd.Series, lookback: int) -> List[int]:
        """고점 찾기"""
        peaks = []
        for i in range(lookback, len(data) - lookback):
            if data.iloc[i] == data.iloc[i-lookback:i+lookback+1].max():
                peaks.append(i)
        return peaks
    
    def _find_troughs(self, data: pd.Series, lookback: int) -> List[int]:
        """저점 찾기"""
        troughs = []
        for i in range(lookback, len(data) - lookback):
            if data.iloc[i] == data.iloc[i-lookback:i+lookback+1].min():
                troughs.append(i)
        return troughs
    
    def _find_nearest_peak(self, peaks: List[int], target: int, tolerance: int = 5) -> Optional[int]:
        """가장 가까운 고점 찾기"""
        nearest = None
        min_distance = float('inf')
        
        for peak in peaks:
            distance = abs(peak - target)
            if distance <= tolerance and distance < min_distance:
                min_distance = distance
                nearest = peak
        
        return nearest
    
    def _find_nearest_trough(self, troughs: List[int], target: int, tolerance: int = 5) -> Optional[int]:
        """가장 가까운 저점 찾기"""
        nearest = None
        min_distance = float('inf')
        
        for trough in troughs:
            distance = abs(trough - target)
            if distance <= tolerance and distance < min_distance:
                min_distance = distance
                nearest = trough
        
        return nearest


class IndicatorLibrary:
    """기술적 지표 라이브러리"""
    
    def __init__(self):
        self.calculator = IndicatorCalculator()
        self.indicator_definitions = self._initialize_definitions()
    
    def _initialize_definitions(self) -> Dict[IndicatorType, Dict[str, Any]]:
        """지표 정의 초기화"""
        
        definitions = {
            IndicatorType.RSI: {
                'name': 'RSI (Relative Strength Index)',
                'category': 'momentum',
                'default_period': 14,
                'range': (0, 100),
                'overbought_level': 70,
                'oversold_level': 30,
                'best_for': ['reversal_signals', 'divergence_analysis'],
                'difficulty': 'beginner',
                'reliability': 0.7
            },
            
            IndicatorType.MACD: {
                'name': 'MACD (Moving Average Convergence Divergence)',
                'category': 'trend_momentum',
                'default_params': {'fast': 12, 'slow': 26, 'signal': 9},
                'best_for': ['trend_following', 'momentum_analysis'],
                'difficulty': 'intermediate',
                'reliability': 0.75
            },
            
            IndicatorType.BOLLINGER_BANDS: {
                'name': 'Bollinger Bands',
                'category': 'volatility',
                'default_params': {'period': 20, 'std_dev': 2.0},
                'best_for': ['volatility_analysis', 'mean_reversion'],
                'difficulty': 'intermediate',
                'reliability': 0.65
            },
            
            IndicatorType.STOCHASTIC: {
                'name': 'Stochastic Oscillator',
                'category': 'momentum',
                'default_params': {'k_period': 14, 'd_period': 3},
                'range': (0, 100),
                'overbought_level': 80,
                'oversold_level': 20,
                'best_for': ['short_term_reversal', 'momentum_confirmation'],
                'difficulty': 'intermediate',
                'reliability': 0.6
            },
            
            IndicatorType.MOVING_AVERAGE: {
                'name': 'Moving Average',
                'category': 'trend',
                'default_period': 20,
                'best_for': ['trend_identification', 'support_resistance'],
                'difficulty': 'beginner',
                'reliability': 0.8
            },
            
            IndicatorType.ATR: {
                'name': 'Average True Range',
                'category': 'volatility',
                'default_period': 14,
                'best_for': ['volatility_measurement', 'stop_loss_setting'],
                'difficulty': 'advanced',
                'reliability': 0.9
            }
        }
        
        return definitions
    
    def get_indicator_info(self, indicator_type: IndicatorType) -> Dict[str, Any]:
        """지표 정보 반환"""
        return self.indicator_definitions.get(indicator_type, {})
    
    def get_beginner_indicators(self) -> List[IndicatorType]:
        """초보자용 지표 목록"""
        return [
            indicator_type for indicator_type, info in self.indicator_definitions.items()
            if info.get('difficulty') == 'beginner'
        ]
    
    def get_indicators_by_category(self, category: str) -> List[IndicatorType]:
        """카테고리별 지표 목록"""
        return [
            indicator_type for indicator_type, info in self.indicator_definitions.items()
            if category in info.get('category', '')
        ]
    
    def create_indicator_combination(self, combination_type: str) -> List[IndicatorType]:
        """지표 조합 추천"""
        
        combinations = {
            'trend_following': [
                IndicatorType.MOVING_AVERAGE,
                IndicatorType.MACD,
                IndicatorType.ATR
            ],
            'mean_reversion': [
                IndicatorType.RSI,
                IndicatorType.BOLLINGER_BANDS,
                IndicatorType.STOCHASTIC
            ],
            'momentum_analysis': [
                IndicatorType.RSI,
                IndicatorType.MACD,
                IndicatorType.STOCHASTIC
            ],
            'volatility_analysis': [
                IndicatorType.BOLLINGER_BANDS,
                IndicatorType.ATR
            ],
            'complete_analysis': [
                IndicatorType.MOVING_AVERAGE,
                IndicatorType.RSI,
                IndicatorType.MACD,
                IndicatorType.BOLLINGER_BANDS
            ]
        }
        
        return combinations.get(combination_type, [])
    
    def calculate_indicator_correlation(self, indicators: List[TechnicalIndicator]) -> Dict[str, float]:
        """지표 간 상관관계 계산"""
        correlations = {}
        
        # 모든 지표 쌍에 대해 상관관계 계산
        for i, indicator1 in enumerate(indicators):
            for j, indicator2 in enumerate(indicators[i+1:], i+1):
                
                # 공통 시간대의 값들 추출
                common_values1 = []
                common_values2 = []
                
                for value1 in indicator1.values:
                    value2 = indicator2.get_value_at_time(value1.timestamp)
                    if value2:
                        # 복합 값인 경우 첫 번째 값 사용
                        val1 = value1.value if isinstance(value1.value, (int, float)) else list(value1.value.values())[0]
                        val2 = value2.value if isinstance(value2.value, (int, float)) else list(value2.value.values())[0]
                        
                        common_values1.append(val1)
                        common_values2.append(val2)
                
                if len(common_values1) > 10:  # 충분한 데이터가 있는 경우
                    correlation = np.corrcoef(common_values1, common_values2)[0, 1]
                    correlations[f"{indicator1.name}_vs_{indicator2.name}"] = correlation
        
        return correlations