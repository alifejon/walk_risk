"""
Yahoo Finance data source implementation
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from urllib.parse import urlencode

from .base import DataSource, MarketData, DataSourceConfig, DataSourceType
from ...utils.logger import logger


class YahooFinanceSource(DataSource):
    """Yahoo Finance data source"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.base_url = "https://query1.finance.yahoo.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def connect(self) -> bool:
        """Connect to Yahoo Finance"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
            
            # Test connection with a simple query
            test_result = await self.health_check()
            if test_result:
                self._connection_status = True
                logger.info(f"Yahoo Finance 연결 성공: {self.name}")
                return True
            else:
                await self.disconnect()
                return False
                
        except Exception as e:
            logger.error(f"Yahoo Finance 연결 실패: {e}")
            self._increment_error_count()
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from Yahoo Finance"""
        if self.session:
            await self.session.close()
            self.session = None
        self._connection_status = False
    
    async def get_current_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for symbol"""
        if not self.session:
            return None
            
        try:
            # Yahoo Finance API endpoint for current quote
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'interval': '1m',
                'range': '1d',
                'includePrePost': 'true'
            }
            
            self._increment_request_count()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_current_data(symbol, data)
                else:
                    logger.warning(f"Yahoo Finance API 오류: {response.status}")
                    self._increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Yahoo Finance 데이터 가져오기 실패: {e}")
            self._increment_error_count()
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MarketData]:
        """Get historical market data"""
        if not self.session:
            return []
            
        try:
            # Convert dates to Unix timestamps
            start_timestamp = int(start_date.timestamp())
            end_timestamp = int(end_date.timestamp())
            
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'period1': start_timestamp,
                'period2': end_timestamp,
                'interval': '1d',
                'includeAdjustedClose': 'true'
            }
            
            self._increment_request_count()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_historical_data(symbol, data)
                else:
                    logger.warning(f"Yahoo Finance 히스토리 API 오류: {response.status}")
                    self._increment_error_count()
                    return []
                    
        except Exception as e:
            logger.error(f"Yahoo Finance 히스토리 데이터 가져오기 실패: {e}")
            self._increment_error_count()
            return []
    
    async def get_volatility_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get volatility indicators for symbol"""
        # Get 20 days of historical data to calculate volatility
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        historical_data = await self.get_historical_data(symbol, start_date, end_date)
        
        if len(historical_data) < 2:
            return None
        
        # Calculate simple volatility metrics
        prices = [data.close for data in historical_data if data.close]
        
        if len(prices) < 2:
            return None
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(prices)):
            daily_return = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(daily_return)
        
        # Calculate volatility (standard deviation of returns)
        if returns:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = (variance ** 0.5) * (252 ** 0.5)  # Annualized volatility
            
            return {
                'volatility': volatility,
                'daily_volatility': variance ** 0.5,
                'return_mean': mean_return,
                'return_std': variance ** 0.5,
                'price_range': max(prices) - min(prices)
            }
        
        return None
    
    async def get_market_indices(self) -> Dict[str, MarketData]:
        """Get major market indices data"""
        indices = {
            'S&P 500': '^GSPC',
            'NASDAQ': '^IXIC',
            'Dow Jones': '^DJI',
            'VIX': '^VIX',
            'Russell 2000': '^RUT'
        }
        
        results = {}
        
        for name, symbol in indices.items():
            data = await self.get_current_data(symbol)
            if data:
                results[name] = data
        
        return results
    
    async def health_check(self) -> bool:
        """Check if Yahoo Finance is accessible"""
        try:
            if not self.session:
                return False
                
            # Test with S&P 500 index
            url = f"{self.base_url}/v8/finance/chart/^GSPC"
            params = {'interval': '1d', 'range': '1d'}
            
            async with self.session.get(url, params=params) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Yahoo Finance 상태 확인 실패: {e}")
            return False
    
    def _parse_current_data(self, symbol: str, data: Dict[str, Any]) -> Optional[MarketData]:
        """Parse current market data from Yahoo Finance response"""
        try:
            chart = data['chart']['result'][0]
            meta = chart['meta']
            
            # Get latest quote
            current_price = meta.get('regularMarketPrice', meta.get('previousClose'))
            
            if current_price is None:
                return None
            
            # Get additional data if available
            quote = chart.get('indicators', {}).get('quote', [{}])[0]
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=current_price,
                volume=meta.get('regularMarketVolume'),
                high=meta.get('regularMarketDayHigh'),
                low=meta.get('regularMarketDayLow'),
                open=meta.get('regularMarketOpen'),
                close=meta.get('previousClose'),
                source=self.name,
                data_type=DataSourceType.REAL_TIME,
                quality_score=0.9
            )
            
            self._update_last_update()
            return market_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance 데이터 파싱 실패: {e}")
            return None
    
    def _parse_historical_data(self, symbol: str, data: Dict[str, Any]) -> List[MarketData]:
        """Parse historical market data from Yahoo Finance response"""
        try:
            chart = data['chart']['result'][0]
            timestamps = chart['timestamp']
            indicators = chart['indicators']['quote'][0]
            
            historical_data = []
            
            for i, timestamp in enumerate(timestamps):
                try:
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=datetime.fromtimestamp(timestamp),
                        price=indicators['close'][i],
                        volume=indicators['volume'][i],
                        high=indicators['high'][i],
                        low=indicators['low'][i],
                        open=indicators['open'][i],
                        close=indicators['close'][i],
                        source=self.name,
                        data_type=DataSourceType.HISTORICAL,
                        quality_score=0.95
                    )
                    historical_data.append(market_data)
                except (IndexError, TypeError):
                    # Skip incomplete data points
                    continue
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance 히스토리 데이터 파싱 실패: {e}")
            return []