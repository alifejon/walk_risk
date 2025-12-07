"""Portfolio Service - 포트폴리오 관리 서비스"""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid

from .base import BaseService
from ..models.portfolio.real_portfolio import RealPortfolio
from ..models.portfolio.assets import Asset, Position
from ..core.trading.order_system import OrderSystem, Order, OrderType, OrderSide

if TYPE_CHECKING:
    from .market_service import MarketService


class PortfolioService(BaseService):
    """포트폴리오 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self, market_service: Optional["MarketService"] = None):
        super().__init__()
        self.order_system = OrderSystem()
        self.market_service = market_service

        # 플레이어별 포트폴리오
        self.portfolios: Dict[str, RealPortfolio] = {}

        # 거래 내역
        self.trade_history: Dict[str, List[Dict[str, Any]]] = {}

        # 폴백용 가격 캐시 (MarketService 없을 때 사용)
        self._fallback_prices: Dict[str, float] = {
            "005930.KS": 75000,
            "000660.KS": 95000,
            "035420.KS": 180000,
            "051910.KS": 420000,
            "207940.KS": 820000,
            "006400.KS": 650000,
            "028260.KS": 120000,
            "068270.KS": 180000,
            "005380.KS": 245000,
            "035720.KS": 55000,
        }

    def set_market_service(self, market_service: "MarketService"):
        """MarketService 설정 (의존성 주입)"""
        self.market_service = market_service

    async def _setup(self):
        """서비스 초기화"""
        await self.order_system.initialize()
        self.logger.info("PortfolioService setup completed")

    async def create_portfolio(
        self,
        player_id: str,
        initial_cash: float = 10000000.0  # 초기 현금 1천만원
    ) -> Dict[str, Any]:
        """새로운 포트폴리오 생성"""
        try:
            self._validate_initialized()

            if player_id in self.portfolios:
                return self._create_response(
                    success=False,
                    message="Portfolio already exists",
                    error_code="PORTFOLIO_EXISTS"
                )

            # 포트폴리오 생성
            portfolio = RealPortfolio(
                portfolio_id=str(uuid.uuid4()),
                player_id=player_id,
                initial_cash=initial_cash,
                current_cash=initial_cash
            )

            self.portfolios[player_id] = portfolio
            self.trade_history[player_id] = []

            self.logger.info(f"Portfolio created for player {player_id}")

            return self._create_response(
                success=True,
                data={
                    "portfolio_id": portfolio.portfolio_id,
                    "initial_cash": initial_cash,
                    "current_cash": initial_cash,
                    "total_value": initial_cash
                },
                message="Portfolio created successfully"
            )

        except Exception as e:
            return self._handle_error(e, "create_portfolio")

    async def get_portfolio(self, player_id: str) -> Dict[str, Any]:
        """포트폴리오 조회"""
        try:
            self._validate_initialized()

            if player_id not in self.portfolios:
                return self._create_response(
                    success=False,
                    message="Portfolio not found",
                    error_code="PORTFOLIO_NOT_FOUND"
                )

            portfolio = self.portfolios[player_id]

            # 포트폴리오 값 업데이트 (실시간 시세 반영)
            await self._update_portfolio_values(portfolio)

            # 보유 종목 정보 구성
            holdings = []
            total_market_value = 0

            for symbol, position in portfolio.positions.items():
                current_price = await self._get_current_price(symbol)
                market_value = position.quantity * current_price
                unrealized_pnl = market_value - (position.average_price * position.quantity)
                weight = (market_value / portfolio.total_value) * 100 if portfolio.total_value > 0 else 0

                total_market_value += market_value

                holdings.append({
                    "symbol": symbol,
                    "name": await self._get_symbol_name(symbol),
                    "quantity": position.quantity,
                    "avg_price": position.average_price,
                    "current_price": current_price,
                    "market_value": market_value,
                    "unrealized_pnl": unrealized_pnl,
                    "weight": round(weight, 2)
                })

            # 최근 거래 내역
            recent_trades = self.trade_history.get(player_id, [])[-10:]  # 최근 10건

            # 총 수익률 계산
            total_return = ((portfolio.total_value - portfolio.initial_cash) / portfolio.initial_cash) * 100

            return self._create_response(
                success=True,
                data={
                    "portfolio_id": portfolio.portfolio_id,
                    "total_value": portfolio.total_value,
                    "cash_balance": portfolio.current_cash,
                    "market_value": total_market_value,
                    "total_return": round(total_return, 2),
                    "holdings": holdings,
                    "recent_trades": recent_trades
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_portfolio")

    async def place_order(
        self,
        player_id: str,
        symbol: str,
        order_type: str,
        side: str,
        quantity: int,
        price: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """주문 실행"""
        try:
            self._validate_initialized()

            if player_id not in self.portfolios:
                return self._create_response(
                    success=False,
                    message="Portfolio not found",
                    error_code="PORTFOLIO_NOT_FOUND"
                )

            portfolio = self.portfolios[player_id]

            # 주문 객체 생성
            order = Order(
                order_id=str(uuid.uuid4()),
                symbol=symbol,
                order_type=OrderType(order_type),
                side=OrderSide(side),
                quantity=quantity,
                price=price,
                player_id=player_id,
                timestamp=datetime.now()
            )

            # 매수 주문 시 현금 확인
            if side == "buy":
                execution_price = price if order_type == "limit" else await self._get_current_price(symbol)
                required_cash = quantity * execution_price

                if portfolio.current_cash < required_cash:
                    return self._create_response(
                        success=False,
                        message="Insufficient cash",
                        error_code="INSUFFICIENT_CASH"
                    )

            # 매도 주문 시 보유 수량 확인
            if side == "sell":
                position = portfolio.positions.get(symbol)
                if not position or position.quantity < quantity:
                    return self._create_response(
                        success=False,
                        message="Insufficient shares",
                        error_code="INSUFFICIENT_SHARES"
                    )

            # 주문 실행
            execution_result = await self.order_system.execute_order(order)

            if execution_result["status"] == "filled":
                # 포트폴리오 업데이트
                await self._update_portfolio_position(
                    portfolio,
                    symbol,
                    side,
                    quantity,
                    execution_result["execution_price"]
                )

                # 거래 내역 기록
                trade_record = {
                    "trade_id": str(uuid.uuid4()),
                    "symbol": symbol,
                    "type": side,
                    "quantity": quantity,
                    "price": execution_result["execution_price"],
                    "timestamp": execution_result["execution_time"],
                    "reason": reason or ""
                }

                self.trade_history[player_id].append(trade_record)

                # 포트폴리오 총액 업데이트
                await self._update_portfolio_values(portfolio)

                return self._create_response(
                    success=True,
                    data={
                        "order_id": order.order_id,
                        "status": "filled",
                        "execution_price": execution_result["execution_price"],
                        "execution_time": execution_result["execution_time"],
                        "portfolio_update": {
                            "new_cash_balance": portfolio.current_cash,
                            "new_total_value": portfolio.total_value,
                            "position_update": self._get_position_info(portfolio, symbol)
                        }
                    }
                )

            else:
                return self._create_response(
                    success=False,
                    message="Order execution failed",
                    error_code="EXECUTION_FAILED",
                    data=execution_result
                )

        except Exception as e:
            return self._handle_error(e, "place_order")

    async def get_performance_analysis(self, player_id: str) -> Dict[str, Any]:
        """포트폴리오 성과 분석"""
        try:
            self._validate_initialized()

            if player_id not in self.portfolios:
                return self._create_response(
                    success=False,
                    message="Portfolio not found",
                    error_code="PORTFOLIO_NOT_FOUND"
                )

            portfolio = self.portfolios[player_id]
            trades = self.trade_history.get(player_id, [])

            # 기본 성과 지표
            total_return = ((portfolio.total_value - portfolio.initial_cash) / portfolio.initial_cash) * 100
            realized_pnl = self._calculate_realized_pnl(trades)
            unrealized_pnl = portfolio.total_value - portfolio.current_cash - portfolio.initial_cash + realized_pnl

            # 거래 통계
            buy_trades = [t for t in trades if t["type"] == "buy"]
            sell_trades = [t for t in trades if t["type"] == "sell"]

            # 섹터별 분산도
            sector_allocation = await self._calculate_sector_allocation(portfolio)

            # 위험 지표
            risk_metrics = await self._calculate_risk_metrics(portfolio, trades)

            return self._create_response(
                success=True,
                data={
                    "performance": {
                        "total_return": round(total_return, 2),
                        "realized_pnl": round(realized_pnl, 2),
                        "unrealized_pnl": round(unrealized_pnl, 2),
                        "initial_value": portfolio.initial_cash,
                        "current_value": portfolio.total_value
                    },
                    "trading_stats": {
                        "total_trades": len(trades),
                        "buy_trades": len(buy_trades),
                        "sell_trades": len(sell_trades),
                        "avg_trade_size": sum(t["quantity"] * t["price"] for t in trades) / len(trades) if trades else 0
                    },
                    "allocation": {
                        "cash_ratio": (portfolio.current_cash / portfolio.total_value) * 100,
                        "equity_ratio": ((portfolio.total_value - portfolio.current_cash) / portfolio.total_value) * 100,
                        "sector_allocation": sector_allocation
                    },
                    "risk_metrics": risk_metrics
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_performance_analysis")

    async def _update_portfolio_values(self, portfolio: RealPortfolio):
        """포트폴리오 값 업데이트"""
        total_market_value = portfolio.current_cash

        for symbol, position in portfolio.positions.items():
            current_price = await self._get_current_price(symbol)
            market_value = position.quantity * current_price
            total_market_value += market_value

        portfolio.total_value = total_market_value

    async def _update_portfolio_position(
        self,
        portfolio: RealPortfolio,
        symbol: str,
        side: str,
        quantity: int,
        price: float
    ):
        """포지션 업데이트"""
        if side == "buy":
            # 매수
            total_cost = quantity * price
            portfolio.current_cash -= total_cost

            if symbol in portfolio.positions:
                position = portfolio.positions[symbol]
                total_quantity = position.quantity + quantity
                total_cost_basis = (position.quantity * position.average_price) + total_cost
                new_avg_price = total_cost_basis / total_quantity

                position.quantity = total_quantity
                position.average_price = new_avg_price
            else:
                portfolio.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    average_price=price
                )

        elif side == "sell":
            # 매도
            sell_proceeds = quantity * price
            portfolio.current_cash += sell_proceeds

            position = portfolio.positions[symbol]
            position.quantity -= quantity

            if position.quantity == 0:
                del portfolio.positions[symbol]

    async def _get_current_price(self, symbol: str) -> float:
        """현재 주가 조회 - MarketService 연동"""
        # MarketService가 있으면 실시간 시세 조회
        if self.market_service:
            try:
                quote_result = await self.market_service.get_quote(symbol)
                if quote_result.get("success"):
                    price = quote_result["data"].get("current_price")
                    if price:
                        # 캐시 업데이트
                        self._fallback_prices[symbol] = price
                        return price
            except Exception as e:
                self.logger.warning(f"MarketService 시세 조회 실패 ({symbol}): {e}")

        # 폴백: 캐시된 가격 사용
        return self._fallback_prices.get(symbol, 10000)

    async def _get_symbol_name(self, symbol: str) -> str:
        """종목명 조회 - MarketService 연동"""
        # MarketService가 있으면 캐시에서 조회
        if self.market_service and hasattr(self.market_service, 'symbols_cache'):
            symbol_info = self.market_service.symbols_cache.get(symbol)
            if symbol_info:
                return symbol_info.get("name", symbol)

        # 폴백: 기본 종목명
        fallback_names = {
            "005930.KS": "삼성전자",
            "000660.KS": "SK하이닉스",
            "035420.KS": "NAVER",
            "051910.KS": "LG화학",
            "207940.KS": "삼성바이오로직스",
            "006400.KS": "삼성SDI",
            "028260.KS": "삼성물산",
            "068270.KS": "셀트리온",
            "005380.KS": "현대차",
            "035720.KS": "카카오",
        }
        return fallback_names.get(symbol, symbol)

    def _get_position_info(self, portfolio: RealPortfolio, symbol: str) -> Optional[Dict[str, Any]]:
        """포지션 정보 반환"""
        if symbol not in portfolio.positions:
            return None

        position = portfolio.positions[symbol]
        return {
            "symbol": symbol,
            "quantity": position.quantity,
            "average_price": position.average_price
        }

    def _calculate_realized_pnl(self, trades: List[Dict[str, Any]]) -> float:
        """실현 손익 계산"""
        # 간단한 FIFO 방식으로 실현 손익 계산
        positions = {}
        realized_pnl = 0

        for trade in trades:
            symbol = trade["symbol"]
            quantity = trade["quantity"]
            price = trade["price"]

            if symbol not in positions:
                positions[symbol] = []

            if trade["type"] == "buy":
                positions[symbol].append({"quantity": quantity, "price": price})
            elif trade["type"] == "sell":
                remaining_sell = quantity
                while remaining_sell > 0 and positions[symbol]:
                    buy_lot = positions[symbol][0]
                    if buy_lot["quantity"] <= remaining_sell:
                        # 전체 매도
                        realized_pnl += buy_lot["quantity"] * (price - buy_lot["price"])
                        remaining_sell -= buy_lot["quantity"]
                        positions[symbol].pop(0)
                    else:
                        # 부분 매도
                        realized_pnl += remaining_sell * (price - buy_lot["price"])
                        buy_lot["quantity"] -= remaining_sell
                        remaining_sell = 0

        return realized_pnl

    async def _calculate_sector_allocation(self, portfolio: RealPortfolio) -> Dict[str, float]:
        """섹터별 자산 배분 계산"""
        # TODO: 실제 섹터 정보 연동
        sector_map = {
            "005930.KS": "Technology",
            "000660.KS": "Technology",
            "035420.KS": "Technology",
            "051910.KS": "Materials",
        }

        sector_values = {}
        total_equity_value = 0

        for symbol, position in portfolio.positions.items():
            current_price = await self._get_current_price(symbol)
            market_value = position.quantity * current_price
            total_equity_value += market_value

            sector = sector_map.get(symbol, "Other")
            sector_values[sector] = sector_values.get(sector, 0) + market_value

        # 비율로 변환
        if total_equity_value > 0:
            return {sector: (value / total_equity_value) * 100
                   for sector, value in sector_values.items()}
        else:
            return {}

    async def _calculate_risk_metrics(
        self,
        portfolio: RealPortfolio,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """위험 지표 계산"""
        # 간단한 위험 지표들
        num_positions = len(portfolio.positions)
        concentration_risk = 0

        if num_positions > 0:
            # 최대 포지션 비중
            max_weight = 0
            for symbol, position in portfolio.positions.items():
                current_price = await self._get_current_price(symbol)
                market_value = position.quantity * current_price
                weight = (market_value / portfolio.total_value) * 100
                max_weight = max(max_weight, weight)

            concentration_risk = max_weight

        return {
            "diversification_score": min(100, num_positions * 10),  # 최대 100점
            "concentration_risk": concentration_risk,
            "position_count": num_positions,
            "cash_ratio": (portfolio.current_cash / portfolio.total_value) * 100
        }