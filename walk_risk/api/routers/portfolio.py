"""포트폴리오 관련 API 엔드포인트"""

from typing import Annotated, Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ...auth.dependencies import get_current_user
from ...database.connection import get_db
from ...database.models import User, Portfolio, Position, Order

router = APIRouter()


class PlaceOrderRequest(BaseModel):
    symbol: str
    order_type: str  # "market", "limit"
    side: str  # "buy", "sell"
    quantity: int
    price: Optional[float] = None
    reason: Optional[str] = None


def get_portfolio_service(request: Request):
    """포트폴리오 서비스 의존성"""
    return request.app.state.services["portfolio"]


@router.get("/")
async def get_portfolio(
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service = Depends(get_portfolio_service)
):
    """현재 포트폴리오 조회"""
    result = await portfolio_service.get_portfolio(current_user.id)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PORTFOLIO_NOT_FOUND":
            # 포트폴리오가 없으면 생성
            create_result = await portfolio_service.create_portfolio(current_user.id)
            if create_result["success"]:
                # 생성 후 다시 조회
                result = await portfolio_service.get_portfolio(current_user.id)
            else:
                raise HTTPException(status_code=500, detail="포트폴리오 생성에 실패했습니다")

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/orders")
async def place_order(
    request: PlaceOrderRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service = Depends(get_portfolio_service)
):
    """주문 실행"""
    result = await portfolio_service.place_order(
        current_user.id,
        request.symbol,
        request.order_type,
        request.side,
        request.quantity,
        request.price,
        request.reason
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PORTFOLIO_NOT_FOUND":
            raise HTTPException(status_code=404, detail="포트폴리오를 찾을 수 없습니다")
        elif error_code == "INSUFFICIENT_CASH":
            raise HTTPException(status_code=400, detail="현금이 부족합니다")
        elif error_code == "INSUFFICIENT_SHARES":
            raise HTTPException(status_code=400, detail="보유 주식이 부족합니다")
        elif error_code == "EXECUTION_FAILED":
            raise HTTPException(status_code=400, detail="주문 실행에 실패했습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/performance")
async def get_performance_analysis(
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service = Depends(get_portfolio_service)
):
    """포트폴리오 성과 분석"""
    result = await portfolio_service.get_performance_analysis(current_user.id)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PORTFOLIO_NOT_FOUND":
            raise HTTPException(status_code=404, detail="포트폴리오를 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/history")
async def get_trading_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 20,
    offset: int = 0,
    symbol: Optional[str] = None,
    side: Optional[str] = None
):
    """거래 내역 조회 - 실제 DB에서 조회"""
    # 사용자의 포트폴리오 조회
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolio = portfolio_result.scalar_one_or_none()

    if not portfolio:
        return {"trades": [], "total": 0, "has_more": False}

    # 주문 내역 조회
    order_stmt = select(Order).where(
        Order.portfolio_id == portfolio.id,
        Order.status == "filled"
    )

    if symbol:
        order_stmt = order_stmt.where(Order.symbol == symbol)
    if side:
        order_stmt = order_stmt.where(Order.side == side)

    order_stmt = order_stmt.order_by(desc(Order.created_at)).offset(offset).limit(limit + 1)
    order_result = await db.execute(order_stmt)
    orders = order_result.scalars().all()

    has_more = len(orders) > limit
    orders = orders[:limit]

    # 총 거래 수 조회
    from sqlalchemy import func
    count_stmt = select(func.count(Order.id)).where(
        Order.portfolio_id == portfolio.id,
        Order.status == "filled"
    )
    if symbol:
        count_stmt = count_stmt.where(Order.symbol == symbol)
    if side:
        count_stmt = count_stmt.where(Order.side == side)

    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # 종목명 매핑
    STOCK_NAMES = {
        "005930.KS": "삼성전자",
        "000660.KS": "SK하이닉스",
        "035420.KS": "NAVER",
        "051910.KS": "LG화학",
        "005380.KS": "현대차",
        "035720.KS": "카카오",
    }

    trades = [
        {
            "trade_id": str(order.id),
            "symbol": order.symbol,
            "name": STOCK_NAMES.get(order.symbol, order.symbol),
            "type": order.side,
            "quantity": order.quantity,
            "price": order.execution_price or order.price,
            "total_amount": (order.execution_price or order.price or 0) * order.quantity,
            "timestamp": order.created_at.isoformat() if order.created_at else None,
            "reason": order.reason
        }
        for order in orders
    ]

    return {
        "trades": trades,
        "total": total,
        "has_more": has_more,
        "pagination": {
            "offset": offset,
            "limit": limit
        }
    }


@router.get("/positions")
async def get_positions(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    portfolio_service = Depends(get_portfolio_service)
):
    """현재 포지션 상세 조회"""
    portfolio_result = await portfolio_service.get_portfolio(current_user.id)

    if not portfolio_result["success"]:
        raise HTTPException(status_code=400, detail=portfolio_result["message"])

    portfolio_data = portfolio_result["data"]

    # DB에서 포트폴리오 조회하여 생성일 확인
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    db_result = await db.execute(portfolio_stmt)
    db_portfolio = db_result.scalar_one_or_none()

    # 포지션별 상세 정보 추가
    detailed_positions = []
    for holding in portfolio_data.get("holdings", []):
        # 보유 일수 계산
        days_held = 0
        if db_portfolio:
            position_stmt = select(Position).where(
                Position.portfolio_id == db_portfolio.id,
                Position.symbol == holding.get("symbol")
            )
            pos_result = await db.execute(position_stmt)
            position = pos_result.scalar_one_or_none()
            if position and position.created_at:
                from datetime import datetime
                days_held = (datetime.utcnow() - position.created_at).days

        avg_price = holding.get("avg_price", 0)
        quantity = holding.get("quantity", 0)
        cost_basis = avg_price * quantity if avg_price and quantity else 1

        position_detail = {
            **holding,
            "profit_loss": holding.get("unrealized_pnl", 0),
            "profit_loss_percent": (holding.get("unrealized_pnl", 0) / cost_basis * 100) if cost_basis else 0,
            "days_held": days_held,
        }
        detailed_positions.append(position_detail)

    return {
        "positions": detailed_positions,
        "summary": {
            "total_positions": len(detailed_positions),
            "total_market_value": portfolio_data.get("total_value", 0) - portfolio_data.get("cash_balance", 0),
            "total_unrealized_pnl": sum(p.get("unrealized_pnl", 0) for p in portfolio_data.get("holdings", [])),
            "best_performer": max(detailed_positions, key=lambda x: x["profit_loss_percent"]) if detailed_positions else None,
            "worst_performer": min(detailed_positions, key=lambda x: x["profit_loss_percent"]) if detailed_positions else None
        }
    }


