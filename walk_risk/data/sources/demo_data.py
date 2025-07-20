"""
Demo data source for testing and development
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from math import sin, cos, pi

from .base import DataSource, MarketData, DataSourceConfig, DataSourceType
from ...utils.logger import logger


class DemoDataSource(DataSource):
    """Demo data source with simulated market data"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.symbols = config.symbols or ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'SPY']
        self.base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 300.0,
            'TSLA': 800.0,
            'SPY': 400.0,
            '^GSPC': 4000.0,
            '^IXIC': 12000.0,
            '^DJI': 33000.0,
            '^VIX': 20.0,
            '^RUT': 1800.0
        }
        self.price_history = {}
        self.volatility_levels = {}
        self._simulation_time = datetime.now()
        
    async def connect(self) -> bool:
        """Connect to demo data source"""
        try:
            # Initialize price history and volatility
            for symbol in self.symbols:
                self.price_history[symbol] = []
                self.volatility_levels[symbol] = random.uniform(0.15, 0.45)
            
            # Generate initial historical data
            await self._generate_initial_history()
            
            self._connection_status = True
            logger.info(f"Demo 데이터 소스 연결 성공: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Demo 데이터 소스 연결 실패: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from demo data source"""
        self._connection_status = False
        logger.info(f"Demo 데이터 소스 연결 해제: {self.name}")
    
    async def get_current_data(self, symbol: str) -> Optional[MarketData]:
        """Get current simulated market data"""
        if not self._connection_status:
            return None
            
        try:
            self._increment_request_count()
            
            # Simulate network delay
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Generate realistic market data
            base_price = self.base_prices.get(symbol, 100.0)
            current_price = self._simulate_price_movement(symbol, base_price)
            
            # Calculate day's high/low/open
            day_volatility = self.volatility_levels.get(symbol, 0.2)
            price_range = current_price * day_volatility * 0.1
            
            high = current_price + random.uniform(0, price_range)
            low = current_price - random.uniform(0, price_range)
            open_price = current_price + random.uniform(-price_range/2, price_range/2)
            
            volume = random.randint(1000000, 50000000)
            
            # Special handling for VIX
            if symbol == '^VIX':
                vix_value = current_price
            else:
                vix_value = self._simulate_vix()
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.now(),
                price=current_price,
                volume=volume,
                high=high,
                low=low,
                open=open_price,
                close=current_price,
                volatility=day_volatility,
                vix=vix_value,
                beta=random.uniform(0.8, 1.5),
                correlation=random.uniform(-0.3, 0.8),
                rsi=random.uniform(30, 70),
                source=self.name,
                data_type=DataSourceType.SIMULATION,
                quality_score=1.0
            )
            
            # Store in history
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            self.price_history[symbol].append(market_data)
            
            # Keep only last 1000 data points
            if len(self.price_history[symbol]) > 1000:
                self.price_history[symbol] = self.price_history[symbol][-1000:]
            
            self._update_last_update()
            return market_data
            
        except Exception as e:
            logger.error(f"Demo 데이터 생성 실패: {e}")
            self._increment_error_count()
            return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MarketData]:
        """Get historical simulated market data"""
        if not self._connection_status:
            return []
            
        try:
            self._increment_request_count()
            
            # Simulate network delay
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            historical_data = []
            current_date = start_date
            base_price = self.base_prices.get(symbol, 100.0)
            current_price = base_price
            
            while current_date <= end_date:
                # Simulate daily price movement
                daily_change = random.uniform(-0.05, 0.05)  # -5% to +5%
                current_price *= (1 + daily_change)
                
                # Ensure price doesn't go too far from base
                if abs(current_price - base_price) > base_price * 0.3:
                    current_price = base_price + random.uniform(-base_price*0.3, base_price*0.3)
                
                # Calculate day's OHLC
                day_volatility = self.volatility_levels.get(symbol, 0.2)
                price_range = current_price * day_volatility * 0.1
                
                open_price = current_price + random.uniform(-price_range/2, price_range/2)
                high = max(open_price, current_price) + random.uniform(0, price_range/2)
                low = min(open_price, current_price) - random.uniform(0, price_range/2)
                volume = random.randint(1000000, 50000000)
                
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=current_date,
                    price=current_price,
                    volume=volume,
                    high=high,
                    low=low,
                    open=open_price,
                    close=current_price,
                    volatility=day_volatility,
                    vix=self._simulate_vix(),
                    beta=random.uniform(0.8, 1.5),
                    source=self.name,
                    data_type=DataSourceType.HISTORICAL,
                    quality_score=1.0
                )
                
                historical_data.append(market_data)
                current_date += timedelta(days=1)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Demo 히스토리 데이터 생성 실패: {e}")
            self._increment_error_count()
            return []
    
    async def get_volatility_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get volatility data for symbol"""
        if not self._connection_status:
            return None
            
        try:
            self._increment_request_count()
            
            # Simulate network delay
            await asyncio.sleep(random.uniform(0.1, 0.2))
            
            base_volatility = self.volatility_levels.get(symbol, 0.2)
            
            # Add some randomness to volatility
            current_volatility = base_volatility * random.uniform(0.8, 1.2)
            
            return {
                'volatility': current_volatility,
                'daily_volatility': current_volatility / (252 ** 0.5),
                'return_mean': random.uniform(-0.001, 0.001),
                'return_std': current_volatility / (252 ** 0.5),
                'price_range': random.uniform(0.1, 0.3),
                'vix_correlation': random.uniform(0.3, 0.8),
                'beta': random.uniform(0.8, 1.5),
                'sharpe_ratio': random.uniform(0.5, 2.0)
            }
            
        except Exception as e:
            logger.error(f"Demo 변동성 데이터 생성 실패: {e}")
            self._increment_error_count()
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
        """Health check always returns True for demo"""
        return True
    
    def _simulate_price_movement(self, symbol: str, base_price: float) -> float:
        """Simulate realistic price movement"""
        # Use sine wave with random noise for realistic movement
        time_factor = datetime.now().timestamp() / 3600  # Hours since epoch
        
        # Different frequencies for different symbols
        frequency = hash(symbol) % 10 + 1
        
        # Trend component (sine wave)
        trend = sin(time_factor * frequency * pi / 24) * 0.02
        
        # Random walk component
        random_walk = random.uniform(-0.01, 0.01)
        
        # Volatility component
        volatility = self.volatility_levels.get(symbol, 0.2)
        volatility_factor = random.gauss(0, volatility * 0.1)
        
        # Combine all factors
        total_change = trend + random_walk + volatility_factor
        
        # Apply change to base price
        new_price = base_price * (1 + total_change)
        
        # Ensure price doesn't go negative or too extreme
        new_price = max(new_price, base_price * 0.1)
        new_price = min(new_price, base_price * 3.0)
        
        return round(new_price, 2)
    
    def _simulate_vix(self) -> float:
        """Simulate VIX (volatility index)"""
        # VIX typically ranges from 10-80, with 20 being average
        base_vix = 20.0
        
        # Add some randomness and market stress simulation
        stress_factor = random.uniform(0.8, 1.5)
        random_factor = random.uniform(-5, 5)
        
        vix = base_vix * stress_factor + random_factor
        
        # Clamp to realistic range
        vix = max(10, min(80, vix))
        
        return round(vix, 2)
    
    async def _generate_initial_history(self) -> None:
        """Generate initial historical data for symbols"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        for symbol in self.symbols:
            historical_data = await self.get_historical_data(symbol, start_date, end_date)
            self.price_history[symbol] = historical_data
    
    def inject_market_event(self, event_type: str, intensity: float = 1.0) -> None:
        """Inject simulated market events for testing"""
        if event_type == "crash":
            # Simulate market crash
            for symbol in self.symbols:
                self.base_prices[symbol] *= (1 - 0.2 * intensity)
                self.volatility_levels[symbol] *= (1 + 0.5 * intensity)
        
        elif event_type == "rally":
            # Simulate market rally
            for symbol in self.symbols:
                self.base_prices[symbol] *= (1 + 0.15 * intensity)
                self.volatility_levels[symbol] *= (1 - 0.2 * intensity)
        
        elif event_type == "volatility_spike":
            # Simulate volatility spike
            for symbol in self.symbols:
                self.volatility_levels[symbol] *= (1 + 0.8 * intensity)
        
        elif event_type == "flash_crash":
            # Simulate flash crash (temporary)
            for symbol in self.symbols:
                self.base_prices[symbol] *= (1 - 0.1 * intensity)
        
        logger.info(f"시장 이벤트 주입: {event_type} (강도: {intensity})")
    
    def reset_market_conditions(self) -> None:
        """Reset to normal market conditions"""
        # Reset to original base prices and volatility
        self.base_prices = {
            'AAPL': 150.0,
            'GOOGL': 2800.0,
            'MSFT': 300.0,
            'TSLA': 800.0,
            'SPY': 400.0,
            '^GSPC': 4000.0,
            '^IXIC': 12000.0,
            '^DJI': 33000.0,
            '^VIX': 20.0,
            '^RUT': 1800.0
        }
        
        for symbol in self.symbols:
            self.volatility_levels[symbol] = random.uniform(0.15, 0.45)
        
        logger.info("시장 조건 리셋")