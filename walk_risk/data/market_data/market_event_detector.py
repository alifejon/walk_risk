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
            # 대형주 - 시가총액 상위
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

            # IT/플랫폼
            "035720.KS",  # 카카오
            "263750.KS",  # 펄어비스
            "036570.KS",  # 엔씨소프트
            "251270.KS",  # 넷마블

            # 2차전지/신에너지
            "373220.KS",  # LG에너지솔루션
            "247540.KS",  # 에코프로비엠
            "086520.KS",  # 에코프로

            # 통신
            "096770.KS",  # SK이노베이션
            "034730.KS",  # SK
            "017670.KS",  # SK텔레콤
            "030200.KS",  # KT

            # 금융
            "105560.KS",  # KB금융
            "055550.KS",  # 신한지주
            "086790.KS",  # 하나금융지주

            # 바이오/제약
            "091990.KS",  # 셀트리온헬스케어
            "326030.KS",  # SK바이오팜
            "145020.KS",  # 휴젤

            # 엔터테인먼트
            "352820.KS",  # 하이브
            "041510.KS",  # SM
            "122870.KS",  # YG엔터테인먼트
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


    def generate_mock_events(self, count: int = 3) -> List[MarketEvent]:
        """API 실패 시 사용할 모의 이벤트 생성 (학습용)"""
        mock_scenarios = [
            {
                "symbol": "삼성전자",
                "event_type": EventType.SHARP_DROP,
                "change_percent": -6.2,
                "volume_ratio": 2.8,
                "sentiment": "bearish",
                "severity": "high",
                "reason": "반도체 업황 우려"
            },
            {
                "symbol": "NAVER",
                "event_type": EventType.SHARP_RISE,
                "change_percent": 7.5,
                "volume_ratio": 3.2,
                "sentiment": "bullish",
                "severity": "high",
                "reason": "AI 사업 성과 기대"
            },
            {
                "symbol": "에코프로",
                "event_type": EventType.VOLATILITY_SPIKE,
                "change_percent": 4.2,
                "volume_ratio": 5.1,
                "sentiment": "neutral",
                "severity": "medium",
                "reason": "2차전지 테마 급등락"
            },
            {
                "symbol": "카카오",
                "event_type": EventType.SECTOR_DIVERGENCE,
                "change_percent": -4.8,
                "volume_ratio": 1.9,
                "sentiment": "bearish",
                "severity": "medium",
                "reason": "플랫폼 규제 우려"
            },
            {
                "symbol": "하이브",
                "event_type": EventType.SHARP_RISE,
                "change_percent": 8.3,
                "volume_ratio": 4.5,
                "sentiment": "bullish",
                "severity": "high",
                "reason": "아티스트 컴백 효과"
            },
            {
                "symbol": "LG에너지솔루션",
                "event_type": EventType.SHARP_DROP,
                "change_percent": -5.5,
                "volume_ratio": 2.1,
                "sentiment": "bearish",
                "severity": "medium",
                "reason": "전기차 수요 둔화 우려"
            },
            {
                "symbol": "SK하이닉스",
                "event_type": EventType.SHARP_RISE,
                "change_percent": 6.8,
                "volume_ratio": 2.9,
                "sentiment": "bullish",
                "severity": "high",
                "reason": "HBM 수요 급증 기대"
            },
            {
                "symbol": "셀트리온",
                "event_type": EventType.NEWS_DRIVEN,
                "change_percent": 5.2,
                "volume_ratio": 3.7,
                "sentiment": "bullish",
                "severity": "medium",
                "reason": "FDA 승인 기대감"
            }
        ]

        # 랜덤하게 선택
        selected = random.sample(mock_scenarios, min(count, len(mock_scenarios)))

        events = []
        for scenario in selected:
            event = MarketEvent(
                event_id=f"mock_{scenario['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                event_type=scenario["event_type"],
                symbol=scenario["symbol"],
                company_name=scenario["symbol"],
                trigger_price=50000 + random.randint(-10000, 30000),  # 모의 가격
                change_percent=scenario["change_percent"],
                volume_ratio=scenario["volume_ratio"],
                market_sentiment=scenario["sentiment"],
                sector_performance={},
                peer_comparison={},
                severity=scenario["severity"],
                puzzle_worthiness=random.uniform(0.6, 0.95)
            )
            events.append(event)

        logger.info(f"모의 이벤트 {len(events)}개 생성 완료")
        return events

    async def get_puzzle_ready_events(self, max_count: int = 5, use_fallback: bool = True) -> List[MarketEvent]:
        """퍼즐로 변환 가능한 이벤트 가져오기 (편의 메서드)

        Args:
            max_count: 최대 이벤트 수
            use_fallback: API 실패 시 모의 데이터 사용 여부

        Returns:
            퍼즐 적합도 순으로 정렬된 이벤트 리스트
        """
        try:
            events = await self.detect_events()

            if events:
                # 퍼즐 적합도 0.5 이상인 이벤트만 필터링
                qualified_events = [e for e in events if e.puzzle_worthiness >= 0.5]
                return qualified_events[:max_count]

            # 이벤트가 없으면 폴백
            if use_fallback:
                logger.info("실시간 이벤트 없음, 모의 이벤트로 대체")
                return self.generate_mock_events(max_count)

            return []

        except Exception as e:
            logger.error(f"이벤트 감지 실패: {e}")
            if use_fallback:
                logger.info("API 오류로 모의 이벤트 사용")
                return self.generate_mock_events(max_count)
            return []

    async def create_instant_puzzle(self, difficulty: PuzzleDifficulty = PuzzleDifficulty.INTERMEDIATE):
        """즉시 실행 가능한 퍼즐 생성 (원클릭 퍼즐)

        실시간 데이터 또는 모의 데이터를 사용해 바로 플레이 가능한 퍼즐 반환
        """
        events = await self.get_puzzle_ready_events(max_count=1, use_fallback=True)

        if not events:
            # 기본 이벤트 생성
            default_event = MarketEvent(
                event_id=f"default_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                event_type=EventType.SHARP_DROP,
                symbol="삼성전자",
                company_name="삼성전자",
                trigger_price=65000,
                change_percent=-5.5,
                volume_ratio=2.3,
                market_sentiment="bearish",
                sector_performance={},
                peer_comparison={},
                severity="medium",
                puzzle_worthiness=0.7
            )
            events = [default_event]

        # 첫 번째 이벤트로 퍼즐 생성
        puzzle = await self.create_puzzle_from_event(events[0])
        return puzzle

    def get_available_stock_names(self) -> Dict[str, str]:
        """사용 가능한 주식 목록과 이름 반환"""
        stock_names = {
            "005930.KS": "삼성전자",
            "000660.KS": "SK하이닉스",
            "035420.KS": "NAVER",
            "051910.KS": "LG화학",
            "006400.KS": "삼성SDI",
            "207940.KS": "삼성바이오로직스",
            "005380.KS": "현대차",
            "000270.KS": "기아",
            "068270.KS": "셀트리온",
            "003670.KS": "포스코홀딩스",
            "035720.KS": "카카오",
            "263750.KS": "펄어비스",
            "036570.KS": "엔씨소프트",
            "251270.KS": "넷마블",
            "373220.KS": "LG에너지솔루션",
            "247540.KS": "에코프로비엠",
            "086520.KS": "에코프로",
            "096770.KS": "SK이노베이션",
            "034730.KS": "SK",
            "017670.KS": "SK텔레콤",
            "030200.KS": "KT",
            "105560.KS": "KB금융",
            "055550.KS": "신한지주",
            "086790.KS": "하나금융지주",
            "091990.KS": "셀트리온헬스케어",
            "326030.KS": "SK바이오팜",
            "145020.KS": "휴젤",
            "352820.KS": "하이브",
            "041510.KS": "SM",
            "122870.KS": "YG엔터테인먼트"
        }
        return stock_names


# 전역 인스턴스
market_event_detector = MarketEventDetector()


# 편의 함수
async def get_realtime_puzzle(difficulty: PuzzleDifficulty = PuzzleDifficulty.INTERMEDIATE):
    """실시간 퍼즐을 간단히 가져오는 함수"""
    return await market_event_detector.create_instant_puzzle(difficulty)


async def get_available_events(max_count: int = 5):
    """사용 가능한 이벤트 목록 가져오기"""
    return await market_event_detector.get_puzzle_ready_events(max_count)