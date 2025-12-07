"""퍼즐 관련 API 엔드포인트"""

from typing import Annotated, Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ...auth.dependencies import get_current_user
from ...database.connection import get_db
from ...database.models import User, PuzzleProgress

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
    current_user: Annotated[User, Depends(get_current_user)],
    difficulty: Optional[str] = Query(None, description="퍼즐 난이도"),
    puzzle_type: Optional[str] = Query(None, description="퍼즐 타입"),
    limit: int = Query(10, description="결과 개수 제한"),
    offset: int = Query(0, description="오프셋"),
    puzzle_service = Depends(get_puzzle_service)
):
    """사용 가능한 퍼즐 목록 조회"""
    result = await puzzle_service.get_available_puzzles(
        current_user.id, difficulty, puzzle_type, limit, offset
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/{puzzle_id}")
async def get_puzzle_details(
    puzzle_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    puzzle_service = Depends(get_puzzle_service)
):
    """특정 퍼즐 상세 조회"""
    result = await puzzle_service.get_puzzle_details(puzzle_id, current_user.id)

    if not result["success"]:
        if result.get("error_code") == "PUZZLE_NOT_FOUND":
            raise HTTPException(status_code=404, detail="퍼즐을 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/{puzzle_id}/investigate")
async def investigate_clue(
    puzzle_id: str,
    request: InvestigateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    puzzle_service = Depends(get_puzzle_service)
):
    """단서 조사 실행"""
    result = await puzzle_service.investigate_clue(
        puzzle_id,
        current_user.id,
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
    current_user: Annotated[User, Depends(get_current_user)],
    puzzle_service = Depends(get_puzzle_service)
):
    """가설 제출"""
    result = await puzzle_service.submit_hypothesis(
        puzzle_id,
        current_user.id,
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
    current_user: Annotated[User, Depends(get_current_user)],
    puzzle_service = Depends(get_puzzle_service)
):
    """일일 퍼즐 생성 (관리자용)"""
    result = await puzzle_service.create_daily_puzzles()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result["data"]


def get_mentor_service(request: Request):
    """멘토 서비스 의존성"""
    return request.app.state.services.get("mentor")


@router.get("/{puzzle_id}/hints")
async def get_puzzle_hints(
    puzzle_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    puzzle_service = Depends(get_puzzle_service),
    mentor_service = Depends(get_mentor_service)
):
    """퍼즐 힌트 조회 - 멘토 기반 힌트 시스템"""
    # 퍼즐 정보 조회
    puzzle_result = await puzzle_service.get_puzzle_details(puzzle_id, current_user.id)
    if not puzzle_result["success"]:
        raise HTTPException(status_code=404, detail="퍼즐을 찾을 수 없습니다")

    puzzle_data = puzzle_result["data"]
    discovered_clues = puzzle_data.get("discovered_clues", [])
    available_clues = puzzle_data.get("available_clues", [])

    # 기본 힌트 구성
    hints = []

    # 단서 수에 따른 힌트 레벨
    clue_count = len(discovered_clues)

    # 레벨 1 힌트: 항상 무료
    hints.append({
        "hint_id": "hint_basic",
        "level": 1,
        "text": f"현재 {clue_count}개의 단서를 발견했습니다. " +
                ("아직 조사를 시작하지 않았네요. 뉴스부터 확인해보세요." if clue_count == 0 else
                 "더 많은 단서를 수집하면 패턴이 보일 거예요."),
        "cost": 0,
        "available": True,
        "unlocked": True
    })

    # 레벨 2 힌트: 50 XP 비용
    undiscovered_types = set()
    for clue in available_clues:
        if clue["clue_id"] not in [c.get("clue_id") for c in discovered_clues]:
            undiscovered_types.add(clue.get("type", "unknown"))

    hints.append({
        "hint_id": "hint_direction",
        "level": 2,
        "text": f"아직 확인하지 않은 단서 유형: {', '.join(undiscovered_types) if undiscovered_types else '모든 단서를 발견했습니다'}",
        "cost": 50,
        "available": current_user.experience >= 50,
        "unlocked": clue_count >= 2
    })

    # 레벨 3 힌트: 멘토 기반 힌트 (100 XP)
    mentor_hint = "시장의 큰 흐름을 보세요. 개별 종목이 아닌 섹터 전체의 움직임을 관찰하면 답이 보일 겁니다."
    if mentor_service:
        try:
            mentor_response = await mentor_service.get_advice(
                current_user.id,
                f"퍼즐 힌트 요청: {puzzle_data.get('title', '알 수 없는 퍼즐')}",
                context={"puzzle_type": puzzle_data.get("type"), "discovered_clues": clue_count}
            )
            if mentor_response.get("success"):
                mentor_hint = mentor_response["data"].get("advice", mentor_hint)
        except Exception:
            pass

    hints.append({
        "hint_id": "hint_mentor",
        "level": 3,
        "text": mentor_hint,
        "cost": 100,
        "available": current_user.experience >= 100,
        "unlocked": clue_count >= 3,
        "mentor": current_user.preferred_mentor
    })

    return {
        "puzzle_id": puzzle_id,
        "hints": hints,
        "player_xp": current_user.experience
    }


@router.get("/stats/summary")
async def get_puzzle_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """퍼즐 통계 요약 - 실제 DB에서 조회"""
    # 전체 퍼즐 시도 횟수
    total_stmt = select(func.count(PuzzleProgress.id)).where(
        PuzzleProgress.user_id == current_user.id
    )
    total_result = await db.execute(total_stmt)
    total_attempts = total_result.scalar() or 0

    # 해결한 퍼즐 수
    solved_stmt = select(func.count(PuzzleProgress.id)).where(
        PuzzleProgress.user_id == current_user.id,
        PuzzleProgress.is_solved == True
    )
    solved_result = await db.execute(solved_stmt)
    total_solved = solved_result.scalar() or 0

    # 획득한 총 XP
    xp_stmt = select(func.sum(PuzzleProgress.xp_earned)).where(
        PuzzleProgress.user_id == current_user.id
    )
    xp_result = await db.execute(xp_stmt)
    total_xp = xp_result.scalar() or 0

    # 성공률 계산
    success_rate = (total_solved / total_attempts * 100) if total_attempts > 0 else 0.0

    # 최근 퍼즐 진행 상황
    recent_stmt = select(PuzzleProgress).where(
        PuzzleProgress.user_id == current_user.id
    ).order_by(PuzzleProgress.started_at.desc()).limit(5)
    recent_result = await db.execute(recent_stmt)
    recent_puzzles = recent_result.scalars().all()

    return {
        "total_puzzles_attempted": total_attempts,
        "total_puzzles_solved": total_solved,
        "success_rate": round(success_rate, 1),
        "total_xp_earned": total_xp,
        "player_level": current_user.level,
        "player_class": current_user.current_class,
        "recent_activity": [
            {
                "puzzle_id": p.puzzle_id,
                "is_solved": p.is_solved,
                "xp_earned": p.xp_earned,
                "started_at": p.started_at.isoformat() if p.started_at else None
            }
            for p in recent_puzzles
        ]
    }