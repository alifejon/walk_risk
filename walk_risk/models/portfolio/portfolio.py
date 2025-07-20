"""
Portfolio management system - Player inventory
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum
import uuid

from .assets import Asset, AssetType, AssetStatus, Stock, Bond, Cash, ETF
from ...utils.logger import logger


class PortfolioStatus(Enum):
    """Portfolio status"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class RebalanceStrategy(Enum):
    """Portfolio rebalancing strategies"""
    NONE = "none"
    PERIODIC = "periodic"
    THRESHOLD = "threshold"
    TACTICAL = "tactical"


@dataclass
class PortfolioAllocation:
    """Target allocation for portfolio"""
    asset_type: AssetType
    target_percentage: Decimal
    min_percentage: Decimal
    max_percentage: Decimal
    
    def is_within_bounds(self, current_percentage: Decimal) -> bool:
        """Check if current allocation is within bounds"""
        return self.min_percentage <= current_percentage <= self.max_percentage


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics"""
    total_value: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    total_return: Decimal = Decimal('0')
    total_return_percentage: Decimal = Decimal('0')
    daily_return: Decimal = Decimal('0')
    
    # Risk metrics
    volatility: Decimal = Decimal('0')
    sharpe_ratio: Decimal = Decimal('0')
    max_drawdown: Decimal = Decimal('0')
    var_95: Decimal = Decimal('0')
    beta: Decimal = Decimal('1.0')
    
    # Game metrics
    total_attack_power: int = 0
    total_defense_power: int = 0
    total_magic_power: int = 0
    average_durability: int = 100
    
    # Allocation metrics
    allocation_by_type: Dict[str, Decimal] = field(default_factory=dict)
    concentration_risk: Decimal = Decimal('0')
    diversification_score: int = 0
    
    def calculate_game_score(self) -> int:
        """Calculate overall portfolio game score"""
        # Balance between offensive and defensive capabilities
        balance_score = min(self.total_attack_power, self.total_defense_power)
        
        # Bonus for diversification
        diversification_bonus = self.diversification_score * 2
        
        # Penalty for poor durability
        durability_penalty = max(0, (100 - self.average_durability) * 2)
        
        return max(0, balance_score + diversification_bonus - durability_penalty)


class Portfolio:
    """Portfolio class - Player's inventory system"""
    
    def __init__(
        self, 
        player_id: str, 
        name: str = "Main Portfolio",
        initial_cash: Decimal = Decimal('100000')
    ):
        self.id = str(uuid.uuid4())
        self.player_id = player_id
        self.name = name
        self.status = PortfolioStatus.ACTIVE
        
        # Portfolio holdings
        self.assets: Dict[str, Asset] = {}
        self.transaction_history: List[Dict[str, Any]] = []
        
        # Strategy and allocation
        self.target_allocations: List[PortfolioAllocation] = []
        self.rebalance_strategy = RebalanceStrategy.NONE
        self.last_rebalance_date: Optional[datetime] = None
        
        # Performance tracking
        self.metrics = PortfolioMetrics()
        self.historical_values: List[Tuple[datetime, Decimal]] = []
        
        # Game features
        self.level = 1
        self.experience = 0
        self.achievements: List[str] = []
        self.portfolio_bonuses: List[str] = []
        
        # Metadata
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        # Initialize with cash
        if initial_cash > 0:
            self._add_initial_cash(initial_cash)
    
    def _add_initial_cash(self, amount: Decimal) -> None:
        """Add initial cash to portfolio"""
        cash = Cash()
        cash.quantity = amount
        cash.status = AssetStatus.OWNED
        cash.purchase_date = datetime.now()
        cash.stats.current_price = Decimal('1')
        cash.stats.market_value = amount
        self.assets[cash.id] = cash
    
    def add_asset(self, asset: Asset) -> bool:
        """Add asset to portfolio"""
        try:
            self.assets[asset.id] = asset
            self._record_transaction("ADD", asset, asset.quantity, asset.stats.current_price)
            self._update_metrics()
            logger.info(f"Added asset to portfolio: {asset.symbol}")
            return True
        except Exception as e:
            logger.error(f"Failed to add asset: {e}")
            return False
    
    def remove_asset(self, asset_id: str) -> bool:
        """Remove asset from portfolio"""
        try:
            if asset_id in self.assets:
                asset = self.assets[asset_id]
                self._record_transaction("REMOVE", asset, asset.quantity, asset.stats.current_price)
                del self.assets[asset_id]
                self._update_metrics()
                logger.info(f"Removed asset from portfolio: {asset.symbol}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove asset: {e}")
            return False
    
    def buy_asset(self, symbol: str, quantity: Decimal, price: Decimal) -> bool:
        """Buy asset - Game equivalent of acquiring new equipment"""
        try:
            total_cost = quantity * price
            
            # Check if enough cash
            cash_available = self.get_cash_balance()
            if cash_available < total_cost:
                logger.warning(f"Insufficient cash: need {total_cost}, have {cash_available}")
                return False
            
            # Deduct cash
            if not self._deduct_cash(total_cost):
                return False
            
            # Find existing asset or create new one
            existing_asset = self.get_asset_by_symbol(symbol)
            
            if existing_asset and existing_asset.status == AssetStatus.OWNED:
                # Add to existing position (like upgrading equipment)
                old_quantity = existing_asset.quantity
                old_cost = existing_asset.average_cost
                
                # Calculate new average cost
                total_quantity = old_quantity + quantity
                total_value = (old_quantity * old_cost) + (quantity * price)
                new_average_cost = total_value / total_quantity
                
                existing_asset.quantity = total_quantity
                existing_asset.average_cost = new_average_cost
                existing_asset.stats.purchase_price = new_average_cost
                existing_asset.stats.market_value = total_quantity * existing_asset.stats.current_price
                
                # Gain experience for upgrading
                existing_asset.gain_experience(int(float(quantity)) * 10)
                
            else:
                # Create new asset
                if symbol.startswith(('BOND', 'T')):  # Simple bond detection
                    asset = Bond(symbol, f"{symbol} Bond")
                elif symbol in ['SPY', 'QQQ', 'VTI']:  # Simple ETF detection
                    asset = ETF(symbol, f"{symbol} ETF")
                else:
                    asset = Stock(symbol, f"{symbol} Stock")
                
                asset.quantity = quantity
                asset.average_cost = price
                asset.stats.purchase_price = price
                asset.stats.current_price = price
                asset.stats.market_value = quantity * price
                asset.status = AssetStatus.OWNED
                asset.purchase_date = datetime.now()
                
                self.assets[asset.id] = asset
            
            # Record transaction
            self._record_transaction("BUY", existing_asset or asset, quantity, price)
            
            # Update portfolio metrics
            self._update_metrics()
            
            # Check for achievements
            self._check_achievements()
            
            logger.info(f"Bought {quantity} shares of {symbol} at ${price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to buy asset: {e}")
            return False
    
    def sell_asset(self, symbol: str, quantity: Decimal, price: Decimal) -> bool:
        """Sell asset - Game equivalent of selling equipment"""
        try:
            asset = self.get_asset_by_symbol(symbol)
            if not asset or asset.status != AssetStatus.OWNED:
                logger.warning(f"Asset not found or not owned: {symbol}")
                return False
            
            if asset.quantity < quantity:
                logger.warning(f"Insufficient quantity: have {asset.quantity}, trying to sell {quantity}")
                return False
            
            # Calculate proceeds
            proceeds = quantity * price
            
            # Add cash back
            self._add_cash(proceeds)
            
            # Update asset quantity
            asset.quantity -= quantity
            
            if asset.quantity == 0:
                # Fully sold
                asset.status = AssetStatus.SOLD
            
            # Update market value
            asset.stats.market_value = asset.quantity * asset.stats.current_price
            
            # Record transaction
            self._record_transaction("SELL", asset, quantity, price)
            
            # Calculate realized gain/loss
            cost_basis = quantity * asset.average_cost
            realized_pnl = proceeds - cost_basis
            
            # Gain experience based on performance
            if realized_pnl > 0:
                asset.gain_experience(int(float(realized_pnl)) // 100)
                self.experience += int(float(realized_pnl)) // 100
            
            # Update portfolio metrics
            self._update_metrics()
            
            logger.info(f"Sold {quantity} shares of {symbol} at ${price} (P&L: ${realized_pnl:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sell asset: {e}")
            return False
    
    def get_asset_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Get asset by symbol"""
        for asset in self.assets.values():
            if asset.symbol == symbol and asset.status == AssetStatus.OWNED:
                return asset
        return None
    
    def get_cash_balance(self) -> Decimal:
        """Get total cash balance"""
        cash_assets = [a for a in self.assets.values() 
                      if a.asset_type == AssetType.CASH and a.status == AssetStatus.OWNED]
        return sum(asset.quantity for asset in cash_assets)
    
    def _deduct_cash(self, amount: Decimal) -> bool:
        """Deduct cash from portfolio"""
        cash_assets = [a for a in self.assets.values() 
                      if a.asset_type == AssetType.CASH and a.status == AssetStatus.OWNED]
        
        total_cash = sum(asset.quantity for asset in cash_assets)
        if total_cash < amount:
            return False
        
        # Deduct from first available cash asset
        for asset in cash_assets:
            if asset.quantity >= amount:
                asset.quantity -= amount
                asset.stats.market_value = asset.quantity
                return True
            else:
                amount -= asset.quantity
                asset.quantity = Decimal('0')
                asset.stats.market_value = Decimal('0')
        
        return True
    
    def _add_cash(self, amount: Decimal) -> None:
        """Add cash to portfolio"""
        # Find existing cash asset or create new one
        cash_assets = [a for a in self.assets.values() 
                      if a.asset_type == AssetType.CASH and a.status == AssetStatus.OWNED]
        
        if cash_assets:
            cash_assets[0].quantity += amount
            cash_assets[0].stats.market_value = cash_assets[0].quantity
        else:
            cash = Cash()
            cash.quantity = amount
            cash.status = AssetStatus.OWNED
            cash.purchase_date = datetime.now()
            cash.stats.current_price = Decimal('1')
            cash.stats.market_value = amount
            self.assets[cash.id] = cash
    
    def _record_transaction(self, action: str, asset: Asset, quantity: Decimal, price: Decimal) -> None:
        """Record transaction in history"""
        transaction = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'symbol': asset.symbol,
            'asset_type': asset.asset_type.value,
            'quantity': str(quantity),
            'price': str(price),
            'total_value': str(quantity * price)
        }
        self.transaction_history.append(transaction)
    
    def _update_metrics(self) -> None:
        """Update portfolio metrics"""
        try:
            owned_assets = [a for a in self.assets.values() if a.status == AssetStatus.OWNED]
            
            # Calculate total values
            total_value = sum(asset.stats.market_value for asset in owned_assets)
            total_cost = sum(asset.quantity * asset.average_cost for asset in owned_assets 
                           if asset.asset_type != AssetType.CASH)
            
            self.metrics.total_value = total_value
            self.metrics.total_cost = total_cost
            
            if total_cost > 0:
                self.metrics.total_return = total_value - total_cost
                self.metrics.total_return_percentage = self.metrics.total_return / total_cost
            
            # Calculate game stats
            self.metrics.total_attack_power = sum(asset.stats.attack_power for asset in owned_assets)
            self.metrics.total_defense_power = sum(asset.stats.defense_power for asset in owned_assets)
            self.metrics.total_magic_power = sum(asset.stats.magic_power for asset in owned_assets)
            
            if owned_assets:
                self.metrics.average_durability = int(sum(asset.stats.durability for asset in owned_assets) / len(owned_assets))
            
            # Calculate allocation by type
            allocation = {}
            for asset_type in AssetType:
                type_value = sum(asset.stats.market_value for asset in owned_assets 
                               if asset.asset_type == asset_type)
                if total_value > 0:
                    allocation[asset_type.value] = type_value / total_value
                else:
                    allocation[asset_type.value] = Decimal('0')
            
            self.metrics.allocation_by_type = allocation
            
            # Calculate diversification score
            non_cash_assets = [a for a in owned_assets if a.asset_type != AssetType.CASH]
            self.metrics.diversification_score = len(non_cash_assets)
            
            # Calculate concentration risk (Herfindahl index)
            if non_cash_assets:
                weights = [asset.stats.market_value / total_value for asset in non_cash_assets]
                hhi = sum(w * w for w in weights)
                self.metrics.concentration_risk = hhi
            
            self.last_updated = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to update portfolio metrics: {e}")
    
    def _check_achievements(self) -> None:
        """Check for portfolio achievements"""
        new_achievements = []
        
        # First purchase achievement
        if "first_purchase" not in self.achievements:
            non_cash_assets = [a for a in self.assets.values() 
                             if a.asset_type != AssetType.CASH and a.status == AssetStatus.OWNED]
            if non_cash_assets:
                new_achievements.append("first_purchase")
        
        # Diversification achievements
        asset_types = set(a.asset_type for a in self.assets.values() if a.status == AssetStatus.OWNED)
        if "diversified_investor" not in self.achievements and len(asset_types) >= 3:
            new_achievements.append("diversified_investor")
        
        # Portfolio value milestones
        total_value = float(self.metrics.total_value)
        milestones = [
            (10000, "portfolio_10k"),
            (50000, "portfolio_50k"),
            (100000, "portfolio_100k"),
            (500000, "portfolio_500k"),
            (1000000, "portfolio_1m")
        ]
        
        for value, achievement in milestones:
            if achievement not in self.achievements and total_value >= value:
                new_achievements.append(achievement)
        
        # Add new achievements
        for achievement in new_achievements:
            self.achievements.append(achievement)
            self.experience += 100  # Bonus experience for achievements
            logger.info(f"Portfolio achievement unlocked: {achievement}")
    
    def update_asset_prices(self, price_updates: Dict[str, Decimal]) -> None:
        """Update asset prices from market data"""
        for symbol, new_price in price_updates.items():
            asset = self.get_asset_by_symbol(symbol)
            if asset:
                asset.update_price(new_price)
                
                # Gain experience for holding assets
                if asset.status == AssetStatus.OWNED:
                    asset.gain_experience(1)  # Small experience for each price update
        
        self._update_metrics()
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary for display"""
        owned_assets = [a for a in self.assets.values() if a.status == AssetStatus.OWNED]
        
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'total_value': float(self.metrics.total_value),
            'total_return': float(self.metrics.total_return),
            'total_return_percentage': float(self.metrics.total_return_percentage),
            'cash_balance': float(self.get_cash_balance()),
            'asset_count': len(owned_assets),
            'game_stats': {
                'attack_power': self.metrics.total_attack_power,
                'defense_power': self.metrics.total_defense_power,
                'magic_power': self.metrics.total_magic_power,
                'durability': self.metrics.average_durability,
                'game_score': self.metrics.calculate_game_score()
            },
            'allocation': {k: float(v) for k, v in self.metrics.allocation_by_type.items()},
            'diversification_score': self.metrics.diversification_score,
            'achievements': self.achievements,
            'level': self.level,
            'experience': self.experience
        }
    
    def get_asset_list(self) -> List[Dict[str, Any]]:
        """Get list of owned assets"""
        owned_assets = [a for a in self.assets.values() if a.status == AssetStatus.OWNED]
        return [asset.to_dict() for asset in owned_assets]
    
    def rebalance_portfolio(self, target_allocations: Dict[AssetType, Decimal]) -> List[str]:
        """Rebalance portfolio to target allocations"""
        actions = []
        total_value = self.metrics.total_value
        
        if total_value == 0:
            return ["Cannot rebalance empty portfolio"]
        
        current_allocations = {}
        target_values = {}
        
        # Calculate current and target values
        for asset_type, target_pct in target_allocations.items():
            current_value = sum(
                asset.stats.market_value for asset in self.assets.values()
                if asset.asset_type == asset_type and asset.status == AssetStatus.OWNED
            )
            current_allocations[asset_type] = current_value / total_value
            target_values[asset_type] = total_value * target_pct
        
        # Generate rebalancing actions
        for asset_type, target_value in target_values.items():
            current_value = current_allocations.get(asset_type, Decimal('0')) * total_value
            difference = target_value - current_value
            
            if abs(difference) > total_value * Decimal('0.01'):  # 1% threshold
                if difference > 0:
                    actions.append(f"Buy ${difference:.2f} worth of {asset_type.value}")
                else:
                    actions.append(f"Sell ${abs(difference):.2f} worth of {asset_type.value}")
        
        self.last_rebalance_date = datetime.now()
        return actions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary for serialization"""
        return {
            'id': self.id,
            'player_id': self.player_id,
            'name': self.name,
            'status': self.status.value,
            'metrics': {
                'total_value': str(self.metrics.total_value),
                'total_return': str(self.metrics.total_return),
                'total_return_percentage': str(self.metrics.total_return_percentage),
                'game_stats': {
                    'attack_power': self.metrics.total_attack_power,
                    'defense_power': self.metrics.total_defense_power,
                    'magic_power': self.metrics.total_magic_power,
                    'durability': self.metrics.average_durability
                }
            },
            'assets': [asset.to_dict() for asset in self.assets.values()],
            'achievements': self.achievements,
            'level': self.level,
            'experience': self.experience,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat()
        }