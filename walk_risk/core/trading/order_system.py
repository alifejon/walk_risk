"""Order System - 모의 거래 주문 시스템"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...models.portfolio.real_portfolio import RealPortfolio, Transaction
from ...data.market_data.yahoo_finance import yahoo_finance, StockData
from ...utils.logger import setup_logger

logger = setup_logger(__name__)


class OrderType(Enum):
    """주문 유형"""
    MARKET = "market"  # 시장가 주문
    LIMIT = "limit"    # 지정가 주문
    STOP_LOSS = "stop_loss"  # 손절매 주문
    TAKE_PROFIT = "take_profit"  # 익절매 주문


class OrderStatus(Enum):
    """주문 상태"""
    PENDING = "pending"  # 대기 중
    FILLED = "filled"   # 체결
    CANCELLED = "cancelled"  # 취소
    REJECTED = "rejected"   # 거부
    PARTIAL = "partial"    # 일부 체결


class OrderSide(Enum):
    """주문 방향"""
    BUY = "buy"   # 매수
    SELL = "sell" # 매도


@dataclass
class OrderRequest:
    """주문 요청"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str = ""
    symbol: str = ""
    side: OrderSide = OrderSide.BUY
    order_type: OrderType = OrderType.MARKET
    quantity: float = 0.0
    price: Optional[float] = None  # 지정가 주문일 때
    stop_price: Optional[float] = None  # 스톱 주문일 때
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # 주문 만료 시간
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    commission: float = 0.0
    
    @property
    def remaining_quantity(self) -> float:
        return self.quantity - self.filled_quantity
        
    @property
    def is_active(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "stop_price": self.stop_price,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "filled_quantity": self.filled_quantity,
            "average_fill_price": self.average_fill_price,
            "commission": self.commission
        }


@dataclass
class Order:
    """간단한 주문 객체 - API 서비스에서 사용"""
    order_id: str
    symbol: str
    order_type: OrderType
    side: OrderSide
    quantity: int
    price: Optional[float] = None
    player_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class OrderSystem:
    """간단한 주문 시스템 - API 서비스용"""

    def __init__(self):
        self.orders: Dict[str, Order] = {}

    async def initialize(self):
        """시스템 초기화"""
        pass

    async def execute_order(self, order: Order) -> Dict[str, Any]:
        """주문 실행 (모의)"""
        # 현재 시세 조회 (모의)
        current_price = await self._get_mock_price(order.symbol)
        execution_price = order.price if order.order_type == OrderType.LIMIT else current_price

        self.orders[order.order_id] = order

        return {
            "status": "filled",
            "execution_price": execution_price,
            "execution_time": datetime.now().isoformat()
        }

    async def _get_mock_price(self, symbol: str) -> float:
        """모의 시세 조회"""
        mock_prices = {
            "005930.KS": 75000,
            "000660.KS": 95000,
            "035420.KS": 180000,
        }
        return mock_prices.get(symbol, 10000)


