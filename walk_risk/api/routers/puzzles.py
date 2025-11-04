"""퍼즐 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter()


class InvestigateRequest(BaseModel):
    clue_id: str
    investigation_type: str


class HypothesisRequest(BaseModel):
    hypothesis: str
    confidence: int
    evidence: List[str]
    predicted_outcome: str


class PuzzleListResponse(BaseModel):
    puzzle_id: str
    title: str
    description: str
    difficulty: str
    type: str
    target_symbol: str
    estimated_time: int
    reward_xp: int
    is_solved: bool
    created_at: str


def get_puzzle_service(request: Request):
    """퍼즐 서비스 의존성"""
    return request.app.state.services["puzzle"]


@router.get("/")
async def get_available_puzzles(
    difficulty: Optional[str] = Query(None, description="퍼즐 난이도"),
    puzzle_type: Optional[str] = Query(None, description="퍼즐 타입"),
    limit: int = Query(10, description="결과 개수 제한"),
    offset: int = Query(0, description="오프셋"),
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """사용 가능한 퍼즐 목록 조회"""
    result = await puzzle_service.get_available_puzzles(
        player_id, difficulty, puzzle_type, limit, offset
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/{puzzle_id}")
async def get_puzzle_details(
    puzzle_id: str,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """특정 퍼즐 상세 조회"""
    result = await puzzle_service.get_puzzle_details(puzzle_id, player_id)

    if not result["success"]:
        if result.get("error_code") == "PUZZLE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="퍼즐을 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/{puzzle_id}/investigate")
async def investigate_clue(
    puzzle_id: str,
    request: InvestigateRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """단서 조사 실행"""
    result = await puzzle_service.investigate_clue(
        puzzle_id,
        player_id,
        request.clue_id,
        request.investigation_type
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PUZZLE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="퍼즐을 찾을 수 없습니다")
        elif error_code == "CLUE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="단서를 찾을 수 없습니다")
        elif error_code == "CLUE_ALREADY_DISCOVERED":
            raise HTTPException(status_code=400, detail="이미 발견한 단서입니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/{puzzle_id}/hypothesis")
async def submit_hypothesis(
    puzzle_id: str,
    request: HypothesisRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """가설 제출"""
    result = await puzzle_service.submit_hypothesis(
        puzzle_id,
        player_id,
        request.hypothesis,
        request.confidence,
        request.evidence,
        request.predicted_outcome
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "PUZZLE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="퍼즐을 찾을 수 없습니다")
        elif error_code == "PUZZLE_NOT_STARTED":
            raise HTTPException(status_code=400, detail="퍼즐을 먼저 시작해주세요")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/daily")
async def create_daily_puzzles(
    puzzle_service = Depends(get_puzzle_service)
):
    """일일 퍼즐 생성 (관리자용)"""
    result = await puzzle_service.create_daily_puzzles()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result["data"]


@router.get("/{puzzle_id}/hints")
async def get_puzzle_hints(
    puzzle_id: str,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """퍼즐 힌트 조회"""
    # TODO: 힌트 시스템 구현
    # 현재는 모의 응답

    hints = [
        {
            "hint_id": "hint_1",
            "text": "뉴스를 먼저 확인해보세요",
            "cost": 0,
            "available": True
        },
        {
            "hint_id": "hint_2",
            "text": "재무 지표를 분석해보세요",
            "cost": 50,
            "available": True
        },
        {
            "hint_id": "hint_3",
            "text": "시장 전체 상황을 고려해보세요",
            "cost": 100,
            "available": False
        }
    ]

    return {"hints": hints}


@router.get("/stats/summary")
async def get_puzzle_stats(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    puzzle_service = Depends(get_puzzle_service)
):
    """퍼즐 통계 요약"""
    # TODO: 통계 시스템 구현
    # 현재는 모의 응답

    return {
        "total_puzzles_solved": 15,
        "total_puzzles_attempted": 23,
        "success_rate": 65.2,
        "average_time": 12.5,  # 분
        "favorite_difficulty": "intermediate",
        "total_xp_earned": 3450,
        "achievements": [
            "first_puzzle_solver",
            "speed_solver",
            "detective_master"
        ]
    }