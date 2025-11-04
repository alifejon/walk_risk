"""멘토 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter()


class AskMentorRequest(BaseModel):
    context: str  # "puzzle", "general", "portfolio"
    question: str
    current_situation: Optional[Dict[str, Any]] = None


class MentorResponse(BaseModel):
    id: str
    name: str
    specialty: str
    description: str
    personality_traits: List[str]
    is_available: bool


def get_mentor_service(request: Request):
    """멘토 서비스 의존성"""
    return request.app.state.services["mentor"]


@router.get("/", response_model=Dict[str, List[MentorResponse]])
async def get_available_mentors(
    mentor_service = Depends(get_mentor_service)
):
    """사용 가능한 멘토 목록 조회"""
    result = await mentor_service.get_available_mentors()

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])

    return result["data"]


@router.post("/{mentor_id}/ask")
async def ask_mentor(
    mentor_id: str,
    request: AskMentorRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """멘토에게 조언 요청"""
    result = await mentor_service.ask_mentor(
        player_id,
        mentor_id,
        request.context,
        request.question,
        request.current_situation
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "MENTOR_NOT_FOUND":
            raise HTTPException(status_code=404, detail="멘토를 찾을 수 없습니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/{mentor_id}/interactions")
async def get_mentor_interactions(
    mentor_id: str,
    limit: int = Query(10, description="결과 개수 제한"),
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """특정 멘토와의 상호작용 기록 조회"""
    result = await mentor_service.get_mentor_interaction_history(
        player_id, mentor_id, limit
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/interactions/all")
async def get_all_interactions(
    limit: int = Query(20, description="결과 개수 제한"),
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """모든 멘토와의 상호작용 기록 조회"""
    result = await mentor_service.get_mentor_interaction_history(
        player_id, None, limit
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/recommendations")
async def get_mentor_recommendations(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """플레이어 프로필 기반 멘토 추천"""
    # TODO: 플레이어 서비스에서 프로필 정보 가져오기
    player_profile = {
        "level": 5,
        "experience": 450,
        "current_class": "Risk Walker"
    }

    result = await mentor_service.get_mentor_recommendations(player_id, player_profile)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/{mentor_id}/stats")
async def get_mentor_stats(
    mentor_id: str,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """특정 멘토와의 상호작용 통계"""
    # TODO: 통계 시스템 구현
    # 현재는 모의 응답

    mock_stats = {
        "total_interactions": 25,
        "average_helpfulness": 4.2,
        "most_discussed_topics": [
            {"topic": "퍼즐 해결", "count": 12},
            {"topic": "포트폴리오 관리", "count": 8},
            {"topic": "일반 투자", "count": 5}
        ],
        "relationship_level": "신뢰",
        "first_interaction": "2025-09-15T10:30:00Z",
        "last_interaction": "2025-09-30T15:45:00Z"
    }

    return mock_stats


@router.post("/{mentor_id}/feedback")
async def submit_mentor_feedback(
    mentor_id: str,
    interaction_id: str,
    helpfulness: int,  # 1-5 점수
    comment: Optional[str] = None,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    mentor_service = Depends(get_mentor_service)
):
    """멘토 상호작용에 대한 피드백 제출"""
    # TODO: 피드백 시스템 구현
    # 현재는 모의 응답

    return {
        "feedback_submitted": True,
        "interaction_id": interaction_id,
        "mentor_id": mentor_id,
        "helpfulness_score": helpfulness,
        "message": "피드백이 성공적으로 제출되었습니다"
    }