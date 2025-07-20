"""
Data source management and coordination
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Type
from dataclasses import dataclass, field
from enum import Enum

from .base import DataSource, MarketData, DataSourceConfig
from .yahoo_finance import YahooFinanceSource
from .demo_data import DemoDataSource
from ...utils.logger import logger


class DataSourcePriority(Enum):
    """Data source priority levels"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    BACKUP = "backup"
    SIMULATION = "simulation"


@dataclass
class DataSourceRegistry:
    """Registry for available data sources"""
    sources: Dict[str, Type[DataSource]] = field(default_factory=dict)
    
    def register(self, name: str, source_class: Type[DataSource]) -> None:
        """Register a data source class"""
        self.sources[name] = source_class
    
    def get_source_class(self, name: str) -> Optional[Type[DataSource]]:
        """Get data source class by name"""
        return self.sources.get(name)
    
    def list_sources(self) -> List[str]:
        """List all registered data sources"""
        return list(self.sources.keys())


# Global data source registry
registry = DataSourceRegistry()
registry.register("yahoo", YahooFinanceSource)
registry.register("demo", DemoDataSource)


@dataclass
class DataSourceInstance:
    """Data source instance with priority and status"""
    source: DataSource
    priority: DataSourcePriority
    enabled: bool = True
    last_success: Optional[datetime] = None
    error_count: int = 0
    consecutive_errors: int = 0
    
    def record_success(self) -> None:
        """Record successful operation"""
        self.last_success = datetime.now()
        self.consecutive_errors = 0
    
    def record_error(self) -> None:
        """Record failed operation"""
        self.error_count += 1
        self.consecutive_errors += 1
        
        # Auto-disable after too many consecutive errors
        if self.consecutive_errors >= 5:
            self.enabled = False
            logger.warning(f"데이터 소스 자동 비활성화: {self.source.name}")


