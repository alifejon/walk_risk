"""Yahoo Finance API 연돔 - 실시간 주식 데이터 수집"""

import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from asyncio_throttle import Throttler
import logging

from ...utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class StockData:
    """주식 데이터 모델"""
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def is_gain(self) -> bool:
        return self.change > 0
        
    @property
    def formatted_change(self) -> str:
        sign = "+" if self.change >= 0 else ""
        return f"{sign}{self.change:.2f} ({sign}{self.change_percent:.2f}%)"


@dataclass
class MarketSummary:
    """시장 요약 정보"""
    kospi_index: float
    kospi_change: float
    kospi_change_percent: float
    kosdaq_index: float
    kosdaq_change: float
    kosdaq_change_percent: float
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def market_sentiment(self) -> str:
        """시장 심리 판단"""
        avg_change = (self.kospi_change_percent + self.kosdaq_change_percent) / 2
        if avg_change > 1:
            return "bullish"  # 상승세
        elif avg_change < -1:
            return "bearish"  # 하락세
        else:
            return "neutral"  # 보합세


class YahooFinanceConnector:
    """
Yahoo Finance API 연동 클래스

한국 주식 데이터를 수집하고 실시간 업데이트를 제공합니다.
    """
    
    def __init__(self, throttle_rate: float = 1.0):
        self.throttler = Throttler(rate_limit=throttle_rate)  # 초당 요청 수 제한
        self.cache: Dict[str, StockData] = {}
        self.cache_duration = 60  # 60초 캐시
        
        # 한국 주요 주식 심볼 매핑
        self.korean_stocks = {
            "005930.KS": "삼성전자",
            "000660.KS": "SK하이닉스", 
            "035420.KS": "NAVER",
            "005490.KS": "POSCO홀딩스",
            "035720.KS": "카카오",
            "012330.KS": "현대모비스",
            "028260.KS": "삼성물산",
            "068270.KS": "셀트리온",
            "105560.KS": "KB금융",
            "055550.KS": "신한은행",
            "003550.KS": "LG",
            "096770.KS": "SK이노베이션",
            "018260.KS": "삼성SDI",
            "032830.KS": "삼성생명",
            "017670.KS": "SK텔레콤"
        }
        
        # 시장 지수
        self.market_indices = {
            "^KS11": "KOSPI",
            "^KQ11": "KOSDAQ"
        }
        
    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """단일 주식 데이터 수집"""
        try:
            # 캐시 확인
            if symbol in self.cache:
                cached_data = self.cache[symbol]
                if (datetime.now() - cached_data.last_updated).seconds < self.cache_duration:
                    return cached_data
                    
            async with self.throttler:
                # Yahoo Finance에서 데이터 수집
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                if hist.empty or len(hist) < 1:
                    logger.warning(f"데이터를 찾을 수 없습니다: {symbol}")
                    return None
                    
                # 최신 데이터 추출
                latest_data = hist.iloc[-1]
                previous_data = hist.iloc[-2] if len(hist) >= 2 else latest_data
                
                current_price = float(latest_data['Close'])
                previous_close = float(previous_data['Close'])
                change = current_price - previous_close
                change_percent = (change / previous_close * 100) if previous_close != 0 else 0
                
                stock_data = StockData(
                    symbol=symbol,
                    name=self.korean_stocks.get(symbol, info.get('longName', symbol)),
                    current_price=current_price,
                    previous_close=previous_close,
                    change=change,
                    change_percent=change_percent,
                    volume=int(latest_data.get('Volume', 0)),
                    market_cap=info.get('marketCap'),
                    pe_ratio=info.get('trailingPE'),
                    dividend_yield=info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None
                )
                
                # 캐시 업데이트
                self.cache[symbol] = stock_data
                
                logger.info(f"주식 데이터 업데이트: {stock_data.name} - {stock_data.current_price:,.0f}원")
                return stock_data
                
        except Exception as e:
            logger.error(f"주식 데이터 수집 실패 ({symbol}): {e}")
            return None
            
    async def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, StockData]:
        """여러 주식 데이터 동시 수집"""
        tasks = [self.get_stock_data(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        stock_data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, StockData):
                stock_data[symbol] = result
            elif isinstance(result, Exception):
                logger.error(f"주식 데이터 수집 실패 ({symbol}): {result}")
                
        return stock_data
        
    async def get_market_summary(self) -> Optional[MarketSummary]:
        """시장 지수 요약 정보"""
        try:
            async with self.throttler:
                # KOSPI 데이터
                kospi = yf.Ticker("^KS11")
                kospi_hist = kospi.history(period="2d")
                
                # KOSDAQ 데이터
                kosdaq = yf.Ticker("^KQ11")
                kosdaq_hist = kosdaq.history(period="2d")
                
                if kospi_hist.empty or kosdaq_hist.empty:
                    logger.warning("시장 지수 데이터를 찾을 수 없습니다")
                    return None
                    
                # KOSPI 계산
                kospi_current = float(kospi_hist.iloc[-1]['Close'])
                kospi_previous = float(kospi_hist.iloc[-2]['Close']) if len(kospi_hist) >= 2 else kospi_current
                kospi_change = kospi_current - kospi_previous
                kospi_change_percent = (kospi_change / kospi_previous * 100) if kospi_previous != 0 else 0
                
                # KOSDAQ 계산
                kosdaq_current = float(kosdaq_hist.iloc[-1]['Close'])
                kosdaq_previous = float(kosdaq_hist.iloc[-2]['Close']) if len(kosdaq_hist) >= 2 else kosdaq_current
                kosdaq_change = kosdaq_current - kosdaq_previous
                kosdaq_change_percent = (kosdaq_change / kosdaq_previous * 100) if kosdaq_previous != 0 else 0
                
                summary = MarketSummary(
                    kospi_index=kospi_current,
                    kospi_change=kospi_change,
                    kospi_change_percent=kospi_change_percent,
                    kosdaq_index=kosdaq_current,
                    kosdaq_change=kosdaq_change,
                    kosdaq_change_percent=kosdaq_change_percent
                )
                
                logger.info(f"시장 요약: KOSPI {kospi_current:.2f} ({kospi_change:+.2f}), KOSDAQ {kosdaq_current:.2f} ({kosdaq_change:+.2f})")
                return summary
                
        except Exception as e:
            logger.error(f"시장 요약 수집 실패: {e}")
            return None
            
    def get_popular_korean_stocks(self) -> List[str]:
        """인기 한국 주식 목록 반환"""
        return list(self.korean_stocks.keys())
        
    def get_stock_name(self, symbol: str) -> str:
        """주식 심볼로 한글 이름 반환"""
        return self.korean_stocks.get(symbol, symbol)
        
    async def search_stocks(self, query: str) -> List[Dict[str, str]]:
        """주식 검색 (한글 이름 기반)"""
        results = []
        query_lower = query.lower()
        
        for symbol, name in self.korean_stocks.items():
            if query_lower in name.lower() or query_lower in symbol.lower():
                results.append({
                    "symbol": symbol,
                    "name": name
                })
                
        return results
        
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """과거 데이터 수집"""
        try:
            async with self.throttler:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period, interval=interval)
                
                if hist.empty:
                    logger.warning(f"과거 데이터를 찾을 수 없습니다: {symbol}")
                    return None
                    
                return hist
                
        except Exception as e:
            logger.error(f"과거 데이터 수집 실패 ({symbol}): {e}")
            return None


# 전역 인스턴스
yahoo_finance = YahooFinanceConnector()


async def demo_yahoo_finance():
    """
Yahoo Finance 연동 데모
    """
    print("📈 Yahoo Finance 연동 데모")
    print("=" * 40)
    
    # 시장 요약
    market_summary = await yahoo_finance.get_market_summary()
    if market_summary:
        print(f"🏆 KOSPI: {market_summary.kospi_index:.2f} ({market_summary.kospi_change:+.2f})")
        print(f"🏆 KOSDAQ: {market_summary.kosdaq_index:.2f} ({market_summary.kosdaq_change:+.2f})")
        print(f"📊 시장 심리: {market_summary.market_sentiment}")
        print()
    
    # 주요 주식 3개
    symbols = ["005930.KS", "035420.KS", "000660.KS"]
    stocks = await yahoo_finance.get_multiple_stocks(symbols)
    
    print("📊 주요 주식:")
    for symbol, stock in stocks.items():
        if stock:
            print(f"  {stock.name}: {stock.current_price:,.0f}원 ({stock.formatted_change})")
    
    print("\n✅ 데모 완료!")


if __name__ == "__main__":
    asyncio.run(demo_yahoo_finance())