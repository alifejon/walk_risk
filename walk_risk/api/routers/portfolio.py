"""포트폴리오 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

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
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """현재 포트폴리오 조회"""
    result = await portfolio_service.get_portfolio(player_id)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PORTFOLIO_NOT_FOUND":
            # 포트폴리오가 없으면 생성
            create_result = await portfolio_service.create_portfolio(player_id)
            if create_result["success"]:
                # 생성 후 다시 조회
                result = await portfolio_service.get_portfolio(player_id)
            else:
                raise HTTPException(status_code=500, detail="포트폴리오 생성에 실패했습니다")

        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/orders")
async def place_order(
    request: PlaceOrderRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """주문 실행"""
    result = await portfolio_service.place_order(
        player_id,
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
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """포트폴리오 성과 분석"""
    result = await portfolio_service.get_performance_analysis(player_id)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PORTFOLIO_NOT_FOUND":
            raise HTTPException(status_code=404, detail="포트폴리오를 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/history")
async def get_trading_history(
    limit: int = 20,
    offset: int = 0,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """거래 내역 조회"""
    # TODO: 거래 내역 조회 로직 구현
    # 현재는 모의 응답

    mock_trades = [
        {
            "trade_id": "trade_1",
            "symbol": "005930.KS",
            "name": "삼성전자",
            "type": "buy",
            "quantity": 10,
            "price": 75000,
            "total_amount": 750000,
            "timestamp": "2025-09-30T10:30:00Z",
            "reason": "퍼즐 해결 결과 매수 판단"
        },
        {
            "trade_id": "trade_2",
            "symbol": "035420.KS",
            "name": "NAVER",
            "type": "buy",
            "quantity": 5,
            "price": 180000,
            "total_amount": 900000,
            "timestamp": "2025-09-29T14:15:00Z",
            "reason": "장기 성장 전망"
        }
    ]

    total_trades = len(mock_trades)
    trades = mock_trades[offset:offset + limit]

    return {
        "trades": trades,
        "total": total_trades,
        "has_more": offset + len(trades) < total_trades
    }


@router.get("/positions")
async def get_positions(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """현재 포지션 상세 조회"""
    portfolio_result = await portfolio_service.get_portfolio(player_id)

    if not portfolio_result["success"]:
        raise HTTPException(status_code=400, detail=portfolio_result["message"])

    portfolio_data = portfolio_result["data"]

    # 포지션별 상세 정보 추가
    detailed_positions = []
    for holding in portfolio_data.get("holdings", []):
        position_detail = {
            **holding,
            "profit_loss": holding["unrealized_pnl"],
            "profit_loss_percent": (holding["unrealized_pnl"] / (holding["avg_price"] * holding["quantity"])) * 100,
            "days_held": 15,  # TODO: 실제 보유 일수 계산
            "dividend_yield": 2.1,  # TODO: 실제 배당률 조회
        }
        detailed_positions.append(position_detail)

    return {
        "positions": detailed_positions,
        "summary": {
            "total_positions": len(detailed_positions),
            "total_market_value": portfolio_data.get("total_value", 0) - portfolio_data.get("cash_balance", 0),
            "total_unrealized_pnl": sum(p["unrealized_pnl"] for p in portfolio_data.get("holdings", [])),
            "best_performer": max(detailed_positions, key=lambda x: x["profit_loss_percent"]) if detailed_positions else None,
            "worst_performer": min(detailed_positions, key=lambda x: x["profit_loss_percent"]) if detailed_positions else None
        }
    }


@router.get("/allocation")
async def get_allocation_analysis(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """자산 배분 분석"""
    performance_result = await portfolio_service.get_performance_analysis(player_id)

    if not performance_result["success"]:
        raise HTTPException(status_code=400, detail=performance_result["message"])

    allocation_data = performance_result["data"].get("allocation", {})

    return {
        "asset_allocation": {
            "cash": allocation_data.get("cash_ratio", 0),
            "stocks": allocation_data.get("equity_ratio", 0)
        },
        "sector_allocation": allocation_data.get("sector_allocation", {}),
        "recommendations": [
            "기술주 비중이 높으니 다른 섹터도 고려해보세요",
            "현금 비중을 줄이고 투자 비중을 늘려보세요"
        ]
    }


@router.post("/rebalance")
async def suggest_rebalancing(
    target_allocation: dict,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    portfolio_service = Depends(get_portfolio_service)
):
    """포트폴리오 리밸런싱 제안"""
    # TODO: 리밸런싱 로직 구현
    # 현재는 모의 응답

    return {
        "rebalancing_needed": True,
        "current_allocation": {
            "Technology": 75,
            "Healthcare": 15,
            "Cash": 10
        },
        "target_allocation": target_allocation,
        "suggested_trades": [
            {
                "action": "sell",
                "symbol": "005930.KS",
                "quantity": 5,
                "reason": "기술주 비중 조정"
            },
            {
                "action": "buy",
                "symbol": "068270.KS",
                "quantity": 3,
                "reason": "헬스케어 비중 증가"
            }
        ],
        "estimated_cost": 15000  # 거래 수수료
    }