class DataManager:
    """Manages multiple data sources with failover"""
    
    def __init__(self):
        self.sources: Dict[str, DataSourceInstance] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.default_cache_duration = 300  # 5 minutes
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._is_running = False
    
    async def add_source(
        self, 
        name: str, 
        config: DataSourceConfig, 
        priority: DataSourcePriority = DataSourcePriority.PRIMARY
    ) -> bool:
        """Add a new data source"""
        try:
            source_class = registry.get_source_class(name)
            if not source_class:
                logger.error(f"알 수 없는 데이터 소스: {name}")
                return False
            
            # Create and connect to data source
            source = source_class(config)
            connected = await source.connect()
            
            if connected:
                self.sources[config.name] = DataSourceInstance(
                    source=source,
                    priority=priority,
                    enabled=True
                )
                logger.info(f"데이터 소스 추가됨: {config.name} ({name})")
                return True
            else:
                logger.error(f"데이터 소스 연결 실패: {config.name}")
                return False
                
        except Exception as e:
            logger.error(f"데이터 소스 추가 오류: {e}")
            return False
    
    async def remove_source(self, name: str) -> bool:
        """Remove a data source"""
        if name in self.sources:
            source_instance = self.sources[name]
            await source_instance.source.disconnect()
            del self.sources[name]
            logger.info(f"데이터 소스 제거됨: {name}")
            return True
        return False
    
    async def get_current_data(self, symbol: str) -> Optional[MarketData]:
        """Get current market data with failover"""
        cache_key = f"current_{symbol}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return MarketData(**cached_data)
        
        # Try data sources in priority order
        for source_instance in self._get_sources_by_priority():
            if not source_instance.enabled:
                continue
                
            try:
                data = await source_instance.source.get_current_data(symbol)
                if data:
                    source_instance.record_success()
                    self._cache_data(cache_key, data.to_dict())
                    return data
                    
            except Exception as e:
                logger.warning(f"데이터 소스 오류 {source_instance.source.name}: {e}")
                source_instance.record_error()
                continue
        
        logger.error(f"모든 데이터 소스에서 실패: {symbol}")
        return None
    
    async def get_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MarketData]:
        """Get historical market data with failover"""
        cache_key = f"historical_{symbol}_{start_date.date()}_{end_date.date()}"
        
        # Check cache first (longer TTL for historical data)
        if self._is_cache_valid(cache_key, ttl_minutes=60):
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return [MarketData(**item) for item in cached_data]
        
        # Try data sources in priority order
        for source_instance in self._get_sources_by_priority():
            if not source_instance.enabled:
                continue
                
            try:
                data = await source_instance.source.get_historical_data(
                    symbol, start_date, end_date
                )
                if data:
                    source_instance.record_success()
                    self._cache_data(
                        cache_key, 
                        [item.to_dict() for item in data],
                        ttl_minutes=60
                    )
                    return data
                    
            except Exception as e:
                logger.warning(f"히스토리 데이터 소스 오류 {source_instance.source.name}: {e}")
                source_instance.record_error()
                continue
        
        logger.error(f"모든 데이터 소스에서 히스토리 데이터 실패: {symbol}")
        return []
    
    async def get_volatility_data(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get volatility data with failover"""
        cache_key = f"volatility_{symbol}"
        
        # Check cache first
        if self._is_cache_valid(cache_key, ttl_minutes=30):
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
        
        # Try data sources in priority order
        for source_instance in self._get_sources_by_priority():
            if not source_instance.enabled:
                continue
                
            try:
                data = await source_instance.source.get_volatility_data(symbol)
                if data:
                    source_instance.record_success()
                    self._cache_data(cache_key, data, ttl_minutes=30)
                    return data
                    
            except Exception as e:
                logger.warning(f"변동성 데이터 소스 오류 {source_instance.source.name}: {e}")
                source_instance.record_error()
                continue
        
        logger.error(f"모든 데이터 소스에서 변동성 데이터 실패: {symbol}")
        return None
    
    async def get_market_indices(self) -> Dict[str, MarketData]:
        """Get market indices data with failover"""
        cache_key = "market_indices"
        
        # Check cache first
        if self._is_cache_valid(cache_key, ttl_minutes=5):
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return {
                    name: MarketData(**data) 
                    for name, data in cached_data.items()
                }
        
        # Try data sources in priority order
        for source_instance in self._get_sources_by_priority():
            if not source_instance.enabled:
                continue
                
            try:
                data = await source_instance.source.get_market_indices()
                if data:
                    source_instance.record_success()
                    cache_data = {
                        name: market_data.to_dict() 
                        for name, market_data in data.items()
                    }
                    self._cache_data(cache_key, cache_data, ttl_minutes=5)
                    return data
                    
            except Exception as e:
                logger.warning(f"시장 지수 데이터 소스 오류 {source_instance.source.name}: {e}")
                source_instance.record_error()
                continue
        
        logger.error("모든 데이터 소스에서 시장 지수 데이터 실패")
        return {}
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all data sources"""
        results = {}
        
        for name, source_instance in self.sources.items():
            try:
                healthy = await source_instance.source.health_check()
                results[name] = healthy
                
                if not healthy and source_instance.enabled:
                    source_instance.record_error()
                elif healthy and not source_instance.enabled:
                    # Re-enable if it's working again
                    source_instance.enabled = True
                    source_instance.consecutive_errors = 0
                    logger.info(f"데이터 소스 재활성화: {name}")
                    
            except Exception as e:
                logger.error(f"데이터 소스 상태 확인 실패 {name}: {e}")
                results[name] = False
                source_instance.record_error()
        
        return results
    
    def get_source_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all data sources"""
        stats = {}
        
        for name, source_instance in self.sources.items():
            source_stats = source_instance.source.get_stats()
            source_stats.update({
                'priority': source_instance.priority.value,
                'enabled': source_instance.enabled,
                'manager_error_count': source_instance.error_count,
                'consecutive_errors': source_instance.consecutive_errors,
                'last_success': source_instance.last_success.isoformat() if source_instance.last_success else None
            })
            stats[name] = source_stats
        
        return stats
    
    def _get_sources_by_priority(self) -> List[DataSourceInstance]:
        """Get data sources sorted by priority"""
        priority_order = [
            DataSourcePriority.PRIMARY,
            DataSourcePriority.SECONDARY,
            DataSourcePriority.BACKUP,
            DataSourcePriority.SIMULATION
        ]
        
        sources = []
        for priority in priority_order:
            for source_instance in self.sources.values():
                if source_instance.priority == priority:
                    sources.append(source_instance)
        
        return sources
    
    def _cache_data(self, key: str, data: Any, ttl_minutes: int = None) -> None:
        """Cache data with TTL"""
        if ttl_minutes is None:
            ttl_minutes = self.default_cache_duration // 60
            
        self.cache[key] = data
        self.cache_ttl[key] = datetime.now() + timedelta(minutes=ttl_minutes)
    
    def _is_cache_valid(self, key: str, ttl_minutes: int = None) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
            
        if key not in self.cache_ttl:
            return False
            
        return datetime.now() < self.cache_ttl[key]
    
    def _cleanup_cache(self) -> None:
        """Remove expired cache entries"""
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self.cache_ttl.items() 
            if now >= expiry
        ]
        
        for key in expired_keys:
            self.cache.pop(key, None)
            self.cache_ttl.pop(key, None)
    
    async def start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        if self._is_running:
            return
            
        self._is_running = True
        
        # Cache cleanup task
        async def cache_cleanup_task():
            while self._is_running:
                self._cleanup_cache()
                await asyncio.sleep(60)  # Clean every minute
        
        # Health check task
        async def health_check_task():
            while self._is_running:
                await self.health_check()
                await asyncio.sleep(300)  # Check every 5 minutes
        
        self._background_tasks = [
            asyncio.create_task(cache_cleanup_task()),
            asyncio.create_task(health_check_task())
        ]
    
    async def stop_background_tasks(self) -> None:
        """Stop background maintenance tasks"""
        self._is_running = False
        
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
    
    async def shutdown(self) -> None:
        """Shutdown data manager and all sources"""
        await self.stop_background_tasks()
        
        for name in list(self.sources.keys()):
            await self.remove_source(name)
        
        logger.info("데이터 매니저 종료")