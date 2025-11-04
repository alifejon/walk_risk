"""Market Event Detector - 실시간 시장 이벤트 감지 및 퍼즐 트리거"""

import asyncio
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random

from .yahoo_finance import YahooFinanceConnector, StockData, MarketSummary
from ...core.risk_puzzle.puzzle_engine import PuzzleEngine, PuzzleDifficulty, PuzzleType
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class EventType(Enum):
    """시장 이벤트 타입"""
    SHARP_DROP = "sharp_drop"           # 급락 (-5% 이상)
    SHARP_RISE = "sharp_rise"           # 급등 (+5% 이상)
    HIGH_VOLUME = "high_volume"         # 거래량 급증 (평균의 3배 이상)
    VOLATILITY_SPIKE = "volatility"     # 변동성 급증
    SECTOR_DIVERGENCE = "divergence"    # 섹터 대비 이상 움직임
    EARNINGS_REACTION = "earnings"      # 실적 발표 반응
    NEWS_DRIVEN = "news_driven"         # 뉴스 기반 움직임


@dataclass
class MarketEvent:
    """감지된 시장 이벤트"""
    event_id: str
    event_type: EventType
    symbol: str
    company_name: str
    
    # 이벤트 데이터
    trigger_price: float
    change_percent: float
    volume_ratio: float  # 평균 대비 거래량 비율
    
    # 시장 컨텍스트
    market_sentiment: str
    sector_performance: Dict[str, float]
    peer_comparison: Dict[str, float]
    
    # 메타데이터
    detected_at: datetime = field(default_factory=datetime.now)
    severity: str = "medium"  # low, medium, high, critical
    puzzle_worthiness: float = 0.0  # 0.0~1.0 퍼즐 적합도
    
    def to_puzzle_data(self) -> Dict[str, Any]:
        """퍼즐 생성용 데이터로 변환"""
        return {
            'symbol': self.symbol,
            'change_percent': self.change_percent,
            'volume_ratio': self.volume_ratio,
            'market_sentiment': self.market_sentiment,
            'time': self.detected_at.strftime('%H:%M'),
            'sector_divergence': self._has_sector_divergence(),
            'event_type': self.event_type.value,
            'severity': self.severity
        }
    
    def _has_sector_divergence(self) -> bool:
        """섹터 대비 이상 움직임 여부"""
        if not self.peer_comparison:
            return False
        
        # 동종업계 평균과 3%p 이상 차이나면 divergence
        peer_avg = statistics.mean(self.peer_comparison.values())
        return abs(self.change_percent - peer_avg) > 3.0


