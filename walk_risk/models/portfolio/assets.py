"""Asset models"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class AssetType(Enum):
    """자산 유형"""
    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    CASH = "cash"
    CRYPTO = "crypto"


@dataclass
class Asset:
    """자산 모델"""
    id: str
    name: str
    type: AssetType
    quantity: float
    average_price: float
    current_price: float

    @property
    def total_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def profit_loss(self) -> float:
        return (self.current_price - self.average_price) * self.quantity

    @property
    def profit_loss_percent(self) -> float:
        if self.average_price == 0:
            return 0
        return ((self.current_price - self.average_price) / self.average_price) * 100


@dataclass
class Position:
    """포지션 모델 - 포트폴리오 서비스에서 사용"""
    symbol: str
    quantity: int
    average_price: float

    @property
    def total_cost_basis(self) -> float:
        """총 취득가액"""
        return self.quantity * self.average_price