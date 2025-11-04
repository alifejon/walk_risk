"""Market Service - 시장 데이터 서비스"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

from .base import BaseService


class MarketService(BaseService):
    """시장 데이터 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        super().__init__()

        # 종목 정보 캐시
        self.symbols_cache: Dict[str, Dict[str, Any]] = {}

        # 시세 정보 캐시 (1분간 유효)
        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timeout = 60  # 60초

    async def _setup(self):
        """서비스 초기화"""
        # 기본 종목 데이터 로드
        await self._load_default_symbols()
        self.logger.info("MarketService setup completed")

    async def _load_default_symbols(self):
        """기본 종목 정보 로드"""
        default_symbols = [
            {
                "symbol": "005930.KS",
                "name": "삼성전자",
                "market": "KRX",
                "sector": "Technology",
                "is_tradable": True
            },
            {
                "symbol": "000660.KS",
                "name": "SK하이닉스",
                "market": "KRX",
                "sector": "Technology",
                "is_tradable": True
            },
            {
                "symbol": "035420.KS",
                "name": "NAVER",
                "market": "KRX",
                "sector": "Technology",
                "is_tradable": True
            },
            {
                "symbol": "051910.KS",
                "name": "LG화학",
                "market": "KRX",
                "sector": "Materials",
                "is_tradable": True
            },
            {
                "symbol": "207940.KS",
                "name": "삼성바이오로직스",
                "market": "KRX",
                "sector": "Healthcare",
                "is_tradable": True
            },
            {
                "symbol": "006400.KS",
                "name": "삼성SDI",
                "market": "KRX",
                "sector": "Technology",
                "is_tradable": True
            },
            {
                "symbol": "028260.KS",
                "name": "삼성물산",
                "market": "KRX",
                "sector": "Industrial",
                "is_tradable": True
            },
            {
                "symbol": "068270.KS",
                "name": "셀트리온",
                "market": "KRX",
                "sector": "Healthcare",
                "is_tradable": True
            }
        ]

        for symbol_info in default_symbols:
            self.symbols_cache[symbol_info["symbol"]] = symbol_info

    async def search_symbols(
        self,
        search_query: Optional[str] = None,
        market: Optional[str] = None,
        sector: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """종목 검색"""
        try:
            self._validate_initialized()

            symbols = list(self.symbols_cache.values())

            # 검색 필터링
            if search_query:
                search_query = search_query.lower()
                symbols = [
                    s for s in symbols
                    if search_query in s["name"].lower() or search_query in s["symbol"].lower()
                ]

            if market:
                symbols = [s for s in symbols if s["market"] == market]

            if sector:
                symbols = [s for s in symbols if s["sector"] == sector]

            # 결과 제한
            symbols = symbols[:limit]

            return self._create_response(
                success=True,
                data={"symbols": symbols}
            )

        except Exception as e:
            return self._handle_error(e, "search_symbols")

    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """실시간 시세 조회"""
        try:
            self._validate_initialized()

            # 캐시 확인
            cached_quote = self._get_cached_quote(symbol)
            if cached_quote:
                return self._create_response(
                    success=True,
                    data=cached_quote
                )

            # 종목 정보 확인
            if symbol not in self.symbols_cache:
                return self._create_response(
                    success=False,
                    message="Symbol not found",
                    error_code="SYMBOL_NOT_FOUND"
                )

            symbol_info = self.symbols_cache[symbol]

            # 실시간 시세 조회 (모의 구현)
            quote_data = await self._fetch_real_time_quote(symbol, symbol_info)

            # 캐시에 저장
            self._cache_quote(symbol, quote_data)

            return self._create_response(
                success=True,
                data=quote_data
            )

        except Exception as e:
            return self._handle_error(e, "get_quote")

    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """다중 종목 시세 조회"""
        try:
            self._validate_initialized()

            quotes = {}
            failed_symbols = []

            # 병렬로 시세 조회
            tasks = []
            for symbol in symbols:
                task = self.get_quote(symbol)
                tasks.append((symbol, task))

            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            for (symbol, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    failed_symbols.append(symbol)
                elif result.get("success"):
                    quotes[symbol] = result["data"]
                else:
                    failed_symbols.append(symbol)

            return self._create_response(
                success=True,
                data={
                    "quotes": quotes,
                    "failed_symbols": failed_symbols,
                    "success_count": len(quotes),
                    "total_requested": len(symbols)
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_multiple_quotes")

    async def get_market_overview(self) -> Dict[str, Any]:
        """시장 개요 조회"""
        try:
            self._validate_initialized()

            # 주요 지수 정보 (모의 구현)
            indices = {
                "KOSPI": {
                    "value": 2850.5,
                    "change": -15.2,
                    "change_percent": -0.53,
                    "volume": 450000000
                },
                "KOSDAQ": {
                    "value": 915.8,
                    "change": +8.3,
                    "change_percent": +0.92,
                    "volume": 680000000
                }
            }

            # 활성 종목들
            active_symbols = ["005930.KS", "000660.KS", "035420.KS"]
            active_stocks = []

            for symbol in active_symbols:
                quote_result = await self.get_quote(symbol)
                if quote_result.get("success"):
                    active_stocks.append(quote_result["data"])

            # 섹터별 성과
            sector_performance = {
                "Technology": {"change_percent": -1.2, "volume": 1200000000},
                "Healthcare": {"change_percent": +2.1, "volume": 350000000},
                "Materials": {"change_percent": -0.8, "volume": 280000000},
                "Industrial": {"change_percent": +0.5, "volume": 150000000}
            }

            return self._create_response(
                success=True,
                data={
                    "indices": indices,
                    "active_stocks": active_stocks,
                    "sector_performance": sector_performance,
                    "market_status": self._get_market_status(),
                    "last_updated": datetime.now().isoformat()
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_market_overview")

    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1M",
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """과거 데이터 조회"""
        try:
            self._validate_initialized()

            if symbol not in self.symbols_cache:
                return self._create_response(
                    success=False,
                    message="Symbol not found",
                    error_code="SYMBOL_NOT_FOUND"
                )

            # 기간 파싱
            days = self._parse_period(period)
            start_date = datetime.now() - timedelta(days=days)

            # 모의 과거 데이터 생성
            historical_data = await self._generate_mock_historical_data(
                symbol, start_date, interval
            )

            return self._create_response(
                success=True,
                data={
                    "symbol": symbol,
                    "period": period,
                    "interval": interval,
                    "data": historical_data
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_historical_data")

    async def _fetch_real_time_quote(self, symbol: str, symbol_info: Dict[str, Any]) -> Dict[str, Any]:
        """실시간 시세 조회 (모의 구현)"""
        # TODO: 실제 Yahoo Finance API 또는 KRX API 연동

        # 모의 시세 데이터
        base_prices = {
            "005930.KS": 75000,
            "000660.KS": 95000,
            "035420.KS": 180000,
            "051910.KS": 420000,
            "207940.KS": 820000,
            "006400.KS": 650000,
            "028260.KS": 120000,
            "068270.KS": 180000
        }

        base_price = base_prices.get(symbol, 10000)

        # 랜덤 변동 적용 (-5% ~ +5%)
        import random
        change_percent = random.uniform(-5.0, 5.0)
        change = base_price * (change_percent / 100)
        current_price = base_price + change

        # 거래량 생성
        volume = random.randint(100000, 50000000)

        # 시가총액 계산 (대략적)
        market_cap = current_price * 100000000  # 1억주 가정

        return {
            "symbol": symbol,
            "name": symbol_info["name"],
            "current_price": round(current_price),
            "change": round(change),
            "change_percent": round(change_percent, 2),
            "volume": volume,
            "market_cap": market_cap,
            "last_updated": datetime.now().isoformat(),
            "trading_session": self._get_trading_session()
        }

    def _get_cached_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """캐시된 시세 조회"""
        if symbol in self.price_cache:
            cached_data = self.price_cache[symbol]
            cache_time = datetime.fromisoformat(cached_data["cached_at"])

            # 캐시 유효성 확인
            if (datetime.now() - cache_time).total_seconds() < self.cache_timeout:
                return cached_data["data"]

        return None

    def _cache_quote(self, symbol: str, quote_data: Dict[str, Any]):
        """시세 데이터 캐시"""
        self.price_cache[symbol] = {
            "data": quote_data,
            "cached_at": datetime.now().isoformat()
        }

    def _get_market_status(self) -> str:
        """시장 상태 확인"""
        now = datetime.now()
        hour = now.hour

        # 한국 시장 기준 (9:00 ~ 15:30)
        if 9 <= hour < 15 or (hour == 15 and now.minute <= 30):
            return "market_hours"
        else:
            return "after_hours"

    def _get_trading_session(self) -> str:
        """거래 세션 상태"""
        market_status = self._get_market_status()
        if market_status == "market_hours":
            return "regular"
        else:
            return "closed"

    def _parse_period(self, period: str) -> int:
        """기간 문자열을 일수로 변환"""
        period_map = {
            "1D": 1,
            "1W": 7,
            "1M": 30,
            "3M": 90,
            "6M": 180,
            "1Y": 365,
            "2Y": 730
        }
        return period_map.get(period, 30)

    async def _generate_mock_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        interval: str
    ) -> List[Dict[str, Any]]:
        """모의 과거 데이터 생성"""
        data = []
        current_date = start_date
        base_price = 75000  # 기준 가격

        import random

        while current_date <= datetime.now():
            # 일일 변동률 (-3% ~ +3%)
            daily_change = random.uniform(-0.03, 0.03)
            base_price = base_price * (1 + daily_change)

            # OHLCV 데이터 생성
            open_price = base_price * random.uniform(0.98, 1.02)
            high_price = base_price * random.uniform(1.0, 1.05)
            low_price = base_price * random.uniform(0.95, 1.0)
            close_price = base_price
            volume = random.randint(1000000, 20000000)

            data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price),
                "high": round(high_price),
                "low": round(low_price),
                "close": round(close_price),
                "volume": volume
            })

            # 다음 날짜로
            if interval == "1d":
                current_date += timedelta(days=1)
            elif interval == "1h":
                current_date += timedelta(hours=1)
            else:
                current_date += timedelta(days=1)

            # 주말 제외
            if current_date.weekday() >= 5:  # 토요일, 일요일
                current_date += timedelta(days=2)

        return data

    async def get_market_news(self, limit: int = 10) -> Dict[str, Any]:
        """시장 뉴스 조회"""
        try:
            self._validate_initialized()

            # 모의 뉴스 데이터
            mock_news = [
                {
                    "id": "news_1",
                    "title": "삼성전자, 새로운 반도체 공장 건설 계획 발표",
                    "summary": "삼성전자가 차세대 반도체 생산을 위한 새로운 공장 건설을 발표했습니다.",
                    "source": "전자신문",
                    "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "url": "https://example.com/news/1",
                    "sentiment": "positive",
                    "related_symbols": ["005930.KS"]
                },
                {
                    "id": "news_2",
                    "title": "코스피, 외국인 매도세에 하락 마감",
                    "summary": "외국인 투자자들의 지속적인 매도세로 인해 코스피가 하락 마감했습니다.",
                    "source": "한국경제",
                    "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                    "url": "https://example.com/news/2",
                    "sentiment": "negative",
                    "related_symbols": []
                },
                {
                    "id": "news_3",
                    "title": "네이버, AI 기술 발전으로 매출 증가 전망",
                    "summary": "네이버의 AI 기술 발전이 향후 매출 증가로 이어질 것으로 전망됩니다.",
                    "source": "디지털타임스",
                    "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "url": "https://example.com/news/3",
                    "sentiment": "positive",
                    "related_symbols": ["035420.KS"]
                }
            ]

            # 요청된 개수만큼 반환
            news_data = mock_news[:limit]

            return self._create_response(
                success=True,
                data={
                    "news": news_data,
                    "total_count": len(mock_news),
                    "last_updated": datetime.now().isoformat()
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_market_news")