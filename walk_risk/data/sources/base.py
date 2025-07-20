"""
Base classes for market data sources
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class DataSourceType(Enum):
    """Types of market data sources"""
    REAL_TIME = "real_time"
    DELAYED = "delayed"
    HISTORICAL = "historical"
    SIMULATION = "simulation"


@dataclass
class MarketData:
    """Standard market data structure"""
    symbol: str
    timestamp: datetime
    price: float
    volume: Optional[int] = None
    high: Optional[float] = None
    low: Optional[float] = None
    open: Optional[float] = None
    close: Optional[float] = None
    
    # Volatility indicators
    volatility: Optional[float] = None
    vix: Optional[float] = None
    
    # Additional metrics
    beta: Optional[float] = None
    correlation: Optional[float] = None
    rsi: Optional[float] = None
    
    # Metadata
    source: str = ""
    data_type: DataSourceType = DataSourceType.REAL_TIME
    quality_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'volume': self.volume,
            'high': self.high,
            'low': self.low,
            'open': self.open,
            'close': self.close,
            'volatility': self.volatility,
            'vix': self.vix,
            'beta': self.beta,
            'correlation': self.correlation,
            'rsi': self.rsi,
            'source': self.source,
            'data_type': self.data_type.value,
            'quality_score': self.quality_score
        }


@dataclass
class DataSourceConfig:
    """Configuration for market data sources"""
    name: str
    api_key: str = ""
    base_url: str = ""
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_count: int = 3
    cache_duration: int = 300  # seconds
    
    # Data quality settings
    max_staleness: int = 300  # seconds
    min_quality_score: float = 0.8
    
    # Symbols to track
    symbols: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return bool(self.name and self.base_url)


class DataSource(ABC):
    """Abstract base class for market data sources"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.name = config.name
        self._connection_status = False
        self._last_update = None
        self._request_count = 0
        self._error_count = 0
    
    @property
    def is_connected(self) -> bool:
        """Check if data source is connected"""
        return self._connection_status
    
    @property
    def request_count(self) -> int:
        """Number of API requests made"""
        return self._request_count
    
    @property
    def error_count(self) -> int:
        """Number of errors encountered"""
        return self._error_count
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from data source"""
        pass
    
    @abstractmethod
    async def get_current_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data for symbol"""
        pass
    
    @abstractmethod
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MarketData]:
        """Get historical market data"""
        pass
    
    @abstractmethod
    async def get_volatility_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get volatility indicators for symbol"""
        pass
    
    @abstractmethod
    async def get_market_indices(self) -> Dict[str, MarketData]:
        """Get major market indices data"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if data source is healthy"""
        pass
    
    def _increment_request_count(self) -> None:
        """Increment API request counter"""
        self._request_count += 1
    
    def _increment_error_count(self) -> None:
        """Increment error counter"""
        self._error_count += 1
    
    def _update_last_update(self) -> None:
        """Update last successful update timestamp"""
        self._last_update = datetime.now()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get data source statistics"""
        return {
            'name': self.name,
            'connected': self.is_connected,
            'requests': self.request_count,
            'errors': self.error_count,
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'error_rate': self.error_count / max(self.request_count, 1)
        }