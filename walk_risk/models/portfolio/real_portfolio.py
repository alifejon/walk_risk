"""Real Portfolio - 실시간 모의투자 포트폴리오"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import json

from ..player.base import Player
from .assets import Asset, AssetType
from ...data.market_data.yahoo_finance import yahoo_finance, StockData
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Transaction:
    """거래 기록"""
    id: str
    portfolio_id: str
    asset_symbol: str
    asset_name: str
    transaction_type: str  # "buy", "sell"
    quantity: float
    price: float
    total_amount: float
    commission: float  # 수수료
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def net_amount(self) -> float:
        """수수료 포함 순 금액"""
        if self.transaction_type == "buy":
            return self.total_amount + self.commission
        else:  # sell
            return self.total_amount - self.commission
            
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "asset_symbol": self.asset_symbol,
            "asset_name": self.asset_name,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "price": self.price,
            "total_amount": self.total_amount,
            "commission": self.commission,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PortfolioPosition:
    """포트폴리오 보유 포지션"""
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def market_value(self) -> float:
        """현재 시가총액"""
        return self.quantity * self.current_price
        
    @property
    def book_value(self) -> float:
        """매수 금액"""
        return self.quantity * self.average_price
        
    @property
    def unrealized_pnl(self) -> float:
        """평가손익"""
        return self.market_value - self.book_value
        
    @property
    def unrealized_pnl_percent(self) -> float:
        """평가수익률"""
        if self.book_value == 0:
            return 0.0
        return (self.unrealized_pnl / self.book_value) * 100
        
    @property
    def is_profit(self) -> bool:
        return self.unrealized_pnl > 0
        
    def update_price(self, new_price: float):
        """주가 업데이트"""
        self.current_price = new_price
        self.last_updated = datetime.now()
        
    def add_quantity(self, quantity: float, price: float):
        """수량 추가 (평균 단가 재계산)"""
        total_cost = (self.quantity * self.average_price) + (quantity * price)
        self.quantity += quantity
        self.average_price = total_cost / self.quantity if self.quantity > 0 else 0
        
    def reduce_quantity(self, quantity: float) -> bool:
        """수량 감소 (매도)"""
        if quantity > self.quantity:
            return False
        self.quantity -= quantity
        return True


class RealPortfolio:
    """
    실시간 모의투자 포트폴리오
    
    실제 시장 데이터를 사용하여 모의투자를 진행합니다.
    거래 수수료, 세금 등을 고려한 현실적인 환경을 제공합니다.
    """
    
    def __init__(
        self, 
        portfolio_id: str,
        owner_id: str,
        initial_cash: float = 10_000_000,  # 1천만원 기본
        commission_rate: float = 0.0015  # 0.15% 수수료
    ):
        self.portfolio_id = portfolio_id
        self.owner_id = owner_id
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.commission_rate = commission_rate
        
        # 보유 포지션
        self.positions: Dict[str, PortfolioPosition] = {}
        
        # 거래 기록
        self.transactions: List[Transaction] = []
        
        # 성과 추적
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.daily_values: List[Tuple[datetime, float]] = []  # 일별 포트폴리오 가치
        
    @property
    def total_market_value(self) -> float:
        """전체 주식 시가총액"""
        return sum(pos.market_value for pos in self.positions.values())
        
    @property
    def total_book_value(self) -> float:
        """전체 매수 금액"""
        return sum(pos.book_value for pos in self.positions.values())
        
    @property
    def total_portfolio_value(self) -> float:
        """포트폴리오 총 가치 (현금 + 주식)"""
        return self.cash + self.total_market_value
        
    @property
    def total_invested(self) -> float:
        """전체 투자 금액"""
        return self.initial_cash - self.cash + sum(
            t.net_amount for t in self.transactions if t.transaction_type == "buy"
        )
        
    @property
    def total_return(self) -> float:
        """전체 수익"""
        return self.total_portfolio_value - self.initial_cash
        
    @property
    def total_return_percent(self) -> float:
        """전체 수익률"""
        if self.initial_cash == 0:
            return 0.0
        return (self.total_return / self.initial_cash) * 100
        
    @property
    def unrealized_pnl(self) -> float:
        """평가손익"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
        
    @property
    def asset_allocation(self) -> Dict[str, float]:
        """자산 비중"""
        total_value = self.total_portfolio_value
        if total_value == 0:
            return {"cash": 100.0}
            
        allocation = {"cash": (self.cash / total_value) * 100}
        
        for symbol, position in self.positions.items():
            allocation[symbol] = (position.market_value / total_value) * 100
            
        return allocation
        
    def calculate_commission(self, amount: float) -> float:
        """수수료 계산"""
        commission = amount * self.commission_rate
        return float(Decimal(str(commission)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        
    async def buy_stock(
        self, 
        symbol: str, 
        quantity: float, 
        price: Optional[float] = None
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """주식 매수"""
        try:
            # 현재 가격 조회 (가격 지정 안된 경우)
            if price is None:
                stock_data = await yahoo_finance.get_stock_data(symbol)
                if not stock_data:
                    return False, f"주식 정보를 찾을 수 없습니다: {symbol}", None
                price = stock_data.current_price
                
            # 금액 계산
            total_amount = quantity * price
            commission = self.calculate_commission(total_amount)
            net_amount = total_amount + commission
            
            # 현금 부족 체크
            if net_amount > self.cash:
                return False, f"현금이 부족합니다. 필요: {net_amount:,.0f}원, 보유: {self.cash:,.0f}원", None
                
            # 거래 실행
            transaction_id = f"BUY_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            stock_name = yahoo_finance.get_stock_name(symbol)
            
            transaction = Transaction(
                id=transaction_id,
                portfolio_id=self.portfolio_id,
                asset_symbol=symbol,
                asset_name=stock_name,
                transaction_type="buy",
                quantity=quantity,
                price=price,
                total_amount=total_amount,
                commission=commission
            )
            
            # 포지션 업데이트
            if symbol in self.positions:
                self.positions[symbol].add_quantity(quantity, price)
            else:
                self.positions[symbol] = PortfolioPosition(
                    symbol=symbol,
                    name=stock_name,
                    quantity=quantity,
                    average_price=price,
                    current_price=price
                )
                
            # 현금 차감
            self.cash -= net_amount
            
            # 거래 기록 추가
            self.transactions.append(transaction)
            self.last_updated = datetime.now()
            
            logger.info(f"매수 완료: {stock_name} {quantity}주 @ {price:,.0f}원")
            return True, f"{stock_name} {quantity}주를 {price:,.0f}원에 매수했습니다.", transaction
            
        except Exception as e:
            logger.error(f"매수 실패: {e}")
            return False, f"매수 실패: {str(e)}", None
            
    async def sell_stock(
        self, 
        symbol: str, 
        quantity: float, 
        price: Optional[float] = None
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """주식 매도"""
        try:
            # 보유 체크
            if symbol not in self.positions:
                return False, f"보유하지 않은 주식입니다: {symbol}", None
                
            position = self.positions[symbol]
            if quantity > position.quantity:
                return False, f"보유 수량 부족. 보유: {position.quantity}주, 매도 요청: {quantity}주", None
                
            # 현재 가격 조회
            if price is None:
                stock_data = await yahoo_finance.get_stock_data(symbol)
                if not stock_data:
                    return False, f"주식 정보를 찾을 수 없습니다: {symbol}", None
                price = stock_data.current_price
                
            # 금액 계산
            total_amount = quantity * price
            commission = self.calculate_commission(total_amount)
            net_amount = total_amount - commission
            
            # 거래 실행
            transaction_id = f"SELL_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            transaction = Transaction(
                id=transaction_id,
                portfolio_id=self.portfolio_id,
                asset_symbol=symbol,
                asset_name=position.name,
                transaction_type="sell",
                quantity=quantity,
                price=price,
                total_amount=total_amount,
                commission=commission
            )
            
            # 포지션 업데이트
            position.reduce_quantity(quantity)
            
            # 전량 매도 시 포지션 제거
            if position.quantity == 0:
                del self.positions[symbol]
                
            # 현금 증가
            self.cash += net_amount
            
            # 거래 기록 추가
            self.transactions.append(transaction)
            self.last_updated = datetime.now()
            
            logger.info(f"매도 완료: {position.name} {quantity}주 @ {price:,.0f}원")
            return True, f"{position.name} {quantity}주를 {price:,.0f}원에 매도했습니다.", transaction
            
        except Exception as e:
            logger.error(f"매도 실패: {e}")
            return False, f"매도 실패: {str(e)}", None
            
    async def update_all_prices(self) -> int:
        """모든 보유 주식 가격 업데이트"""
        if not self.positions:
            return 0
            
        symbols = list(self.positions.keys())
        updated_count = 0
        
        try:
            stock_data_dict = await yahoo_finance.get_multiple_stocks(symbols)
            
            for symbol, stock_data in stock_data_dict.items():
                if symbol in self.positions and stock_data:
                    self.positions[symbol].update_price(stock_data.current_price)
                    updated_count += 1
                    
            self.last_updated = datetime.now()
            
            # 일별 가치 기록 (하루 한 번만)
            today = datetime.now().date()
            if not self.daily_values or self.daily_values[-1][0].date() != today:
                self.daily_values.append((datetime.now(), self.total_portfolio_value))
                
            logger.info(f"가격 업데이트 완료: {updated_count}/{len(symbols)} 종목")
            return updated_count
            
        except Exception as e:
            logger.error(f"가격 업데이트 실패: {e}")
            return 0
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """성과 요약"""
        return {
            "portfolio_id": self.portfolio_id,
            "total_value": self.total_portfolio_value,
            "cash": self.cash,
            "invested_value": self.total_market_value,
            "total_return": self.total_return,
            "total_return_percent": self.total_return_percent,
            "unrealized_pnl": self.unrealized_pnl,
            "position_count": len(self.positions),
            "transaction_count": len(self.transactions),
            "asset_allocation": self.asset_allocation,
            "last_updated": self.last_updated.isoformat()
        }
        
    def get_positions_summary(self) -> List[Dict[str, Any]]:
        """보유 포지션 요약"""
        positions = []
        for symbol, position in self.positions.items():
            positions.append({
                "symbol": symbol,
                "name": position.name,
                "quantity": position.quantity,
                "average_price": position.average_price,
                "current_price": position.current_price,
                "market_value": position.market_value,
                "unrealized_pnl": position.unrealized_pnl,
                "unrealized_pnl_percent": position.unrealized_pnl_percent,
                "is_profit": position.is_profit
            })
        return positions
        
    def save_to_dict(self) -> Dict[str, Any]:
        """포트폴리오 데이터 딕셔너리로 저장"""
        return {
            "portfolio_id": self.portfolio_id,
            "owner_id": self.owner_id,
            "cash": self.cash,
            "initial_cash": self.initial_cash,
            "commission_rate": self.commission_rate,
            "positions": {
                symbol: {
                    "symbol": pos.symbol,
                    "name": pos.name,
                    "quantity": pos.quantity,
                    "average_price": pos.average_price,
                    "current_price": pos.current_price,
                    "last_updated": pos.last_updated.isoformat()
                } for symbol, pos in self.positions.items()
            },
            "transactions": [t.to_dict() for t in self.transactions],
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "daily_values": [(dt.isoformat(), value) for dt, value in self.daily_values]
        }
        
    @classmethod
    def load_from_dict(cls, data: Dict[str, Any]) -> 'RealPortfolio':
        """딕셔너리에서 포트폴리오 로드"""
        portfolio = cls(
            portfolio_id=data["portfolio_id"],
            owner_id=data["owner_id"],
            initial_cash=data["initial_cash"],
            commission_rate=data["commission_rate"]
        )
        
        portfolio.cash = data["cash"]
        portfolio.created_at = datetime.fromisoformat(data["created_at"])
        portfolio.last_updated = datetime.fromisoformat(data["last_updated"])
        
        # 포지션 로드
        for symbol, pos_data in data["positions"].items():
            portfolio.positions[symbol] = PortfolioPosition(
                symbol=pos_data["symbol"],
                name=pos_data["name"],
                quantity=pos_data["quantity"],
                average_price=pos_data["average_price"],
                current_price=pos_data["current_price"],
                last_updated=datetime.fromisoformat(pos_data["last_updated"])
            )
            
        # 거래 기록 로드
        for t_data in data["transactions"]:
            portfolio.transactions.append(Transaction(
                id=t_data["id"],
                portfolio_id=t_data["portfolio_id"],
                asset_symbol=t_data["asset_symbol"],
                asset_name=t_data["asset_name"],
                transaction_type=t_data["transaction_type"],
                quantity=t_data["quantity"],
                price=t_data["price"],
                total_amount=t_data["total_amount"],
                commission=t_data["commission"],
                timestamp=datetime.fromisoformat(t_data["timestamp"])
            ))
            
        # 일별 가치 로드
        portfolio.daily_values = [
            (datetime.fromisoformat(dt_str), value) 
            for dt_str, value in data["daily_values"]
        ]
        
        return portfolio