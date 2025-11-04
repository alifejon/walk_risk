"""플레이어 관련 API 엔드포인트"""

from datetime import datetime
from typing import Annotated, Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ...auth.dependencies import get_current_user
from ...database.connection import get_db
from ...database.models import User

router = APIRouter()


class PlayerUpdateRequest(BaseModel):
    preferred_mentor: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class PlayerResponse(BaseModel):
    id: str
    username: str
    email: str
    level: int
    experience: int
    current_class: str
    energy: int
    max_energy: int
    unlocked_skills: List[str]
    unlocked_features: List[str]
    preferred_mentor: str
    settings: Dict[str, Any]
    created_at: str
    last_active: Optional[str]


@router.get("/me", response_model=PlayerResponse)
async def get_current_player(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """현재 사용자 정보 조회"""
    return PlayerResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        level=current_user.level,
        experience=current_user.experience,
        current_class=current_user.current_class,
        energy=current_user.energy,
        max_energy=current_user.max_energy,
        unlocked_skills=current_user.unlocked_skills,
        unlocked_features=current_user.unlocked_features,
        preferred_mentor=current_user.preferred_mentor,
        settings=current_user.settings,
        created_at=current_user.created_at.isoformat(),
        last_active=current_user.last_active.isoformat() if current_user.last_active else None
    )


@router.put("/me")
async def update_current_player(
    request: PlayerUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """현재 사용자 정보 업데이트"""
    try:
        updates = request.dict(exclude_unset=True)

        for key, value in updates.items():
            if hasattr(current_user, key):
                setattr(current_user, key, value)

        await db.commit()
        await db.refresh(current_user)

        return {
            "message": "Player updated successfully",
            "player": PlayerResponse(
                id=current_user.id,
                username=current_user.username,
                email=current_user.email,
                level=current_user.level,
                experience=current_user.experience,
                current_class=current_user.current_class,
                energy=current_user.energy,
                max_energy=current_user.max_energy,
                unlocked_skills=current_user.unlocked_skills,
                unlocked_features=current_user.unlocked_features,
                preferred_mentor=current_user.preferred_mentor,
                settings=current_user.settings,
                created_at=current_user.created_at.isoformat(),
                last_active=current_user.last_active.isoformat() if current_user.last_active else None
            )
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


class EnergyRequest(BaseModel):
    amount: int


@router.post("/me/energy/consume")
async def consume_energy(
    request: EnergyRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """에너지 소모"""
    if current_user.energy < request.amount:
        raise HTTPException(status_code=400, detail="에너지가 부족합니다")

    current_user.energy -= request.amount
    await db.commit()

    return {
        "energy": current_user.energy,
        "max_energy": current_user.max_energy
    }


@router.post("/me/energy/restore")
async def restore_energy(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Optional[EnergyRequest] = None
):
    """에너지 회복"""
    if request and request.amount:
        current_user.energy = min(current_user.energy + request.amount, current_user.max_energy)
    else:
        current_user.energy = current_user.max_energy

    await db.commit()

    return {
        "energy": current_user.energy,
        "max_energy": current_user.max_energy
    }


class ProgressRequest(BaseModel):
    experience_gained: int = 0
    skills_unlocked: Optional[List[str]] = None
    features_unlocked: Optional[List[str]] = None


@router.post("/me/progress")
async def update_player_progress(
    request: ProgressRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """플레이어 진행도 업데이트"""
    # 경험치 추가
    current_user.experience += request.experience_gained

    # 레벨업 체크
    while current_user.experience >= current_user.level * 100:
        current_user.experience -= current_user.level * 100
        current_user.level += 1

        # 레벨에 따른 클래스 업데이트
        if current_user.level >= 25:
            current_user.current_class = "Risk Transcender"
        elif current_user.level >= 15:
            current_user.current_class = "Risk Master"
        elif current_user.level >= 5:
            current_user.current_class = "Risk Walker"

    # 스킬 언락
    if request.skills_unlocked:
        for skill in request.skills_unlocked:
            if skill not in current_user.unlocked_skills:
                current_user.unlocked_skills.append(skill)

    # 기능 언락
    if request.features_unlocked:
        for feature in request.features_unlocked:
            if feature not in current_user.unlocked_features:
                current_user.unlocked_features.append(feature)

    await db.commit()
    await db.refresh(current_user)

    return {
        "level": current_user.level,
        "experience": current_user.experience,
        "current_class": current_user.current_class,
        "unlocked_skills": current_user.unlocked_skills,
        "unlocked_features": current_user.unlocked_features
    }


@router.get("/stats")
async def get_player_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """플레이어 통계 조회"""
    from sqlalchemy import select, func
    from ...database.models import PuzzleProgress, Portfolio

    # 퍼즐 통계
    puzzle_stmt = select(
        func.count(PuzzleProgress.id).label("total_attempts"),
        func.sum(func.cast(PuzzleProgress.is_solved, Integer)).label("solved")
    ).where(PuzzleProgress.user_id == current_user.id)

    puzzle_result = await db.execute(puzzle_stmt)
    puzzle_stats = puzzle_result.first()

    # 포트폴리오 통계
    portfolio_stmt = select(Portfolio).where(Portfolio.user_id == current_user.id)
    portfolio_result = await db.execute(portfolio_stmt)
    portfolios = portfolio_result.scalars().all()

    total_value = sum(p.total_value for p in portfolios)

    return {
        "player_info": {
            "level": current_user.level,
            "experience": current_user.experience,
            "current_class": current_user.current_class
        },
        "puzzle_stats": {
            "total_attempts": puzzle_stats.total_attempts or 0 if puzzle_stats else 0,
            "solved": puzzle_stats.solved or 0 if puzzle_stats else 0,
            "success_rate": (puzzle_stats.solved / puzzle_stats.total_attempts * 100) if puzzle_stats and puzzle_stats.total_attempts else 0
        },
        "portfolio_stats": {
            "total_portfolios": len(portfolios),
            "total_value": total_value
        }
    }


@router.get("/leaderboard")
async def get_leaderboard(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    period: str = "weekly",
    metric: str = "xp",
    limit: int = 10
):
    """리더보드 조회"""
    from sqlalchemy import select, desc

    # 메트릭에 따라 정렬
    if metric == "xp":
        order_by = desc(User.experience)
    elif metric == "level":
        order_by = desc(User.level)
    else:
        order_by = desc(User.experience)

    stmt = select(User).order_by(order_by).limit(limit)
    result = await db.execute(stmt)
    top_users = result.scalars().all()

    leaderboard = [
        {
            "rank": idx + 1,
            "user_id": user.id,
            "username": user.username,
            "score": user.experience if metric == "xp" else user.level,
            "level": user.level,
            "current_class": user.current_class
        }
        for idx, user in enumerate(top_users)
    ]

    # 현재 사용자 순위 계산
    all_stmt = select(User).order_by(order_by)
    all_result = await db.execute(all_stmt)
    all_users = all_result.scalars().all()

    my_rank = next((idx + 1 for idx, u in enumerate(all_users) if u.id == current_user.id), None)

    return {
        "leaderboard": leaderboard,
        "my_rank": {
            "rank": my_rank,
            "score": current_user.experience if metric == "xp" else current_user.level
        },
        "period": period,
        "metric": metric
    }