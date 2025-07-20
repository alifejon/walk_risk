"""
Risk analysis engine with multiple risk categories
"""
import asyncio
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from ...models.risk.base import Risk, RiskCategory, RiskLevel, RiskMetrics, RiskAnalyzer
from ...data.sources.base import MarketData
from ...utils.logger import logger


class RiskEvent(Enum):
    """Types of risk events"""
    VOLATILITY_SPIKE = "volatility_spike"
    PRICE_CRASH = "price_crash"
    VOLUME_ANOMALY = "volume_anomaly"
    CORRELATION_BREAKDOWN = "correlation_breakdown"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    FLASH_CRASH = "flash_crash"
    BLACK_SWAN = "black_swan"


@dataclass
class RiskAlert:
    """Risk alert structure"""
    id: str
    event_type: RiskEvent
    severity: float  # 0-1 scale
    description: str
    affected_symbols: List[str]
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'severity': self.severity,
            'description': self.description,
            'affected_symbols': self.affected_symbols,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data
        }


class MarketRiskAnalyzer(RiskAnalyzer):
    """Market risk analyzer"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.volatility_threshold = self.config.get('volatility_threshold', 0.3)
        self.vix_high_threshold = self.config.get('vix_high_threshold', 30.0)
        self.vix_extreme_threshold = self.config.get('vix_extreme_threshold', 40.0)
        self.price_drop_threshold = self.config.get('price_drop_threshold', -0.05)
        
    async def analyze(self, data: Dict[str, Any]) -> Risk:
        """Analyze market data and create risk assessment"""
        symbol = data.get('symbol', 'UNKNOWN')
        market_data = data.get('market_data')
        historical_data = data.get('historical_data', [])
        
        if not market_data:
            raise ValueError("Market data is required for analysis")
        
        # Calculate risk metrics
        metrics = self.calculate_metrics(data)
        
        # Determine risk severity
        severity = self.determine_severity(metrics)
        
        # Calculate complexity based on market conditions
        complexity = self._calculate_complexity(market_data, historical_data)
        
        # Generate risk description
        description = self._generate_description(symbol, metrics, severity)
        
        # Create risk object
        risk = Risk(
            name=f"Market Risk - {symbol}",
            category=RiskCategory.MARKET,
            description=description,
            severity=severity,
            complexity=complexity,
            frequency=self._estimate_frequency(historical_data),
            metrics=metrics
        )
        
        # Set initial level based on severity
        if severity < 0.3:
            risk.level = RiskLevel.LOCKED
        elif severity < 0.6:
            risk.level = RiskLevel.UNLOCKING
        else:
            risk.level = RiskLevel.UNLOCKED
        
        return risk
    
    def calculate_metrics(self, data: Dict[str, Any]) -> RiskMetrics:
        """Calculate market risk metrics"""
        market_data = data.get('market_data')
        historical_data = data.get('historical_data', [])
        
        metrics = RiskMetrics()
        
        if market_data:
            # Current volatility
            metrics.volatility = market_data.volatility or 0.0
            
            # Beta from market data
            metrics.beta = market_data.beta or 1.0
            
            # Correlation
            metrics.correlation = market_data.correlation or 0.0
        
        # Calculate metrics from historical data
        if historical_data and len(historical_data) > 1:
            prices = [d.close for d in historical_data if d.close]
            
            if len(prices) > 1:
                # Calculate returns
                returns = []
                for i in range(1, len(prices)):
                    ret = (prices[i] - prices[i-1]) / prices[i-1]
                    returns.append(ret)
                
                if returns:
                    # Value at Risk (95%)
                    returns_sorted = sorted(returns)
                    var_index = int(len(returns_sorted) * 0.05)
                    metrics.var_95 = abs(returns_sorted[var_index]) if var_index < len(returns_sorted) else 0.0
                    
                    # Maximum drawdown
                    peak = prices[0]
                    max_drawdown = 0.0
                    for price in prices:
                        if price > peak:
                            peak = price
                        drawdown = (peak - price) / peak
                        max_drawdown = max(max_drawdown, drawdown)
                    
                    metrics.max_drawdown = max_drawdown
                    
                    # Sharpe ratio (simplified)
                    mean_return = np.mean(returns)
                    std_return = np.std(returns)
                    metrics.sharpe_ratio = mean_return / std_return if std_return > 0 else 0.0
        
        # Custom metrics
        metrics.custom_metrics = {
            'vix_level': market_data.vix if market_data else 0.0,
            'rsi': market_data.rsi if market_data else 50.0,
            'price_momentum': self._calculate_momentum(historical_data),
            'volume_trend': self._calculate_volume_trend(historical_data)
        }
        
        return metrics
    
    def determine_severity(self, metrics: RiskMetrics) -> float:
        """Determine risk severity from metrics"""
        severity_factors = []
        
        # Volatility factor
        if metrics.volatility > self.volatility_threshold:
            vol_factor = min(metrics.volatility / self.volatility_threshold, 2.0)
            severity_factors.append(vol_factor * 0.3)
        
        # VIX factor
        vix_level = metrics.custom_metrics.get('vix_level', 20.0)
        if vix_level > self.vix_high_threshold:
            vix_factor = min(vix_level / self.vix_high_threshold, 2.0)
            severity_factors.append(vix_factor * 0.25)
        
        # Maximum drawdown factor
        if metrics.max_drawdown > 0.1:  # 10% drawdown
            dd_factor = min(metrics.max_drawdown / 0.1, 2.0)
            severity_factors.append(dd_factor * 0.25)
        
        # VaR factor
        if metrics.var_95 > 0.03:  # 3% VaR
            var_factor = min(metrics.var_95 / 0.03, 2.0)
            severity_factors.append(var_factor * 0.2)
        
        # Calculate weighted average
        if severity_factors:
            total_severity = sum(severity_factors)
            return min(total_severity, 1.0)
        
        return 0.1  # Minimum baseline severity
    
    def _calculate_complexity(self, market_data: MarketData, historical_data: List[MarketData]) -> float:
        """Calculate risk complexity based on market conditions"""
        complexity_factors = []
        
        # Beta complexity (higher beta = more complexity)
        if market_data.beta:
            beta_complexity = abs(market_data.beta - 1.0)
            complexity_factors.append(min(beta_complexity, 1.0) * 0.3)
        
        # Correlation complexity (extreme correlations are complex)
        if market_data.correlation:
            corr_complexity = abs(market_data.correlation)
            complexity_factors.append(corr_complexity * 0.2)
        
        # Price volatility complexity
        if historical_data and len(historical_data) > 5:
            prices = [d.close for d in historical_data[-5:] if d.close]
            if len(prices) > 1:
                price_changes = [abs(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
                volatility_complexity = np.std(price_changes) * 10
                complexity_factors.append(min(volatility_complexity, 1.0) * 0.3)
        
        # Volume complexity
        if historical_data and len(historical_data) > 5:
            volumes = [d.volume for d in historical_data[-5:] if d.volume]
            if len(volumes) > 1:
                volume_changes = [abs(volumes[i] - volumes[i-1]) / volumes[i-1] for i in range(1, len(volumes))]
                volume_complexity = np.std(volume_changes) * 2
                complexity_factors.append(min(volume_complexity, 1.0) * 0.2)
        
        # Calculate weighted average
        if complexity_factors:
            return min(sum(complexity_factors), 1.0)
        
        return 0.3  # Default complexity
    
    def _estimate_frequency(self, historical_data: List[MarketData]) -> float:
        """Estimate risk event frequency"""
        if not historical_data or len(historical_data) < 10:
            return 0.1
        
        # Count significant price movements
        significant_moves = 0
        for i in range(1, len(historical_data)):
            if historical_data[i].close and historical_data[i-1].close:
                change = abs(historical_data[i].close - historical_data[i-1].close) / historical_data[i-1].close
                if change > 0.03:  # 3% change
                    significant_moves += 1
        
        # Frequency as ratio of significant moves
        return min(significant_moves / len(historical_data), 1.0)
    
    def _calculate_momentum(self, historical_data: List[MarketData]) -> float:
        """Calculate price momentum"""
        if not historical_data or len(historical_data) < 5:
            return 0.0
        
        prices = [d.close for d in historical_data[-5:] if d.close]
        if len(prices) < 2:
            return 0.0
        
        # Simple momentum: (current - past) / past
        return (prices[-1] - prices[0]) / prices[0]
    
    def _calculate_volume_trend(self, historical_data: List[MarketData]) -> float:
        """Calculate volume trend"""
        if not historical_data or len(historical_data) < 5:
            return 0.0
        
        volumes = [d.volume for d in historical_data[-5:] if d.volume]
        if len(volumes) < 2:
            return 0.0
        
        # Volume trend: (current - past) / past
        return (volumes[-1] - volumes[0]) / volumes[0]
    
    def _generate_description(self, symbol: str, metrics: RiskMetrics, severity: float) -> str:
        """Generate risk description"""
        if severity < 0.3:
            risk_level = "낮음"
        elif severity < 0.6:
            risk_level = "보통"
        else:
            risk_level = "높음"
        
        vix_level = metrics.custom_metrics.get('vix_level', 20.0)
        volatility = metrics.volatility
        
        description = f"{symbol} 시장 리스크 수준: {risk_level}\n"
        description += f"현재 변동성: {volatility:.2%}\n"
        description += f"VIX 지수: {vix_level:.1f}\n"
        
        if metrics.max_drawdown > 0.1:
            description += f"최대 손실: {metrics.max_drawdown:.2%}\n"
        
        if metrics.var_95 > 0.03:
            description += f"VaR(95%): {metrics.var_95:.2%}\n"
        
        return description


class LiquidityRiskAnalyzer(RiskAnalyzer):
    """Liquidity risk analyzer"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.volume_threshold = self.config.get('volume_threshold', 0.5)
        self.spread_threshold = self.config.get('spread_threshold', 0.02)
    
    async def analyze(self, data: Dict[str, Any]) -> Risk:
        """Analyze liquidity risk"""
        symbol = data.get('symbol', 'UNKNOWN')
        market_data = data.get('market_data')
        historical_data = data.get('historical_data', [])
        
        if not market_data:
            raise ValueError("Market data is required for liquidity analysis")
        
        metrics = self.calculate_metrics(data)
        severity = self.determine_severity(metrics)
        complexity = self._calculate_liquidity_complexity(market_data, historical_data)
        
        description = self._generate_liquidity_description(symbol, metrics, severity)
        
        risk = Risk(
            name=f"Liquidity Risk - {symbol}",
            category=RiskCategory.LIQUIDITY,
            description=description,
            severity=severity,
            complexity=complexity,
            frequency=self._estimate_liquidity_frequency(historical_data),
            metrics=metrics
        )
        
        return risk
    
    def calculate_metrics(self, data: Dict[str, Any]) -> RiskMetrics:
        """Calculate liquidity risk metrics"""
        market_data = data.get('market_data')
        historical_data = data.get('historical_data', [])
        
        metrics = RiskMetrics()
        
        # Volume-based metrics
        if historical_data and len(historical_data) > 1:
            volumes = [d.volume for d in historical_data if d.volume]
            if volumes:
                avg_volume = np.mean(volumes)
                current_volume = market_data.volume or 0
                
                # Volume ratio
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                
                # Bid-ask spread estimation (simplified)
                if market_data.high and market_data.low:
                    spread = (market_data.high - market_data.low) / market_data.price
                else:
                    spread = 0.01  # Default spread
                
                metrics.custom_metrics = {
                    'volume_ratio': volume_ratio,
                    'avg_volume': avg_volume,
                    'current_volume': current_volume,
                    'bid_ask_spread': spread,
                    'volume_volatility': np.std(volumes) / np.mean(volumes) if volumes else 0
                }
        
        return metrics
    
    def determine_severity(self, metrics: RiskMetrics) -> float:
        """Determine liquidity risk severity"""
        severity_factors = []
        
        # Volume ratio factor
        volume_ratio = metrics.custom_metrics.get('volume_ratio', 1.0)
        if volume_ratio < self.volume_threshold:
            vol_factor = (self.volume_threshold - volume_ratio) / self.volume_threshold
            severity_factors.append(vol_factor * 0.4)
        
        # Bid-ask spread factor
        spread = metrics.custom_metrics.get('bid_ask_spread', 0.01)
        if spread > self.spread_threshold:
            spread_factor = min(spread / self.spread_threshold, 3.0)
            severity_factors.append(spread_factor * 0.3)
        
        # Volume volatility factor
        vol_volatility = metrics.custom_metrics.get('volume_volatility', 0.0)
        if vol_volatility > 0.5:
            vol_vol_factor = min(vol_volatility / 0.5, 2.0)
            severity_factors.append(vol_vol_factor * 0.3)
        
        if severity_factors:
            return min(sum(severity_factors), 1.0)
        
        return 0.1
    
    def _calculate_liquidity_complexity(self, market_data: MarketData, historical_data: List[MarketData]) -> float:
        """Calculate liquidity complexity"""
        complexity_factors = []
        
        # Market cap complexity (smaller = more complex)
        # Note: This would need market cap data in practice
        complexity_factors.append(0.5)  # Default complexity
        
        # Volume pattern complexity
        if historical_data and len(historical_data) > 10:
            volumes = [d.volume for d in historical_data[-10:] if d.volume]
            if volumes:
                volume_changes = [abs(volumes[i] - volumes[i-1]) / volumes[i-1] for i in range(1, len(volumes))]
                pattern_complexity = np.std(volume_changes) * 5
                complexity_factors.append(min(pattern_complexity, 1.0) * 0.5)
        
        return min(sum(complexity_factors), 1.0)
    
    def _estimate_liquidity_frequency(self, historical_data: List[MarketData]) -> float:
        """Estimate liquidity crisis frequency"""
        if not historical_data or len(historical_data) < 10:
            return 0.1
        
        # Count low volume days
        volumes = [d.volume for d in historical_data if d.volume]
        if not volumes:
            return 0.1
        
        avg_volume = np.mean(volumes)
        low_volume_days = sum(1 for v in volumes if v < avg_volume * 0.5)
        
        return min(low_volume_days / len(volumes), 1.0)
    
    def _generate_liquidity_description(self, symbol: str, metrics: RiskMetrics, severity: float) -> str:
        """Generate liquidity risk description"""
        if severity < 0.3:
            risk_level = "낮음"
        elif severity < 0.6:
            risk_level = "보통"
        else:
            risk_level = "높음"
        
        volume_ratio = metrics.custom_metrics.get('volume_ratio', 1.0)
        spread = metrics.custom_metrics.get('bid_ask_spread', 0.01)
        
        description = f"{symbol} 유동성 리스크 수준: {risk_level}\n"
        description += f"거래량 비율: {volume_ratio:.1f}x\n"
        description += f"스프레드: {spread:.2%}\n"
        
        if volume_ratio < 0.5:
            description += "주의: 거래량 부족으로 인한 유동성 위험\n"
        
        return description


