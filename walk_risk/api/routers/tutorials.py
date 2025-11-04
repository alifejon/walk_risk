"""튜토리얼 관련 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


class CompleteStageRequest(BaseModel):
    stage_results: Optional[Dict[str, Any]] = None


class StartTutorialRequest(BaseModel):
    tutorial_type: str = "integrated"


def get_tutorial_service(request: Request):
    """튜토리얼 서비스 의존성"""
    return request.app.state.services["tutorial"]


@router.get("/progress")
async def get_tutorial_progress(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """튜토리얼 진행 상황 조회"""
    result = await tutorial_service.get_tutorial_progress(player_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/start")
async def start_tutorial(
    request: StartTutorialRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """튜토리얼 시작"""
    result = await tutorial_service.start_tutorial(player_id, request.tutorial_type)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/{stage}/complete")
async def complete_tutorial_stage(
    stage: str,
    request: CompleteStageRequest,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """튜토리얼 단계 완료"""
    result = await tutorial_service.complete_tutorial_stage(
        player_id, stage, request.stage_results
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "TUTORIAL_NOT_STARTED":
            raise HTTPException(status_code=400, detail="튜토리얼을 먼저 시작해주세요")
        elif error_code == "INVALID_STAGE":
            raise HTTPException(status_code=400, detail="잘못된 튜토리얼 단계입니다")
        elif error_code == "STAGE_ALREADY_COMPLETED":
            raise HTTPException(status_code=400, detail="이미 완료된 단계입니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/puzzle/start")
async def start_puzzle_tutorial(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """퍼즐 튜토리얼 시작"""
    result = await tutorial_service.start_puzzle_tutorial(player_id)

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "BASIC_TUTORIAL_REQUIRED":
            raise HTTPException(status_code=400, detail="기본 튜토리얼을 먼저 완료해주세요")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.post("/puzzle/{step}/complete")
async def complete_puzzle_tutorial_step(
    step: str,
    results: Optional[Dict[str, Any]] = None,
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """퍼즐 튜토리얼 단계별 완료"""
    result = await tutorial_service.complete_puzzle_tutorial_step(
        player_id, step, results
    )

    if not result["success"]:
        error_code = result.get("error_code")
        if error_code == "TUTORIAL_NOT_FOUND":
            raise HTTPException(status_code=404, detail="튜토리얼을 찾을 수 없습니다")
        elif error_code == "INVALID_STEP":
            raise HTTPException(status_code=400, detail="잘못된 튜토리얼 단계입니다")
        raise HTTPException(status_code=400, detail=result["message"])

    return result["data"]


@router.get("/stages")
async def get_tutorial_stages():
    """사용 가능한 튜토리얼 단계 목록"""
    stages = [
        {
            "stage": "welcome",
            "name": "환영 인사",
            "description": "Walk Risk에 오신 것을 환영합니다",
            "estimated_time": 2,
            "requirements": []
        },
        {
            "stage": "mentor_selection",
            "name": "멘토 선택",
            "description": "당신만의 투자 가이드를 선택하세요",
            "estimated_time": 5,
            "requirements": ["welcome"]
        },
        {
            "stage": "first_risk",
            "name": "첫 번째 리스크",
            "description": "첫 번째 투자 리스크에 도전해보세요",
            "estimated_time": 15,
            "requirements": ["mentor_selection"]
        },
        {
            "stage": "portfolio_basics",
            "name": "포트폴리오 기초",
            "description": "포트폴리오 관리의 기초를 배워보세요",
            "estimated_time": 10,
            "requirements": ["first_risk"]
        },
        {
            "stage": "market_simulation",
            "name": "시장 시뮬레이션",
            "description": "실제 시장 상황을 시뮬레이션해보세요",
            "estimated_time": 20,
            "requirements": ["portfolio_basics"]
        },
        {
            "stage": "graduation",
            "name": "졸업",
            "description": "튜토리얼을 완주하고 졸업하세요",
            "estimated_time": 5,
            "requirements": ["market_simulation"]
        }
    ]

    return {"stages": stages}


@router.get("/stats")
async def get_tutorial_stats(
    player_id: str = "test_player_123",  # TODO: JWT에서 추출
    tutorial_service = Depends(get_tutorial_service)
):
    """튜토리얼 통계"""
    # TODO: 통계 시스템 구현
    # 현재는 모의 응답

    return {
        "total_time_spent": 45,  # 분
        "stages_completed": 4,
        "total_stages": 6,
        "completion_rate": 66.7,
        "average_stage_time": 11.25,
        "puzzle_tutorial_completed": False,
        "achievements_earned": [
            "first_steps",
            "mentor_bonded",
            "risk_taker"
        ]
    }


@router.get("/help")
async def get_tutorial_help():
    """튜토리얼 도움말"""
    return {
        "faq": [
            {
                "question": "튜토리얼을 건너뛸 수 있나요?",
                "answer": "네, 하지만 기본 개념을 이해하기 위해 완주하는 것을 권장합니다."
            },
            {
                "question": "에너지가 부족하면 어떻게 하나요?",
                "answer": "튜토리얼에서는 에너지가 무제한이므로 걱정하지 마세요."
            },
            {
                "question": "실수했을 때 다시 시작할 수 있나요?",
                "answer": "네, 언제든지 이전 단계로 돌아가거나 처음부터 시작할 수 있습니다."
            }
        ],
        "tips": [
            "멘토의 조언을 자주 들어보세요",
            "서두르지 말고 차근차근 진행하세요",
            "실패해도 괜찮습니다. 학습이 목적입니다"
        ]
    }