class MarketEventDetector:
    """실시간 시장 이벤트 감지기"""
    
    def __init__(self):
        self.yahoo_api = YahooFinanceConnector()
        self.puzzle_engine = PuzzleEngine()
        
        # 감지 설정
        self.detection_thresholds = {
            'sharp_movement': 5.0,     # ±5% 이상
            'volume_multiplier': 2.5,  # 평균의 2.5배 이상
            'volatility_threshold': 30, # 일일 변동성 30% 이상
        }
        
        # 모니터링 대상 주식들
        self.watch_list = self._get_watch_list()
        
        # 이벤트 히스토리 (중복 방지용)
        self.recent_events: List[MarketEvent] = []
        self.event_cooldown = timedelta(hours=1)  # 같은 종목 1시간 쿨다운
        
    def _get_watch_list(self) -> List[str]:
        """모니터링 대상 주식 리스트"""
        return [
            # 대형주
            "005930.KS",  # 삼성전자
            "000660.KS",  # SK하이닉스
            "035420.KS",  # NAVER
            "051910.KS",  # LG화학
            "006400.KS",  # 삼성SDI
            "207940.KS",  # 삼성바이오로직스
            "005380.KS",  # 현대차
            "000270.KS",  # 기아
            "068270.KS",  # 셀트리온
            "003670.KS",  # 포스코홀딩스
            
            # 중형주 (변동성 높음)
            "035720.KS",  # 카카오
            "096770.KS",  # SK이노베이션
            "034730.KS",  # SK
            "017670.KS",  # SK텔레콤
            "030200.KS",  # KT
        ]
    
    async def detect_events(self) -> List[MarketEvent]:
        """실시간 이벤트 감지"""
        detected_events = []
        
        logger.info(f"시장 이벤트 감지 시작: {len(self.watch_list)}개 종목 모니터링")
        
        # 병렬로 모든 종목 체크
        tasks = [self._check_stock_for_events(symbol) for symbol in self.watch_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, MarketEvent):
                # 중복 이벤트 필터링
                if not self._is_duplicate_event(result):
                    detected_events.append(result)
                    self.recent_events.append(result)
                    logger.info(f"새 이벤트 감지: {result.symbol} - {result.event_type.value}")
            elif isinstance(result, Exception):
                logger.warning(f"이벤트 감지 중 오류: {result}")
        
        # 오래된 이벤트 정리
        self._cleanup_old_events()
        
        # 퍼즐 적합도 순으로 정렬
        detected_events.sort(key=lambda e: e.puzzle_worthiness, reverse=True)
        
        logger.info(f"총 {len(detected_events)}개 이벤트 감지 완료")
        return detected_events
    
    async def _check_stock_for_events(self, symbol: str) -> Optional[MarketEvent]:
        """개별 종목 이벤트 체크"""
        try:
            # 현재 주식 데이터 가져오기
            stock_data = await self.yahoo_api.get_stock_data(symbol)
            if not stock_data:
                return None
            
            # 거래량 히스토리 (평균 계산용)
            volume_history = await self._get_volume_history(symbol)
            if not volume_history:
                return None
            
            avg_volume = statistics.mean(volume_history)
            volume_ratio = stock_data.volume / avg_volume if avg_volume > 0 else 1.0
            
            # 이벤트 감지 조건들 체크
            events = []
            
            # 1. 급락/급등 체크
            if abs(stock_data.change_percent) >= self.detection_thresholds['sharp_movement']:
                event_type = EventType.SHARP_DROP if stock_data.change_percent < 0 else EventType.SHARP_RISE
                events.append((event_type, abs(stock_data.change_percent) / 10.0))  # 적합도: 변동률/10
            
            # 2. 거래량 급증 체크
            if volume_ratio >= self.detection_thresholds['volume_multiplier']:
                events.append((EventType.HIGH_VOLUME, min(volume_ratio / 5.0, 1.0)))  # 적합도: 비율/5 (최대 1.0)
            
            # 3. 복합 이벤트 (급락+거래량 급증 = 높은 적합도)
            if (abs(stock_data.change_percent) >= 3.0 and 
                volume_ratio >= 2.0):
                puzzle_worthiness = min(
                    (abs(stock_data.change_percent) / 5.0) * (volume_ratio / 3.0),
                    1.0
                )
                
                # 가장 적합한 이벤트만 선택
                if events:
                    best_event = max(events, key=lambda x: x[1])
                    event_type = best_event[0]
                else:
                    event_type = EventType.SHARP_DROP if stock_data.change_percent < 0 else EventType.SHARP_RISE
                
                # 시장 컨텍스트 수집
                market_context = await self._gather_market_context(symbol, stock_data)
                
                # 이벤트 생성
                event = MarketEvent(
                    event_id=f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}",
                    event_type=event_type,
                    symbol=symbol,
                    company_name=stock_data.name,
                    trigger_price=stock_data.current_price,
                    change_percent=stock_data.change_percent,
                    volume_ratio=volume_ratio,
                    market_sentiment=market_context['sentiment'],
                    sector_performance=market_context.get('sector', {}),
                    peer_comparison=market_context.get('peers', {}),
                    severity=self._calculate_severity(stock_data.change_percent, volume_ratio),
                    puzzle_worthiness=puzzle_worthiness
                )
                
                return event
            
            return None
            
        except Exception as e:
            logger.error(f"종목 {symbol} 이벤트 체크 오류: {e}")
            return None
    
    async def _get_volume_history(self, symbol: str, days: int = 20) -> List[int]:
        """거래량 히스토리 조회 (평균 계산용)"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{days}d")
            
            if hist.empty:
                return []
            
            return hist['Volume'].tolist()[-days:]  # 최근 N일
            
        except Exception as e:
            logger.warning(f"거래량 히스토리 조회 실패 {symbol}: {e}")
            return []
    
    async def _gather_market_context(self, symbol: str, stock_data: StockData) -> Dict[str, Any]:
        """시장 컨텍스트 정보 수집"""
        context = {
            'sentiment': 'neutral',
            'sector': {},
            'peers': {}
        }
        
        try:
            # 시장 전체 상황
            market_summary = await self.yahoo_api.get_market_summary()
            if market_summary:
                kospi_change = market_summary.kospi_change_percent
                kosdaq_change = market_summary.kosdaq_change_percent
                
                if kospi_change < -2 or kosdaq_change < -2:
                    context['sentiment'] = 'bearish'
                elif kospi_change > 2 or kosdaq_change > 2:
                    context['sentiment'] = 'bullish'
                else:
                    context['sentiment'] = 'neutral'
            
            # 동종업계 비교 (간단 버전)
            sector_symbols = self._get_sector_peers(symbol)
            if sector_symbols:
                peer_data = await self.yahoo_api.get_multiple_stocks(sector_symbols[:3])  # 최대 3개
                context['peers'] = {
                    sym: data.change_percent 
                    for sym, data in peer_data.items() 
                    if data
                }
        
        except Exception as e:
            logger.warning(f"시장 컨텍스트 수집 오류: {e}")
        
        return context
    
    def _get_sector_peers(self, symbol: str) -> List[str]:
        """동종업계 심볼 반환 (간단 매핑)"""
        sector_map = {
            # 반도체
            "005930.KS": ["000660.KS", "006400.KS"],  # 삼성전자 -> SK하이닉스, 삼성SDI
            "000660.KS": ["005930.KS", "006400.KS"],  # SK하이닉스 -> 삼성전자, 삼성SDI
            
            # IT 서비스
            "035420.KS": ["035720.KS"],  # NAVER -> 카카오
            "035720.KS": ["035420.KS"],  # 카카오 -> NAVER
            
            # 자동차
            "005380.KS": ["000270.KS"],  # 현대차 -> 기아
            "000270.KS": ["005380.KS"],  # 기아 -> 현대차
            
            # 바이오
            "068270.KS": ["207940.KS"],  # 셀트리온 -> 삼성바이오로직스
            "207940.KS": ["068270.KS"],  # 삼성바이오로직스 -> 셀트리온
        }
        
        return sector_map.get(symbol, [])
    
    def _calculate_severity(self, change_percent: float, volume_ratio: float) -> str:
        """이벤트 심각도 계산"""
        abs_change = abs(change_percent)
        
        if abs_change >= 10 or volume_ratio >= 5:
            return "critical"
        elif abs_change >= 7 or volume_ratio >= 3:
            return "high"
        elif abs_change >= 5 or volume_ratio >= 2:
            return "medium"
        else:
            return "low"
    
    def _is_duplicate_event(self, new_event: MarketEvent) -> bool:
        """중복 이벤트 체크"""
        cutoff_time = datetime.now() - self.event_cooldown
        
        for existing_event in self.recent_events:
            if (existing_event.symbol == new_event.symbol and
                existing_event.detected_at > cutoff_time and
                existing_event.event_type == new_event.event_type):
                return True
        
        return False
    
    def _cleanup_old_events(self):
        """오래된 이벤트 정리"""
        cutoff_time = datetime.now() - timedelta(hours=24)  # 24시간 이전 이벤트 삭제
        self.recent_events = [
            event for event in self.recent_events 
            if event.detected_at > cutoff_time
        ]
    
    async def create_puzzle_from_event(self, event: MarketEvent) -> Optional[Any]:
        """이벤트로부터 퍼즐 생성"""
        try:
            # 이벤트 타입에 따른 난이도 결정
            difficulty_map = {
                "critical": PuzzleDifficulty.MASTER,
                "high": PuzzleDifficulty.ADVANCED,
                "medium": PuzzleDifficulty.INTERMEDIATE,
                "low": PuzzleDifficulty.BEGINNER
            }
            
            difficulty = difficulty_map.get(event.severity, PuzzleDifficulty.INTERMEDIATE)
            
            # 퍼즐 생성
            puzzle = self.puzzle_engine.create_puzzle(
                symbol=event.company_name,
                market_event=event.to_puzzle_data(),
                difficulty=difficulty
            )
            
            # 실제 이벤트 데이터로 퍼즐 커스터마이징
            puzzle.title = f"🔥 실시간: {event.company_name} {event.change_percent:+.1f}% 미스터리"
            puzzle.description = f"""
🚨 [실시간 이벤트]

📊 상황: {event.company_name}이(가) {event.change_percent:+.1f}% 변동했습니다.
📈 거래량: 평소 대비 {event.volume_ratio:.1f}배
🌍 시장: {event.market_sentiment}
⏰ 감지 시간: {event.detected_at.strftime('%H:%M:%S')}
🔥 심각도: {event.severity.upper()}

무엇이 이 움직임을 만들었을까요?
실시간 데이터를 분석하고 진실을 찾아보세요!
            """.strip()
            
            logger.info(f"실시간 퍼즐 생성: {puzzle.title}")
            return puzzle
            
        except Exception as e:
            logger.error(f"퍼즐 생성 오류: {e}")
            return None


# 전역 인스턴스
market_event_detector = MarketEventDetector()