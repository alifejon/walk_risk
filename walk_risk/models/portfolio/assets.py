"""
Investment assets as game items
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import uuid


class AssetType(Enum):
    """Asset types mapped to game item categories"""
    CASH = "cash"           # HP/Stamina
    STOCK = "stock"         # Weapons/Tools
    BOND = "bond"           # Armor/Shields
    ETF = "etf"             # Weapon Sets
    CRYPTO = "crypto"       # Magic Items
    REAL_ESTATE = "real_estate"  # Buildings
    COMMODITY = "commodity"     # Raw Materials
    OPTION = "option"       # Consumables
    FUTURE = "future"       # Temporary Buffs


class AssetRarity(Enum):
    """Asset rarity levels"""
    COMMON = "common"       # 일반주 (흰색)
    UNCOMMON = "uncommon"   # 우량주 (초록색)
    RARE = "rare"           # 성장주 (파란색)
    EPIC = "epic"           # 대형주 (보라색)
    LEGENDARY = "legendary" # 배당킹 (주황색)
    MYTHIC = "mythic"       # 워렌버핏급 (빨간색)


class AssetStatus(Enum):
    """Asset status in portfolio"""
    OWNED = "owned"         # 보유 중
    WATCHING = "watching"   # 관심목록
    SOLD = "sold"           # 매도 완료
    EXPIRED = "expired"     # 만료 (옵션/선물)


@dataclass
class AssetStats:
    """Asset performance statistics"""
    # Basic stats
    current_price: Decimal = Decimal('0')
    purchase_price: Decimal = Decimal('0')
    market_value: Decimal = Decimal('0')
    
    # Performance metrics
    total_return: Decimal = Decimal('0')      # 총 수익률
    daily_return: Decimal = Decimal('0')      # 일일 수익률
    volatility: Decimal = Decimal('0')        # 변동성
    beta: Decimal = Decimal('1.0')            # 베타
    sharpe_ratio: Decimal = Decimal('0')      # 샤프 비율
    
    # Game stats
    attack_power: int = 0      # 수익 창출력
    defense_power: int = 0     # 안정성
    magic_power: int = 0       # 성장 잠재력
    durability: int = 100      # 지속가능성
    
    # Risk metrics
    var_95: Decimal = Decimal('0')            # Value at Risk
    max_drawdown: Decimal = Decimal('0')      # 최대 손실
    correlation_spy: Decimal = Decimal('0')   # S&P 500 상관관계
    
    def calculate_game_stats(self) -> None:
        """Calculate game stats from financial metrics"""
        # Attack Power = 수익률 기반
        self.attack_power = max(0, min(100, int(float(self.total_return) * 100)))
        
        # Defense Power = 안정성 기반 (낮은 변동성 = 높은 방어력)
        self.defense_power = max(0, min(100, int((1 - float(self.volatility)) * 100)))
        
        # Magic Power = 성장 잠재력 (베타 기반)
        self.magic_power = max(0, min(100, int(float(self.beta) * 50)))
        
        # Durability = 샤프비율 기반
        if self.sharpe_ratio > 0:
            self.durability = max(50, min(100, int(float(self.sharpe_ratio) * 20 + 80)))
        else:
            self.durability = max(10, min(50, int(abs(float(self.sharpe_ratio)) * 10 + 40)))


@dataclass
class AssetModifier:
    """Asset modifiers (like enchantments)"""
    name: str
    description: str
    modifier_type: str  # "dividend", "growth", "momentum", "value"
    effect_value: Decimal
    duration: Optional[timedelta] = None
    applied_date: datetime = field(default_factory=datetime.now)
    
    def is_active(self) -> bool:
        """Check if modifier is still active"""
        if self.duration is None:
            return True
        return datetime.now() - self.applied_date < self.duration


class Asset(ABC):
    """Base class for all investment assets (game items)"""
    
    def __init__(
        self,
        symbol: str,
        name: str,
        asset_type: AssetType,
        rarity: AssetRarity = AssetRarity.COMMON
    ):
        self.id = str(uuid.uuid4())
        self.symbol = symbol
        self.name = name
        self.asset_type = asset_type
        self.rarity = rarity
        self.status = AssetStatus.WATCHING
        
        # Ownership details
        self.quantity = Decimal('0')
        self.average_cost = Decimal('0')
        self.purchase_date: Optional[datetime] = None
        self.last_updated = datetime.now()
        
        # Stats and modifiers
        self.stats = AssetStats()
        self.modifiers: List[AssetModifier] = []
        
        # Game properties
        self.level = 1
        self.experience = 0
        self.max_level = 100
        
        # Metadata
        self.description = ""
        self.sector = ""
        self.industry = ""
        self.market_cap = Decimal('0')
        self.tags: List[str] = []
    
    @abstractmethod
    def calculate_stats(self, market_data: Dict[str, Any]) -> None:
        """Calculate asset statistics from market data"""
        pass
    
    @abstractmethod
    def get_item_description(self) -> str:
        """Get game-style item description"""
        pass
    
    def update_price(self, new_price: Decimal) -> None:
        """Update current price and recalculate stats"""
        old_price = self.stats.current_price
        self.stats.current_price = new_price
        
        if self.quantity > 0:
            self.stats.market_value = new_price * self.quantity
            
            if self.stats.purchase_price > 0:
                self.stats.total_return = (new_price - self.stats.purchase_price) / self.stats.purchase_price
            
            # Calculate daily return
            if old_price > 0:
                self.stats.daily_return = (new_price - old_price) / old_price
        
        self.last_updated = datetime.now()
        self.stats.calculate_game_stats()
    
    def add_modifier(self, modifier: AssetModifier) -> None:
        """Add modifier to asset"""
        self.modifiers.append(modifier)
    
    def remove_expired_modifiers(self) -> None:
        """Remove expired modifiers"""
        self.modifiers = [m for m in self.modifiers if m.is_active()]
    
    def get_effective_stats(self) -> AssetStats:
        """Get stats with modifiers applied"""
        effective_stats = AssetStats(**self.stats.__dict__)
        
        for modifier in self.modifiers:
            if modifier.is_active():
                if modifier.modifier_type == "dividend":
                    effective_stats.attack_power += int(float(modifier.effect_value))
                elif modifier.modifier_type == "growth":
                    effective_stats.magic_power += int(float(modifier.effect_value))
                elif modifier.modifier_type == "stability":
                    effective_stats.defense_power += int(float(modifier.effect_value))
        
        return effective_stats
    
    def level_up(self) -> bool:
        """Level up the asset if enough experience"""
        if self.level >= self.max_level:
            return False
        
        required_exp = self.level * 100  # Simple progression
        if self.experience >= required_exp:
            self.level += 1
            self.experience -= required_exp
            self._apply_level_bonus()
            return True
        return False
    
    def _apply_level_bonus(self) -> None:
        """Apply level-up bonuses"""
        # Increase all stats slightly
        self.stats.attack_power += 1
        self.stats.defense_power += 1
        self.stats.magic_power += 1
    
    def gain_experience(self, amount: int) -> None:
        """Gain experience points"""
        self.experience += amount
        while self.level_up():
            pass  # Keep leveling up if possible
    
    def get_rarity_color(self) -> str:
        """Get color code for rarity"""
        color_map = {
            AssetRarity.COMMON: "white",
            AssetRarity.UNCOMMON: "green",
            AssetRarity.RARE: "blue",
            AssetRarity.EPIC: "purple",
            AssetRarity.LEGENDARY: "orange",
            AssetRarity.MYTHIC: "red"
        }
        return color_map.get(self.rarity, "white")
    
    def get_type_emoji(self) -> str:
        """Get emoji for asset type"""
        emoji_map = {
            AssetType.CASH: "💰",
            AssetType.STOCK: "⚔️",
            AssetType.BOND: "🛡️",
            AssetType.ETF: "📦",
            AssetType.CRYPTO: "🔮",
            AssetType.REAL_ESTATE: "🏠",
            AssetType.COMMODITY: "⚡",
            AssetType.OPTION: "🧪",
            AssetType.FUTURE: "⏰"
        }
        return emoji_map.get(self.asset_type, "❓")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'asset_type': self.asset_type.value,
            'rarity': self.rarity.value,
            'status': self.status.value,
            'quantity': str(self.quantity),
            'average_cost': str(self.average_cost),
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'level': self.level,
            'experience': self.experience,
            'stats': {
                'current_price': str(self.stats.current_price),
                'market_value': str(self.stats.market_value),
                'total_return': str(self.stats.total_return),
                'attack_power': self.stats.attack_power,
                'defense_power': self.stats.defense_power,
                'magic_power': self.stats.magic_power,
                'durability': self.stats.durability
            },
            'sector': self.sector,
            'industry': self.industry,
            'tags': self.tags
        }


class Stock(Asset):
    """Stock asset - Primary weapon"""
    
    def __init__(self, symbol: str, name: str, **kwargs):
        super().__init__(symbol, name, AssetType.STOCK, **kwargs)
        self.dividend_yield = Decimal('0')
        self.pe_ratio = Decimal('0')
        self.pb_ratio = Decimal('0')
        self.roe = Decimal('0')
        self.debt_to_equity = Decimal('0')
    
    def calculate_stats(self, market_data: Dict[str, Any]) -> None:
        """Calculate stock-specific statistics"""
        # Update basic price info
        if 'price' in market_data:
            self.update_price(Decimal(str(market_data['price'])))
        
        # Update financial metrics
        if 'dividend_yield' in market_data:
            self.dividend_yield = Decimal(str(market_data['dividend_yield']))
        if 'pe_ratio' in market_data:
            self.pe_ratio = Decimal(str(market_data['pe_ratio']))
        if 'pb_ratio' in market_data:
            self.pb_ratio = Decimal(str(market_data['pb_ratio']))
        
        # Calculate rarity based on fundamentals
        self._update_rarity()
    
    def _update_rarity(self) -> None:
        """Update rarity based on stock fundamentals"""
        score = 0
        
        # Dividend yield contribution
        if self.dividend_yield > Decimal('0.05'):  # >5%
            score += 2
        elif self.dividend_yield > Decimal('0.03'):  # >3%
            score += 1
        
        # P/E ratio contribution (lower is better for value)
        if 0 < self.pe_ratio < Decimal('15'):
            score += 2
        elif 0 < self.pe_ratio < Decimal('25'):
            score += 1
        
        # ROE contribution
        if self.roe > Decimal('0.20'):  # >20%
            score += 2
        elif self.roe > Decimal('0.15'):  # >15%
            score += 1
        
        # Market cap consideration
        if self.market_cap > Decimal('100000000000'):  # >100B (large cap)
            score += 1
        
        # Set rarity based on score
        if score >= 6:
            self.rarity = AssetRarity.LEGENDARY
        elif score >= 5:
            self.rarity = AssetRarity.EPIC
        elif score >= 3:
            self.rarity = AssetRarity.RARE
        elif score >= 2:
            self.rarity = AssetRarity.UNCOMMON
        else:
            self.rarity = AssetRarity.COMMON
    
    def get_item_description(self) -> str:
        """Get RPG-style item description"""
        desc = f"🗡️ {self.name} ({self.symbol})\n"
        desc += f"레벨: {self.level} | 희귀도: {self.rarity.value}\n"
        desc += f"공격력: {self.stats.attack_power} | 방어력: {self.stats.defense_power}\n"
        desc += f"마법력: {self.stats.magic_power} | 내구도: {self.stats.durability}/100\n"
        desc += f"현재가: ${self.stats.current_price:.2f}\n"
        
        if self.dividend_yield > 0:
            desc += f"📈 배당수익률: {self.dividend_yield:.2%} (패시브 수입)\n"
        
        if self.pe_ratio > 0:
            desc += f"💰 PER: {self.pe_ratio:.1f} (가치 지표)\n"
        
        # Add modifiers
        active_modifiers = [m for m in self.modifiers if m.is_active()]
        if active_modifiers:
            desc += "\n🔮 활성 효과:\n"
            for modifier in active_modifiers:
                desc += f"  • {modifier.name}: {modifier.description}\n"
        
        return desc


class Bond(Asset):
    """Bond asset - Defensive armor"""
    
    def __init__(self, symbol: str, name: str, **kwargs):
        super().__init__(symbol, name, AssetType.BOND, **kwargs)
        self.maturity_date: Optional[datetime] = None
        self.coupon_rate = Decimal('0')
        self.yield_to_maturity = Decimal('0')
        self.duration = Decimal('0')
        self.credit_rating = ""
    
    def calculate_stats(self, market_data: Dict[str, Any]) -> None:
        """Calculate bond-specific statistics"""
        if 'price' in market_data:
            self.update_price(Decimal(str(market_data['price'])))
        
        if 'yield' in market_data:
            self.yield_to_maturity = Decimal(str(market_data['yield']))
        
        # Bonds have high defense, low attack
        self.stats.defense_power = min(95, int(float(self.yield_to_maturity) * 1000))
        self.stats.attack_power = min(30, int(float(self.yield_to_maturity) * 500))
        self.stats.magic_power = 10  # Low growth potential
        
        # Update rarity based on credit rating and yield
        self._update_rarity()
    
    def _update_rarity(self) -> None:
        """Update rarity based on bond characteristics"""
        score = 0
        
        # Credit rating contribution
        if self.credit_rating in ['AAA', 'AA+', 'AA', 'AA-']:
            score += 3
        elif self.credit_rating in ['A+', 'A', 'A-']:
            score += 2
        elif self.credit_rating in ['BBB+', 'BBB', 'BBB-']:
            score += 1
        
        # Yield contribution
        if self.yield_to_maturity > Decimal('0.06'):  # >6%
            score += 2
        elif self.yield_to_maturity > Decimal('0.04'):  # >4%
            score += 1
        
        # Set rarity
        if score >= 5:
            self.rarity = AssetRarity.LEGENDARY
        elif score >= 4:
            self.rarity = AssetRarity.EPIC
        elif score >= 3:
            self.rarity = AssetRarity.RARE
        elif score >= 2:
            self.rarity = AssetRarity.UNCOMMON
        else:
            self.rarity = AssetRarity.COMMON
    
    def get_item_description(self) -> str:
        """Get RPG-style item description"""
        desc = f"🛡️ {self.name} ({self.symbol})\n"
        desc += f"레벨: {self.level} | 희귀도: {self.rarity.value}\n"
        desc += f"방어력: {self.stats.defense_power} | 공격력: {self.stats.attack_power}\n"
        desc += f"안정성: {self.stats.durability}/100\n"
        desc += f"현재가: ${self.stats.current_price:.2f}\n"
        desc += f"📊 수익률: {self.yield_to_maturity:.2%}\n"
        
        if self.credit_rating:
            desc += f"💎 신용등급: {self.credit_rating}\n"
        
        if self.maturity_date:
            days_to_maturity = (self.maturity_date - datetime.now()).days
            desc += f"⏰ 만기: {days_to_maturity}일 후\n"
        
        return desc


class Cash(Asset):
    """Cash asset - Health/Stamina"""
    
    def __init__(self, currency: str = "USD", **kwargs):
        super().__init__(currency, f"{currency} Cash", AssetType.CASH, **kwargs)
        self.currency = currency
        self.interest_rate = Decimal('0')
        
        # Cash has no attack but provides stability
        self.stats.attack_power = 0
        self.stats.defense_power = 100
        self.stats.magic_power = 0
        self.stats.durability = 100
    
    def calculate_stats(self, market_data: Dict[str, Any] = None) -> None:
        """Cash stats are mostly static"""
        if market_data and 'interest_rate' in market_data:
            self.interest_rate = Decimal(str(market_data['interest_rate']))
            # Interest rate affects "regeneration" rate
            self.stats.magic_power = min(10, int(float(self.interest_rate) * 200))
    
    def get_item_description(self) -> str:
        """Get RPG-style item description"""
        desc = f"💰 {self.name}\n"
        desc += f"잔액: ${self.quantity:.2f}\n"
        desc += f"방어력: {self.stats.defense_power} (완전 안전)\n"
        desc += f"유동성: 100% (즉시 사용 가능)\n"
        
        if self.interest_rate > 0:
            desc += f"📈 이자율: {self.interest_rate:.2%} (패시브 증가)\n"
        
        desc += "\n💡 현금은 기회비용이 있지만 안전한 피난처입니다."
        return desc


class ETF(Asset):
    """ETF asset - Equipment sets"""
    
    def __init__(self, symbol: str, name: str, **kwargs):
        super().__init__(symbol, name, AssetType.ETF, **kwargs)
        self.expense_ratio = Decimal('0')
        self.tracking_error = Decimal('0')
        self.underlying_assets: List[str] = []
        self.rebalance_frequency = ""
    
    def calculate_stats(self, market_data: Dict[str, Any]) -> None:
        """Calculate ETF-specific statistics"""
        if 'price' in market_data:
            self.update_price(Decimal(str(market_data['price'])))
        
        # ETFs provide balanced stats with set bonuses
        self.stats.attack_power = 50  # Moderate attack
        self.stats.defense_power = 60  # Good defense through diversification
        self.stats.magic_power = 40   # Moderate growth
        
        # Lower expense ratio = higher durability
        if self.expense_ratio > 0:
            self.stats.durability = max(50, 100 - int(float(self.expense_ratio) * 1000))
    
    def get_item_description(self) -> str:
        """Get RPG-style item description"""
        desc = f"📦 {self.name} ({self.symbol})\n"
        desc += f"레벨: {self.level} | 희귀도: {self.rarity.value}\n"
        desc += f"균형 스탯 - 공격: {self.stats.attack_power} | 방어: {self.stats.defense_power}\n"
        desc += f"현재가: ${self.stats.current_price:.2f}\n"
        desc += f"💰 운용비용: {self.expense_ratio:.2%}\n"
        desc += f"🎯 추적오차: {self.tracking_error:.2%}\n"
        desc += f"\n🔗 세트 효과: 분산투자 보너스\n"
        desc += "  • 포트폴리오 전체 리스크 감소\n"
        desc += "  • 안정적인 수익 제공\n"
        return desc