@router.get("/allocation")
async def get_allocation_analysis(
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service = Depends(get_portfolio_service)
):
    """자산 배분 분석"""
    performance_result = await portfolio_service.get_performance_analysis(current_user.id)

    if not performance_result["success"]:
        raise HTTPException(status_code=400, detail=performance_result["message"])

    allocation_data = performance_result["data"].get("allocation", {})

    # 동적 추천 생성
    recommendations = []
    cash_ratio = allocation_data.get("cash_ratio", 0)
    sector_allocation = allocation_data.get("sector_allocation", {})

    if cash_ratio > 30:
        recommendations.append("현금 비중이 높습니다. 시장 상황을 보며 투자 기회를 모색해보세요.")
    elif cash_ratio < 10:
        recommendations.append("현금 비중이 낮습니다. 리스크 관리를 위해 일부 현금을 확보하세요.")

    # 가장 높은 섹터 비중 확인
    if sector_allocation:
        max_sector = max(sector_allocation.items(), key=lambda x: x[1], default=None)
        if max_sector and max_sector[1] > 50:
            recommendations.append(f"{max_sector[0]} 섹터 비중이 {max_sector[1]:.1f}%로 높습니다. 분산 투자를 고려해보세요.")

    if not recommendations:
        recommendations.append("포트폴리오가 적절히 분산되어 있습니다.")

    return {
        "asset_allocation": {
            "cash": allocation_data.get("cash_ratio", 0),
            "stocks": allocation_data.get("equity_ratio", 0)
        },
        "sector_allocation": sector_allocation,
        "recommendations": recommendations
    }


class RebalanceRequest(BaseModel):
    target_allocation: Dict[str, float]


@router.post("/rebalance")
async def suggest_rebalancing(
    request: RebalanceRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    portfolio_service = Depends(get_portfolio_service)
):
    """포트폴리오 리밸런싱 제안"""
    # 현재 포트폴리오 정보 조회
    performance_result = await portfolio_service.get_performance_analysis(current_user.id)

    if not performance_result["success"]:
        raise HTTPException(status_code=400, detail=performance_result["message"])

    allocation_data = performance_result["data"].get("allocation", {})
    current_sector = allocation_data.get("sector_allocation", {})
    portfolio_data = await portfolio_service.get_portfolio(current_user.id)

    if not portfolio_data["success"]:
        raise HTTPException(status_code=400, detail="포트폴리오를 조회할 수 없습니다")

    total_value = portfolio_data["data"].get("total_value", 0)
    holdings = portfolio_data["data"].get("holdings", [])

    # 리밸런싱 필요 여부 계산
    rebalancing_needed = False
    suggested_trades = []

    for sector, target_pct in request.target_allocation.items():
        current_pct = current_sector.get(sector, 0)
        diff = target_pct - current_pct

        if abs(diff) > 5:  # 5% 이상 차이나면 조정 필요
            rebalancing_needed = True
            target_value = total_value * (target_pct / 100)
            current_value = total_value * (current_pct / 100)
            adjust_amount = target_value - current_value

            # 해당 섹터의 종목 찾기
            sector_holdings = [h for h in holdings if h.get("sector") == sector]

            if diff > 0 and sector_holdings:
                # 매수 제안
                holding = sector_holdings[0]
                quantity = int(adjust_amount / holding.get("current_price", 1))
                if quantity > 0:
                    suggested_trades.append({
                        "action": "buy",
                        "symbol": holding["symbol"],
                        "quantity": quantity,
                        "reason": f"{sector} 비중 증가 ({current_pct:.1f}% → {target_pct:.1f}%)"
                    })
            elif diff < 0 and sector_holdings:
                # 매도 제안
                holding = sector_holdings[0]
                quantity = min(
                    int(abs(adjust_amount) / holding.get("current_price", 1)),
                    holding.get("quantity", 0)
                )
                if quantity > 0:
                    suggested_trades.append({
                        "action": "sell",
                        "symbol": holding["symbol"],
                        "quantity": quantity,
                        "reason": f"{sector} 비중 감소 ({current_pct:.1f}% → {target_pct:.1f}%)"
                    })

    # 예상 거래 비용 계산 (0.1% 수수료 가정)
    estimated_cost = sum(
        abs(t.get("quantity", 0) * 100000 * 0.001)  # 대략적인 비용
        for t in suggested_trades
    )

    return {
        "rebalancing_needed": rebalancing_needed,
        "current_allocation": current_sector,
        "target_allocation": request.target_allocation,
        "suggested_trades": suggested_trades,
        "estimated_cost": int(estimated_cost),
        "total_portfolio_value": total_value
    }