class OrderExecutionEngine:
    """
    주문 실행 엔진
    
    다양한 주문 유형을 처리하고, 실시간 시장 데이터를 기반으로
    모의 거래를 실행합니다.
    """
    
    def __init__(self):
        self.active_orders: Dict[str, OrderRequest] = {}
        self.order_history: List[OrderRequest] = []
        self.execution_callbacks: List[Callable] = []
        self.is_market_open = True  # 모의 시장은 언제나 열려 있음
        
    def add_execution_callback(self, callback: Callable[[OrderRequest, Transaction], None]):
        """주문 체결 콜백 등록"""
        self.execution_callbacks.append(callback)
        
    async def submit_order(
        self, 
        portfolio: RealPortfolio, 
        order_request: OrderRequest
    ) -> Tuple[bool, str]:
        """주문 제출"""
        try:
            # 주문 유효성 검증
            validation_result = await self._validate_order(portfolio, order_request)
            if not validation_result[0]:
                order_request.status = OrderStatus.REJECTED
                return False, validation_result[1]
                
            # 활성 주문에 추가
            self.active_orders[order_request.id] = order_request
            
            # 시장가 주문이면 즉시 실행
            if order_request.order_type == OrderType.MARKET:
                await self._execute_market_order(portfolio, order_request)
            else:
                logger.info(f"주문 대기열에 추가: {order_request.symbol} {order_request.side.value} {order_request.quantity}")
                
            return True, f"주문이 성공적으로 제출되었습니다. 주문 ID: {order_request.id}"
            
        except Exception as e:
            logger.error(f"주문 제출 실패: {e}")
            order_request.status = OrderStatus.REJECTED
            return False, f"주문 제출 실패: {str(e)}"
            
    async def _validate_order(
        self, 
        portfolio: RealPortfolio, 
        order_request: OrderRequest
    ) -> Tuple[bool, str]:
        """주문 유효성 검증"""
        # 기본 유효성 검증
        if order_request.quantity <= 0:
            return False, "주문 수량이 0보다 작거나 같습니다"
            
        if not order_request.symbol:
            return False, "주식 심볼이 누락되었습니다"
            
        # 시장 상태 체크
        if not self.is_market_open:
            return False, "시장이 닫혀 있습니다"
            
        # 매수 주문 유효성 검증
        if order_request.side == OrderSide.BUY:
            return await self._validate_buy_order(portfolio, order_request)
        else:
            return await self._validate_sell_order(portfolio, order_request)
            
    async def _validate_buy_order(
        self, 
        portfolio: RealPortfolio, 
        order_request: OrderRequest
    ) -> Tuple[bool, str]:
        """매수 주문 유효성 검증"""
        # 가격 정보 확인
        price = order_request.price
        if order_request.order_type == OrderType.MARKET or price is None:
            stock_data = await yahoo_finance.get_stock_data(order_request.symbol)
            if not stock_data:
                return False, f"주식 정보를 찾을 수 없습니다: {order_request.symbol}"
            price = stock_data.current_price
            
        # 필요 자금 계산
        total_amount = order_request.quantity * price
        commission = portfolio.calculate_commission(total_amount)
        required_cash = total_amount + commission
        
        if required_cash > portfolio.cash:
            return False, f"현금이 부족합니다. 필요: {required_cash:,.0f}원, 보유: {portfolio.cash:,.0f}원"
            
        return True, "유효한 매수 주문입니다"
        
    async def _validate_sell_order(
        self, 
        portfolio: RealPortfolio, 
        order_request: OrderRequest
    ) -> Tuple[bool, str]:
        """매도 주문 유효성 검증"""
        # 보유 수량 확인
        if order_request.symbol not in portfolio.positions:
            return False, f"보유하지 않은 주식입니다: {order_request.symbol}"
            
        position = portfolio.positions[order_request.symbol]
        if order_request.quantity > position.quantity:
            return False, f"보유 수량 부족. 보유: {position.quantity}주, 매도 요청: {order_request.quantity}주"
            
        return True, "유효한 매도 주문입니다"
        
    async def _execute_market_order(
        self, 
        portfolio: RealPortfolio, 
        order_request: OrderRequest
    ):
        """시장가 주문 실행"""
        try:
            if order_request.side == OrderSide.BUY:
                success, message, transaction = await portfolio.buy_stock(
                    order_request.symbol, 
                    order_request.quantity
                )
            else:
                success, message, transaction = await portfolio.sell_stock(
                    order_request.symbol, 
                    order_request.quantity
                )
                
            if success and transaction:
                # 주문 체결 처리
                order_request.status = OrderStatus.FILLED
                order_request.filled_quantity = order_request.quantity
                order_request.average_fill_price = transaction.price
                order_request.commission = transaction.commission
                
                # 활성 주문에서 제거 및 이력에 추가
                if order_request.id in self.active_orders:
                    del self.active_orders[order_request.id]
                self.order_history.append(order_request)
                
                # 콜백 실행
                for callback in self.execution_callbacks:
                    try:
                        callback(order_request, transaction)
                    except Exception as e:
                        logger.error(f"콜백 실행 오류: {e}")
                        
                logger.info(f"주문 체결: {order_request.id} - {message}")
            else:
                # 주문 실패
                order_request.status = OrderStatus.REJECTED
                if order_request.id in self.active_orders:
                    del self.active_orders[order_request.id]
                self.order_history.append(order_request)
                logger.warning(f"주문 실패: {order_request.id} - {message}")
                
        except Exception as e:
            logger.error(f"주문 실행 오류: {e}")
            order_request.status = OrderStatus.REJECTED
            
    async def process_pending_orders(self, portfolio: RealPortfolio):
        """대기 중인 주문 처리 (지정가, 스톱 주문 등)"""
        if not self.active_orders:
            return
            
        # 현재 가격 정보 수집
        symbols = {order.symbol for order in self.active_orders.values()}
        stock_data_dict = await yahoo_finance.get_multiple_stocks(list(symbols))
        
        orders_to_execute = []
        
        for order_id, order in self.active_orders.items():
            if order.symbol not in stock_data_dict:
                continue
                
            current_price = stock_data_dict[order.symbol].current_price
            
            # 주문 만료 체크
            if order.expires_at and datetime.now() > order.expires_at:
                order.status = OrderStatus.CANCELLED
                orders_to_execute.append(order_id)
                continue
                
            # 주문 유형별 체결 조건 체크
            should_execute = False
            
            if order.order_type == OrderType.LIMIT:
                if order.side == OrderSide.BUY and current_price <= order.price:
                    should_execute = True
                elif order.side == OrderSide.SELL and current_price >= order.price:
                    should_execute = True
                    
            elif order.order_type == OrderType.STOP_LOSS:
                if order.side == OrderSide.SELL and current_price <= order.stop_price:
                    should_execute = True
                    
            elif order.order_type == OrderType.TAKE_PROFIT:
                if order.side == OrderSide.SELL and current_price >= order.price:
                    should_execute = True
                    
            if should_execute:
                orders_to_execute.append(order_id)
                
        # 체결 주문 실행
        for order_id in orders_to_execute:
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                if order.status != OrderStatus.CANCELLED:
                    await self._execute_market_order(portfolio, order)
                else:
                    # 취소된 주문 정리
                    del self.active_orders[order_id]
                    self.order_history.append(order)
                    
    def cancel_order(self, order_id: str) -> Tuple[bool, str]:
        """주문 취소"""
        if order_id not in self.active_orders:
            return False, "해당 주문을 찾을 수 없습니다"
            
        order = self.active_orders[order_id]
        order.status = OrderStatus.CANCELLED
        
        del self.active_orders[order_id]
        self.order_history.append(order)
        
        logger.info(f"주문 취소: {order_id}")
        return True, f"주문이 취소되었습니다: {order_id}"
        
    def get_active_orders(self, portfolio_id: Optional[str] = None) -> List[OrderRequest]:
        """활성 주문 조회"""
        orders = list(self.active_orders.values())
        if portfolio_id:
            orders = [order for order in orders if order.portfolio_id == portfolio_id]
        return orders
        
    def get_order_history(
        self, 
        portfolio_id: Optional[str] = None,
        limit: int = 100
    ) -> List[OrderRequest]:
        """주문 이력 조회"""
        orders = self.order_history[-limit:] if limit > 0 else self.order_history
        if portfolio_id:
            orders = [order for order in orders if order.portfolio_id == portfolio_id]
        return orders[::-1]  # 최신 순으로 정렬
        
    def get_order_statistics(self, portfolio_id: str) -> Dict[str, Any]:
        """주문 통계"""
        all_orders = [
            order for order in self.order_history 
            if order.portfolio_id == portfolio_id
        ]
        
        if not all_orders:
            return {
                "total_orders": 0,
                "filled_orders": 0,
                "cancelled_orders": 0,
                "success_rate": 0.0,
                "total_commission": 0.0
            }
            
        filled_orders = [o for o in all_orders if o.status == OrderStatus.FILLED]
        cancelled_orders = [o for o in all_orders if o.status == OrderStatus.CANCELLED]
        
        return {
            "total_orders": len(all_orders),
            "filled_orders": len(filled_orders),
            "cancelled_orders": len(cancelled_orders),
            "success_rate": len(filled_orders) / len(all_orders) * 100,
            "total_commission": sum(o.commission for o in filled_orders)
        }


# 전역 인스턴스
order_engine = OrderExecutionEngine()