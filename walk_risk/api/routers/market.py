"""시장 데이터 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Optional, List

router = APIRouter()


def get_market_service(request: Request):
    """마켓 서비스 의존성"""
    return request.app.state.services["market"]


@router.get("/symbols")
async def search_symbols(
    search: Optional[str] = Query(None, description="종목명 또는 심볼 검색"),
    market: Optional[str] = Query(None, description="시장 구분"),
    sector: Optional[str] = Query(None, description="섹터 구분"),
    limit: int = Query(20, description="결과 개수 제한"),
    market_service = Depends(get_market_service)
):
    """검색 가능한 종목 목록"""
    result = await market_service.search_symbols(search, market, sector, limit)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/quote/{symbol}")
async def get_quote(
    symbol: str,
    market_service = Depends(get_market_service)
):
    """실시간 시세 조회"""
    result = await market_service.get_quote(symbol)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "SYMBOL_NOT_FOUND":
            raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/quotes")
async def get_multiple_quotes(
    symbols: List[str],
    market_service = Depends(get_market_service)
):
    """다중 종목 시세 조회"""
    result = await market_service.get_multiple_quotes(symbols)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/overview")
async def get_market_overview(
    market_service = Depends(get_market_service)
):
    """시장 개요 조회"""
    result = await market_service.get_market_overview()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result["data"]


@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1M", description="조회 기간 (1D, 1W, 1M, 3M, 6M, 1Y, 2Y)"),
    interval: str = Query("1d", description="데이터 간격 (1d, 1h)"),
    market_service = Depends(get_market_service)
):
    """과거 데이터 조회"""
    result = await market_service.get_historical_data(symbol, period, interval)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "SYMBOL_NOT_FOUND":
            raise HTTPException(status_code=404, detail="종목을 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/news")
async def get_market_news(
    limit: int = Query(10, description="뉴스 개수"),
    market_service = Depends(get_market_service)
):
    """시장 뉴스 조회"""
    result = await market_service.get_market_news(limit)

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result["data"]


@router.get("/sectors")
async def get_sector_performance():
    """섹터별 성과 조회"""
    # TODO: 섹터 성과 로직 구현
    # 현재는 모의 응답

    sectors = [
        {
            "sector": "Technology",
            "change_percent": -1.2,
            "volume": 1200000000,
            "market_cap": 850000000000,
            "top_stocks": [
                {"symbol": "005930.KS", "name": "삼성전자", "change_percent": -2.1},
                {"symbol": "000660.KS", "name": "SK하이닉스", "change_percent": -0.8},
                {"symbol": "035420.KS", "name": "NAVER", "change_percent": +1.5}
            ]
        },
        {
            "sector": "Healthcare",
            "change_percent": +2.1,
            "volume": 350000000,
            "market_cap": 280000000000,
            "top_stocks": [
                {"symbol": "207940.KS", "name": "삼성바이오로직스", "change_percent": +3.2},
                {"symbol": "068270.KS", "name": "셀트리온", "change_percent": +1.8}
            ]
        },
        {
            "sector": "Materials",
            "change_percent": -0.8,
            "volume": 280000000,
            "market_cap": 180000000000,
            "top_stocks": [
                {"symbol": "051910.KS", "name": "LG화학", "change_percent": -1.2}
            ]
        }
    ]

    return {"sectors": sectors}


@router.get("/indices")
async def get_market_indices():
    """주요 지수 조회"""
    indices = [
        {
            "name": "KOSPI",
            "symbol": "KS11",
            "value": 2850.5,
            "change": -15.2,
            "change_percent": -0.53,
            "volume": 450000000,
            "timestamp": "2025-09-30T15:30:00Z"
        },
        {
            "name": "KOSDAQ",
            "symbol": "KQ11",
            "value": 915.8,
            "change": +8.3,
            "change_percent": +0.92,
            "volume": 680000000,
            "timestamp": "2025-09-30T15:30:00Z"
        },
        {
            "name": "KPI200",
            "symbol": "KS200",
            "value": 385.2,
            "change": -2.1,
            "change_percent": -0.54,
            "volume": 0,
            "timestamp": "2025-09-30T15:30:00Z"
        }
    ]

    return {"indices": indices}


@router.get("/movers")
async def get_market_movers(
    mover_type: str = Query("gainers", description="상승/하락 구분 (gainers, losers, active)"),
    limit: int = Query(10, description="결과 개수")
):
    """시장 주요 변동 종목"""
    # TODO: 실제 변동 종목 로직 구현
    # 현재는 모의 응답

    if mover_type == "gainers":
        movers = [
            {"symbol": "068270.KS", "name": "셀트리온", "change_percent": +5.8, "volume": 2500000},
            {"symbol": "207940.KS", "name": "삼성바이오로직스", "change_percent": +4.2, "volume": 180000},
            {"symbol": "035420.KS", "name": "NAVER", "change_percent": +3.1, "volume": 980000}
        ]
    elif mover_type == "losers":
        movers = [
            {"symbol": "005930.KS", "name": "삼성전자", "change_percent": -3.2, "volume": 15000000},
            {"symbol": "000660.KS", "name": "SK하이닉스", "change_percent": -2.8, "volume": 8500000},
            {"symbol": "051910.KS", "name": "LG화학", "change_percent": -1.9, "volume": 450000}
        ]
    else:  # active
        movers = [
            {"symbol": "005930.KS", "name": "삼성전자", "change_percent": -3.2, "volume": 15000000},
            {"symbol": "000660.KS", "name": "SK하이닉스", "change_percent": -2.8, "volume": 8500000},
            {"symbol": "068270.KS", "name": "셀트리온", "change_percent": +5.8, "volume": 2500000}
        ]

    return {
        "type": mover_type,
        "movers": movers[:limit]
    }


@router.get("/status")
async def get_market_status():
    """시장 상태 조회"""
    # TODO: 실제 시장 상태 로직 구현

    return {
        "market_status": "market_hours",  # "market_hours", "after_hours", "pre_market", "closed"
        "trading_session": "regular",
        "next_open": "2025-10-01T09:00:00Z",
        "next_close": "2025-09-30T15:30:00Z",
        "timezone": "Asia/Seoul",
        "last_updated": "2025-09-30T15:45:00Z"
    }