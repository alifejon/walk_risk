"""
Portfolio management system integration
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from .portfolio import Portfolio
from .assets import Asset, AssetType, Stock, Bond, ETF, Cash
from ...data.sources.data_manager import DataManager
from ...utils.logger import logger


class PortfolioManager:
    """Manages portfolios for all players"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.portfolios: Dict[str, Portfolio] = {}  # player_id -> Portfolio
        self.market_prices: Dict[str, Decimal] = {}
        self._is_running = False
        self._background_tasks: List[asyncio.Task] = []
    
    async def start(self) -> None:
        """Start portfolio manager"""
        self._is_running = True
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._price_update_loop()),
            asyncio.create_task(self._portfolio_update_loop())
        ]
        
        logger.info("Portfolio manager started")
    
    async def stop(self) -> None:
        """Stop portfolio manager"""
        self._is_running = False
        
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
        logger.info("Portfolio manager stopped")
    
    async def _price_update_loop(self) -> None:
        """Background task to update market prices"""
        while self._is_running:
            try:
                await self._update_market_prices()
                await asyncio.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Price update error: {e}")
                await asyncio.sleep(10)
    
    async def _portfolio_update_loop(self) -> None:
        """Background task to update portfolio metrics"""
        while self._is_running:
            try:
                await self._update_all_portfolios()
                await asyncio.sleep(300)  # Update every 5 minutes
            except Exception as e:
                logger.error(f"Portfolio update error: {e}")
                await asyncio.sleep(30)
    
    async def _update_market_prices(self) -> None:
        """Update market prices from data sources"""
        try:
            # Get all unique symbols from all portfolios
            symbols = set()
            for portfolio in self.portfolios.values():
                for asset in portfolio.assets.values():
                    if asset.asset_type != AssetType.CASH:
                        symbols.add(asset.symbol)
            
            # Update prices for each symbol
            price_updates = {}
            for symbol in symbols:
                try:
                    market_data = await self.data_manager.get_current_data(symbol)
                    if market_data and market_data.price:
                        price_updates[symbol] = Decimal(str(market_data.price))
                        self.market_prices[symbol] = Decimal(str(market_data.price))
                except Exception as e:
                    logger.warning(f"Failed to get price for {symbol}: {e}")
            
            # Update portfolios with new prices
            for portfolio in self.portfolios.values():
                portfolio.update_asset_prices(price_updates)
            
            if price_updates:
                logger.debug(f"Updated prices for {len(price_updates)} symbols")
                
        except Exception as e:
            logger.error(f"Market price update failed: {e}")
    
    async def _update_all_portfolios(self) -> None:
        """Update all portfolio metrics"""
        for portfolio in self.portfolios.values():
            try:
                portfolio._update_metrics()
            except Exception as e:
                logger.error(f"Portfolio update failed for {portfolio.id}: {e}")
    
    def create_portfolio(self, player_id: str, name: str = "Main Portfolio", initial_cash: Decimal = Decimal('100000')) -> Portfolio:
        """Create new portfolio for player"""
        if player_id in self.portfolios:
            logger.warning(f"Portfolio already exists for player {player_id}")
            return self.portfolios[player_id]
        
        portfolio = Portfolio(player_id, name, initial_cash)
        self.portfolios[player_id] = portfolio
        
        logger.info(f"Created portfolio for player {player_id} with ${initial_cash} cash")
        return portfolio
    
    def get_portfolio(self, player_id: str) -> Optional[Portfolio]:
        """Get portfolio for player"""
        return self.portfolios.get(player_id)
    
    async def buy_asset_for_player(
        self, 
        player_id: str, 
        symbol: str, 
        quantity: Decimal, 
        asset_type: AssetType = AssetType.STOCK
    ) -> bool:
        """Buy asset for player at current market price"""
        portfolio = self.get_portfolio(player_id)
        if not portfolio:
            logger.error(f"No portfolio found for player {player_id}")
            return False
        
        try:
            # Get current market price
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                logger.error(f"Could not get price for {symbol}")
                return False
            
            # Execute buy order
            success = portfolio.buy_asset(symbol, quantity, current_price)
            
            if success:
                logger.info(f"Player {player_id} bought {quantity} of {symbol} at ${current_price}")
                
                # Trigger achievement check
                await self._check_trading_achievements(portfolio, "BUY", symbol, quantity, current_price)
            
            return success
            
        except Exception as e:
            logger.error(f"Buy order failed: {e}")
            return False
    
    async def sell_asset_for_player(
        self, 
        player_id: str, 
        symbol: str, 
        quantity: Decimal
    ) -> bool:
        """Sell asset for player at current market price"""
        portfolio = self.get_portfolio(player_id)
        if not portfolio:
            logger.error(f"No portfolio found for player {player_id}")
            return False
        
        try:
            # Get current market price
            current_price = await self._get_current_price(symbol)
            if current_price is None:
                logger.error(f"Could not get price for {symbol}")
                return False
            
            # Execute sell order
            success = portfolio.sell_asset(symbol, quantity, current_price)
            
            if success:
                logger.info(f"Player {player_id} sold {quantity} of {symbol} at ${current_price}")
                
                # Trigger achievement check
                await self._check_trading_achievements(portfolio, "SELL", symbol, quantity, current_price)
            
            return success
            
        except Exception as e:
            logger.error(f"Sell order failed: {e}")
            return False
    
    async def _get_current_price(self, symbol: str) -> Optional[Decimal]:
        """Get current market price for symbol"""
        try:
            # Try cached price first
            if symbol in self.market_prices:
                return self.market_prices[symbol]
            
            # Get from data source
            market_data = await self.data_manager.get_current_data(symbol)
            if market_data and market_data.price:
                price = Decimal(str(market_data.price))
                self.market_prices[symbol] = price
                return price
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            return None
    
    async def _check_trading_achievements(
        self, 
        portfolio: Portfolio, 
        action: str, 
        symbol: str, 
        quantity: Decimal, 
        price: Decimal
    ) -> None:
        """Check for trading-related achievements"""
        try:
            total_value = float(quantity * price)
            
            # Large trade achievements
            if "large_trade_10k" not in portfolio.achievements and total_value >= 10000:
                portfolio.achievements.append("large_trade_10k")
                portfolio.experience += 200
                logger.info(f"Achievement unlocked: large_trade_10k")
            
            if "large_trade_100k" not in portfolio.achievements and total_value >= 100000:
                portfolio.achievements.append("large_trade_100k")
                portfolio.experience += 500
                logger.info(f"Achievement unlocked: large_trade_100k")
            
            # Frequent trader achievements
            trade_count = len(portfolio.transaction_history)
            milestones = [(10, "frequent_trader_10"), (50, "frequent_trader_50"), (100, "frequent_trader_100")]
            
            for count, achievement in milestones:
                if achievement not in portfolio.achievements and trade_count >= count:
                    portfolio.achievements.append(achievement)
                    portfolio.experience += count * 2
                    logger.info(f"Achievement unlocked: {achievement}")
            
            # Blue chip stock bonus
            blue_chip_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ']
            if symbol in blue_chip_symbols and "blue_chip_investor" not in portfolio.achievements:
                portfolio.achievements.append("blue_chip_investor")
                portfolio.experience += 100
                logger.info(f"Achievement unlocked: blue_chip_investor")
            
        except Exception as e:
            logger.error(f"Achievement check failed: {e}")
    
    def get_market_data_for_portfolio(self, player_id: str) -> Dict[str, Any]:
        """Get market data relevant to player's portfolio"""
        portfolio = self.get_portfolio(player_id)
        if not portfolio:
            return {}
        
        market_data = {}
        for asset in portfolio.assets.values():
            if asset.asset_type != AssetType.CASH and asset.symbol in self.market_prices:
                market_data[asset.symbol] = {
                    'current_price': float(self.market_prices[asset.symbol]),
                    'owned_quantity': float(asset.quantity),
                    'market_value': float(asset.stats.market_value),
                    'total_return': float(asset.stats.total_return),
                    'daily_return': float(asset.stats.daily_return),
                    'game_stats': {
                        'attack_power': asset.stats.attack_power,
                        'defense_power': asset.stats.defense_power,
                        'magic_power': asset.stats.magic_power,
                        'durability': asset.stats.durability,
                        'level': asset.level
                    }
                }
        
        return market_data
    
    def get_portfolio_leaderboard(self, metric: str = "total_return_percentage") -> List[Dict[str, Any]]:
        """Get portfolio leaderboard"""
        leaderboard = []
        
        for portfolio in self.portfolios.values():
            if metric == "total_return_percentage":
                score = float(portfolio.metrics.total_return_percentage)
            elif metric == "total_value":
                score = float(portfolio.metrics.total_value)
            elif metric == "game_score":
                score = portfolio.metrics.calculate_game_score()
            else:
                score = 0
            
            leaderboard.append({
                'player_id': portfolio.player_id,
                'portfolio_name': portfolio.name,
                'score': score,
                'total_value': float(portfolio.metrics.total_value),
                'total_return': float(portfolio.metrics.total_return_percentage),
                'game_score': portfolio.metrics.calculate_game_score(),
                'level': portfolio.level
            })
        
        # Sort by score descending
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rankings
        for i, entry in enumerate(leaderboard):
            entry['rank'] = i + 1
        
        return leaderboard
    
    async def simulate_market_scenario(self, scenario: str, intensity: float = 1.0) -> Dict[str, Any]:
        """Simulate market scenario for all portfolios"""
        results = {}
        
        try:
            # Apply scenario effects to market prices
            price_changes = {}
            
            if scenario == "market_crash":
                # Simulate market crash: stocks down 10-30%, bonds up slightly
                for symbol, price in self.market_prices.items():
                    if symbol in ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL']:  # Stocks
                        change = -0.1 * intensity - (0.2 * intensity * (hash(symbol) % 100 / 100))
                        price_changes[symbol] = price * (1 + Decimal(str(change)))
                    elif symbol.startswith('T'):  # Bonds
                        change = 0.02 * intensity
                        price_changes[symbol] = price * (1 + Decimal(str(change)))
            
            elif scenario == "bull_rally":
                # Simulate bull rally: stocks up 5-15%
                for symbol, price in self.market_prices.items():
                    if not symbol.startswith('T'):  # Not bonds
                        change = 0.05 * intensity + (0.1 * intensity * (hash(symbol) % 100 / 100))
                        price_changes[symbol] = price * (1 + Decimal(str(change)))
            
            elif scenario == "volatility_spike":
                # Simulate high volatility: random movements
                for symbol, price in self.market_prices.items():
                    change = (hash(symbol + scenario) % 200 - 100) / 1000 * intensity  # -10% to +10%
                    price_changes[symbol] = price * (1 + Decimal(str(change)))
            
            # Update portfolios with scenario prices
            portfolio_results = {}
            for player_id, portfolio in self.portfolios.items():
                old_value = portfolio.metrics.total_value
                portfolio.update_asset_prices(price_changes)
                new_value = portfolio.metrics.total_value
                
                portfolio_results[player_id] = {
                    'old_value': float(old_value),
                    'new_value': float(new_value),
                    'change': float(new_value - old_value),
                    'change_percentage': float((new_value - old_value) / old_value) if old_value > 0 else 0,
                    'game_score_change': portfolio.metrics.calculate_game_score()
                }
            
            results = {
                'scenario': scenario,
                'intensity': intensity,
                'price_changes': {k: float(v) for k, v in price_changes.items()},
                'portfolio_results': portfolio_results,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Simulated market scenario: {scenario} (intensity: {intensity})")
            
        except Exception as e:
            logger.error(f"Market scenario simulation failed: {e}")
            results = {'error': str(e)}
        
        return results
    
    def get_portfolio_statistics(self) -> Dict[str, Any]:
        """Get aggregate portfolio statistics"""
        if not self.portfolios:
            return {}
        
        total_value = sum(float(p.metrics.total_value) for p in self.portfolios.values())
        total_return = sum(float(p.metrics.total_return) for p in self.portfolios.values())
        avg_return_pct = sum(float(p.metrics.total_return_percentage) for p in self.portfolios.values()) / len(self.portfolios)
        
        # Asset type distribution
        asset_type_totals = {}
        for portfolio in self.portfolios.values():
            for asset_type, allocation in portfolio.metrics.allocation_by_type.items():
                asset_type_totals[asset_type] = asset_type_totals.get(asset_type, 0) + float(allocation * portfolio.metrics.total_value)
        
        return {
            'total_portfolios': len(self.portfolios),
            'total_value': total_value,
            'total_return': total_return,
            'average_return_percentage': avg_return_pct,
            'asset_type_distribution': asset_type_totals,
            'top_performers': self.get_portfolio_leaderboard("total_return_percentage")[:5],
            'market_prices_count': len(self.market_prices)
        }