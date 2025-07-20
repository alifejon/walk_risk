"""
Specific market risk implementations
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np

from .base import Risk, RiskCategory, RiskLevel, RiskMetrics, RiskKey


@dataclass
class VolatilityRisk(Risk):
    """Volatility-specific risk with enhanced metrics"""
    
    def __init__(self, symbol: str, volatility_data: Dict[str, float], **kwargs):
        super().__init__(**kwargs)
        self.name = f"Volatility Risk - {symbol}"
        self.category = RiskCategory.MARKET
        self.symbol = symbol
        self.volatility_data = volatility_data
        self._calculate_volatility_metrics()
    
    def _calculate_volatility_metrics(self) -> None:
        """Calculate volatility-specific metrics"""
        current_vol = self.volatility_data.get('current_volatility', 0.0)
        historical_vol = self.volatility_data.get('historical_volatility', 0.0)
        
        # Enhanced volatility metrics
        self.metrics.custom_metrics.update({
            'volatility_ratio': current_vol / historical_vol if historical_vol > 0 else 1.0,
            'volatility_percentile': self.volatility_data.get('volatility_percentile', 50.0),
            'garch_volatility': self.volatility_data.get('garch_volatility', current_vol),
            'implied_volatility': self.volatility_data.get('implied_volatility', current_vol),
            'volatility_skew': self.volatility_data.get('volatility_skew', 0.0),
            'volatility_term_structure': self.volatility_data.get('term_structure', {})
        })
        
        # Update severity based on volatility
        vol_ratio = self.metrics.custom_metrics['volatility_ratio']
        if vol_ratio > 2.0:
            self.severity = min(vol_ratio / 3.0, 1.0)
        elif vol_ratio > 1.5:
            self.severity = 0.6
        else:
            self.severity = 0.3
    
    def get_volatility_forecast(self, days: int = 5) -> Dict[str, float]:
        """Get volatility forecast"""
        current_vol = self.volatility_data.get('current_volatility', 0.0)
        vol_ratio = self.metrics.custom_metrics.get('volatility_ratio', 1.0)
        
        # Simple mean reversion forecast
        forecast = {}
        for day in range(1, days + 1):
            # Mean reversion factor
            reversion = 0.95 ** day
            forecasted_vol = current_vol * (reversion * vol_ratio + (1 - reversion))
            forecast[f'day_{day}'] = forecasted_vol
        
        return forecast


@dataclass
class CorrelationRisk(Risk):
    """Correlation breakdown risk"""
    
    def __init__(self, symbol_pair: tuple, correlation_data: Dict[str, float], **kwargs):
        super().__init__(**kwargs)
        self.name = f"Correlation Risk - {symbol_pair[0]}/{symbol_pair[1]}"
        self.category = RiskCategory.MARKET
        self.symbol_pair = symbol_pair
        self.correlation_data = correlation_data
        self._calculate_correlation_metrics()
    
    def _calculate_correlation_metrics(self) -> None:
        """Calculate correlation-specific metrics"""
        current_corr = self.correlation_data.get('current_correlation', 0.0)
        historical_corr = self.correlation_data.get('historical_correlation', 0.0)
        
        # Correlation breakdown detection
        corr_change = abs(current_corr - historical_corr)
        
        self.metrics.custom_metrics.update({
            'correlation_change': corr_change,
            'correlation_stability': 1.0 - corr_change,
            'rolling_correlation': self.correlation_data.get('rolling_correlation', []),
            'correlation_volatility': self.correlation_data.get('correlation_volatility', 0.0),
            'tail_correlation': self.correlation_data.get('tail_correlation', current_corr)
        })
        
        # Update severity based on correlation breakdown
        if corr_change > 0.5:
            self.severity = min(corr_change, 1.0)
        else:
            self.severity = corr_change * 0.6
    
    def is_correlation_breakdown(self) -> bool:
        """Check if correlation has broken down"""
        corr_change = self.metrics.custom_metrics.get('correlation_change', 0.0)
        return corr_change > 0.4


@dataclass
class MomentumRisk(Risk):
    """Price momentum risk"""
    
    def __init__(self, symbol: str, momentum_data: Dict[str, float], **kwargs):
        super().__init__(**kwargs)
        self.name = f"Momentum Risk - {symbol}"
        self.category = RiskCategory.MARKET
        self.symbol = symbol
        self.momentum_data = momentum_data
        self._calculate_momentum_metrics()
    
    def _calculate_momentum_metrics(self) -> None:
        """Calculate momentum-specific metrics"""
        momentum = self.momentum_data.get('momentum', 0.0)
        momentum_strength = abs(momentum)
        
        self.metrics.custom_metrics.update({
            'momentum': momentum,
            'momentum_strength': momentum_strength,
            'momentum_direction': 1 if momentum > 0 else -1,
            'rsi': self.momentum_data.get('rsi', 50.0),
            'macd': self.momentum_data.get('macd', 0.0),
            'momentum_divergence': self.momentum_data.get('momentum_divergence', False),
            'trend_strength': self.momentum_data.get('trend_strength', 0.5)
        })
        
        # Momentum risk increases with extreme momentum
        rsi = self.metrics.custom_metrics['rsi']
        if rsi > 80 or rsi < 20:
            self.severity = min((abs(rsi - 50) - 30) / 20, 1.0)
        else:
            self.severity = momentum_strength
    
    def is_momentum_exhaustion(self) -> bool:
        """Check if momentum is showing signs of exhaustion"""
        rsi = self.metrics.custom_metrics.get('rsi', 50.0)
        divergence = self.metrics.custom_metrics.get('momentum_divergence', False)
        
        return (rsi > 80 or rsi < 20) and divergence


@dataclass
class LiquidityRisk(Risk):
    """Market liquidity risk"""
    
    def __init__(self, symbol: str, liquidity_data: Dict[str, float], **kwargs):
        super().__init__(**kwargs)
        self.name = f"Liquidity Risk - {symbol}"
        self.category = RiskCategory.LIQUIDITY
        self.symbol = symbol
        self.liquidity_data = liquidity_data
        self._calculate_liquidity_metrics()
    
    def _calculate_liquidity_metrics(self) -> None:
        """Calculate liquidity-specific metrics"""
        volume_ratio = self.liquidity_data.get('volume_ratio', 1.0)
        bid_ask_spread = self.liquidity_data.get('bid_ask_spread', 0.01)
        
        self.metrics.custom_metrics.update({
            'volume_ratio': volume_ratio,
            'bid_ask_spread': bid_ask_spread,
            'market_depth': self.liquidity_data.get('market_depth', 1.0),
            'turnover_ratio': self.liquidity_data.get('turnover_ratio', 1.0),
            'price_impact': self.liquidity_data.get('price_impact', 0.0),
            'liquidity_score': self._calculate_liquidity_score(),
            'illiquidity_ratio': self.liquidity_data.get('illiquidity_ratio', 0.0)
        })
        
        # Liquidity risk severity
        liquidity_score = self.metrics.custom_metrics['liquidity_score']
        self.severity = max(1.0 - liquidity_score, 0.1)
    
    def _calculate_liquidity_score(self) -> float:
        """Calculate overall liquidity score (0-1, higher is better)"""
        volume_ratio = self.liquidity_data.get('volume_ratio', 1.0)
        bid_ask_spread = self.liquidity_data.get('bid_ask_spread', 0.01)
        market_depth = self.liquidity_data.get('market_depth', 1.0)
        
        # Volume component (0-1)
        volume_score = min(volume_ratio, 2.0) / 2.0
        
        # Spread component (0-1, lower spread is better)
        spread_score = max(0, 1.0 - bid_ask_spread / 0.05)  # 5% spread = 0 score
        
        # Depth component (0-1)
        depth_score = min(market_depth, 2.0) / 2.0
        
        # Weighted average
        return (volume_score * 0.4 + spread_score * 0.4 + depth_score * 0.2)
    
    def get_liquidity_level(self) -> str:
        """Get liquidity level description"""
        score = self.metrics.custom_metrics.get('liquidity_score', 0.5)
        
        if score > 0.8:
            return "높음"
        elif score > 0.6:
            return "보통"
        elif score > 0.4:
            return "낮음"
        else:
            return "매우 낮음"


@dataclass
class ConcentrationRisk(Risk):
    """Portfolio concentration risk"""
    
    def __init__(self, portfolio_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.name = "Concentration Risk"
        self.category = RiskCategory.MARKET
        self.portfolio_data = portfolio_data
        self._calculate_concentration_metrics()
    
    def _calculate_concentration_metrics(self) -> None:
        """Calculate concentration-specific metrics"""
        weights = self.portfolio_data.get('weights', [])
        sectors = self.portfolio_data.get('sectors', [])
        
        if weights:
            # Herfindahl-Hirschman Index
            hhi = sum(w**2 for w in weights)
            
            # Top N concentration
            sorted_weights = sorted(weights, reverse=True)
            top_3_concentration = sum(sorted_weights[:3]) if len(sorted_weights) >= 3 else sum(sorted_weights)
            top_5_concentration = sum(sorted_weights[:5]) if len(sorted_weights) >= 5 else sum(sorted_weights)
            
            # Sector concentration
            sector_concentration = self._calculate_sector_concentration(sectors, weights)
            
            self.metrics.custom_metrics.update({
                'hhi': hhi,
                'top_3_concentration': top_3_concentration,
                'top_5_concentration': top_5_concentration,
                'sector_concentration': sector_concentration,
                'diversification_ratio': 1.0 / hhi if hhi > 0 else 0,
                'effective_positions': 1.0 / hhi if hhi > 0 else len(weights)
            })
            
            # Concentration risk severity
            if hhi > 0.5:  # Highly concentrated
                self.severity = min(hhi, 1.0)
            elif top_3_concentration > 0.6:
                self.severity = top_3_concentration
            else:
                self.severity = hhi * 0.8
    
    def _calculate_sector_concentration(self, sectors: List[str], weights: List[float]) -> Dict[str, float]:
        """Calculate sector concentration"""
        if not sectors or not weights or len(sectors) != len(weights):
            return {}
        
        sector_weights = {}
        for sector, weight in zip(sectors, weights):
            sector_weights[sector] = sector_weights.get(sector, 0) + weight
        
        return sector_weights
    
    def get_concentration_level(self) -> str:
        """Get concentration level description"""
        hhi = self.metrics.custom_metrics.get('hhi', 0.0)
        
        if hhi > 0.25:
            return "매우 높음"
        elif hhi > 0.15:
            return "높음"
        elif hhi > 0.1:
            return "보통"
        else:
            return "낮음"


class RiskMetricsCalculator:
    """Utility class for calculating advanced risk metrics"""
    
    @staticmethod
    def calculate_var(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index]) if index < len(sorted_returns) else 0.0
    
    @staticmethod
    def calculate_cvar(returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        if not returns:
            return 0.0
        
        sorted_returns = sorted(returns)
        cutoff_index = int((1 - confidence) * len(sorted_returns))
        
        if cutoff_index == 0:
            return abs(sorted_returns[0])
        
        tail_returns = sorted_returns[:cutoff_index]
        return abs(np.mean(tail_returns)) if tail_returns else 0.0
    
    @staticmethod
    def calculate_maximum_drawdown(prices: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(prices) < 2:
            return 0.0
        
        peak = prices[0]
        max_drawdown = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return max_drawdown
    
    @staticmethod
    def calculate_beta(asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta coefficient"""
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0
        
        asset_returns = np.array(asset_returns)
        market_returns = np.array(market_returns)
        
        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        return covariance / market_variance if market_variance > 0 else 1.0
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if not returns:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Assuming daily returns
        mean_excess = np.mean(excess_returns)
        std_excess = np.std(excess_returns)
        
        return mean_excess / std_excess if std_excess > 0 else 0.0
    
    @staticmethod
    def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]
        downside_returns = [r for r in excess_returns if r < 0]
        
        mean_excess = np.mean(excess_returns)
        downside_std = np.std(downside_returns) if downside_returns else 0.0
        
        return mean_excess / downside_std if downside_std > 0 else float('inf')
    
    @staticmethod
    def calculate_calmar_ratio(returns: List[float], prices: List[float]) -> float:
        """Calculate Calmar ratio"""
        if not returns or not prices:
            return 0.0
        
        annual_return = np.mean(returns) * 252  # Assuming daily returns
        max_drawdown = RiskMetricsCalculator.calculate_maximum_drawdown(prices)
        
        return annual_return / max_drawdown if max_drawdown > 0 else float('inf')