class RiskEventDetector:
    """Real-time risk event detection"""
    
    def __init__(self):
        self.alert_thresholds = {
            RiskEvent.VOLATILITY_SPIKE: 0.5,
            RiskEvent.PRICE_CRASH: -0.1,
            RiskEvent.VOLUME_ANOMALY: 3.0,
            RiskEvent.LIQUIDITY_CRISIS: 0.7,
            RiskEvent.FLASH_CRASH: -0.05
        }
        self.recent_data = {}
        self.alerts = []
    
    async def detect_events(self, symbol: str, current_data: MarketData, historical_data: List[MarketData]) -> List[RiskAlert]:
        """Detect risk events in real-time"""
        alerts = []
        
        # Store recent data
        if symbol not in self.recent_data:
            self.recent_data[symbol] = []
        
        self.recent_data[symbol].append(current_data)
        
        # Keep only last 100 data points
        if len(self.recent_data[symbol]) > 100:
            self.recent_data[symbol] = self.recent_data[symbol][-100:]
        
        # Check for various risk events
        alerts.extend(await self._detect_volatility_spike(symbol, current_data, historical_data))
        alerts.extend(await self._detect_price_crash(symbol, current_data))
        alerts.extend(await self._detect_volume_anomaly(symbol, current_data, historical_data))
        alerts.extend(await self._detect_liquidity_crisis(symbol, current_data, historical_data))
        alerts.extend(await self._detect_flash_crash(symbol, current_data))
        
        # Store alerts
        self.alerts.extend(alerts)
        
        # Keep only recent alerts (last 1000)
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        return alerts
    
    async def _detect_volatility_spike(self, symbol: str, current_data: MarketData, historical_data: List[MarketData]) -> List[RiskAlert]:
        """Detect volatility spikes"""
        alerts = []
        
        if not current_data.volatility:
            return alerts
        
        # Calculate average volatility
        if historical_data and len(historical_data) > 20:
            historical_volatilities = [d.volatility for d in historical_data[-20:] if d.volatility]
            if historical_volatilities:
                avg_volatility = np.mean(historical_volatilities)
                
                # Check for spike
                if current_data.volatility > avg_volatility * 2.0:
                    severity = min((current_data.volatility / avg_volatility) / 3.0, 1.0)
                    
                    alert = RiskAlert(
                        id=f"vol_spike_{symbol}_{int(datetime.now().timestamp())}",
                        event_type=RiskEvent.VOLATILITY_SPIKE,
                        severity=severity,
                        description=f"{symbol} 변동성 급등 감지: {current_data.volatility:.2%} (평균: {avg_volatility:.2%})",
                        affected_symbols=[symbol],
                        timestamp=datetime.now(),
                        data={
                            'current_volatility': current_data.volatility,
                            'avg_volatility': avg_volatility,
                            'spike_ratio': current_data.volatility / avg_volatility
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _detect_price_crash(self, symbol: str, current_data: MarketData) -> List[RiskAlert]:
        """Detect price crashes"""
        alerts = []
        
        if symbol not in self.recent_data or len(self.recent_data[symbol]) < 2:
            return alerts
        
        # Compare with previous data
        prev_data = self.recent_data[symbol][-2]
        
        if prev_data.close and current_data.close:
            price_change = (current_data.close - prev_data.close) / prev_data.close
            
            if price_change <= self.alert_thresholds[RiskEvent.PRICE_CRASH]:
                severity = min(abs(price_change) / 0.2, 1.0)
                
                alert = RiskAlert(
                    id=f"crash_{symbol}_{int(datetime.now().timestamp())}",
                    event_type=RiskEvent.PRICE_CRASH,
                    severity=severity,
                    description=f"{symbol} 가격 급락 감지: {price_change:.2%}",
                    affected_symbols=[symbol],
                    timestamp=datetime.now(),
                    data={
                        'price_change': price_change,
                        'prev_price': prev_data.close,
                        'current_price': current_data.close
                    }
                )
                alerts.append(alert)
        
        return alerts
    
    async def _detect_volume_anomaly(self, symbol: str, current_data: MarketData, historical_data: List[MarketData]) -> List[RiskAlert]:
        """Detect volume anomalies"""
        alerts = []
        
        if not current_data.volume:
            return alerts
        
        # Calculate average volume
        if historical_data and len(historical_data) > 20:
            historical_volumes = [d.volume for d in historical_data[-20:] if d.volume]
            if historical_volumes:
                avg_volume = np.mean(historical_volumes)
                
                # Check for anomaly
                volume_ratio = current_data.volume / avg_volume
                if volume_ratio >= self.alert_thresholds[RiskEvent.VOLUME_ANOMALY]:
                    severity = min(volume_ratio / 5.0, 1.0)
                    
                    alert = RiskAlert(
                        id=f"vol_anomaly_{symbol}_{int(datetime.now().timestamp())}",
                        event_type=RiskEvent.VOLUME_ANOMALY,
                        severity=severity,
                        description=f"{symbol} 거래량 이상 감지: {volume_ratio:.1f}x 증가",
                        affected_symbols=[symbol],
                        timestamp=datetime.now(),
                        data={
                            'current_volume': current_data.volume,
                            'avg_volume': avg_volume,
                            'volume_ratio': volume_ratio
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _detect_liquidity_crisis(self, symbol: str, current_data: MarketData, historical_data: List[MarketData]) -> List[RiskAlert]:
        """Detect liquidity crises"""
        alerts = []
        
        if not current_data.volume:
            return alerts
        
        # Check for extremely low volume
        if historical_data and len(historical_data) > 10:
            historical_volumes = [d.volume for d in historical_data[-10:] if d.volume]
            if historical_volumes:
                avg_volume = np.mean(historical_volumes)
                
                if current_data.volume < avg_volume * 0.1:  # Less than 10% of average
                    severity = min((avg_volume - current_data.volume) / avg_volume, 1.0)
                    
                    alert = RiskAlert(
                        id=f"liquidity_{symbol}_{int(datetime.now().timestamp())}",
                        event_type=RiskEvent.LIQUIDITY_CRISIS,
                        severity=severity,
                        description=f"{symbol} 유동성 위기 감지: 거래량 {current_data.volume/avg_volume:.1%}로 감소",
                        affected_symbols=[symbol],
                        timestamp=datetime.now(),
                        data={
                            'current_volume': current_data.volume,
                            'avg_volume': avg_volume,
                            'volume_ratio': current_data.volume / avg_volume
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    async def _detect_flash_crash(self, symbol: str, current_data: MarketData) -> List[RiskAlert]:
        """Detect flash crashes (rapid price movements)"""
        alerts = []
        
        if symbol not in self.recent_data or len(self.recent_data[symbol]) < 5:
            return alerts
        
        # Check last 5 minutes of data
        recent_prices = [d.close for d in self.recent_data[symbol][-5:] if d.close]
        
        if len(recent_prices) >= 3:
            # Check for rapid decline
            max_price = max(recent_prices)
            min_price = min(recent_prices)
            
            if max_price > 0:
                crash_magnitude = (max_price - min_price) / max_price
                
                if crash_magnitude >= abs(self.alert_thresholds[RiskEvent.FLASH_CRASH]):
                    severity = min(crash_magnitude / 0.1, 1.0)
                    
                    alert = RiskAlert(
                        id=f"flash_crash_{symbol}_{int(datetime.now().timestamp())}",
                        event_type=RiskEvent.FLASH_CRASH,
                        severity=severity,
                        description=f"{symbol} 플래시 크래시 감지: {crash_magnitude:.2%} 급락",
                        affected_symbols=[symbol],
                        timestamp=datetime.now(),
                        data={
                            'crash_magnitude': crash_magnitude,
                            'max_price': max_price,
                            'min_price': min_price,
                            'recent_prices': recent_prices
                        }
                    )
                    alerts.append(alert)
        
        return alerts
    
    def get_recent_alerts(self, hours: int = 24) -> List[RiskAlert]:
        """Get recent alerts within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp > cutoff_time]
    
    def get_alerts_by_symbol(self, symbol: str, hours: int = 24) -> List[RiskAlert]:
        """Get alerts for specific symbol"""
        recent_alerts = self.get_recent_alerts(hours)
        return [alert for alert in recent_alerts if symbol in alert.affected_symbols]