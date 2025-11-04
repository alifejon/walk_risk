"""Tutorial Manager - 튜토리얼 핵심 관리 시스템"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime

from ..core.game_state.game_manager import GameManager
from ..ai.ai_guide_manager import AIGuideManager
from ..models.player.base import Player
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class TutorialStage(Enum):
    """튜토리얼 진행 단계"""
    WELCOME = "welcome"  # 환영 인사
    MENTOR_SELECTION = "mentor_selection"  # 멘토 선택
    FIRST_RISK = "first_risk"  # 첫 리스크 도전
    PORTFOLIO_BASICS = "portfolio_basics"  # 포트폴리오 기초
    MARKET_SIMULATION = "market_simulation"  # 시장 시뮬레이션
    GRADUATION = "graduation"  # 졸업


@dataclass
class TutorialProgress:
    """튜토리얼 진행 상황"""
    current_stage: TutorialStage = TutorialStage.WELCOME
    completed_stages: List[TutorialStage] = field(default_factory=list)
    stage_data: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    completion_rate: float = 0.0
    
    def complete_stage(self, stage: TutorialStage):
        """스테이지 완료 처리"""
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)
            self.completion_rate = len(self.completed_stages) / len(TutorialStage) * 100
            
    def is_stage_completed(self, stage: TutorialStage) -> bool:
        """스테이지 완료 여부 확인"""
        return stage in self.completed_stages


class TutorialManager:
    """튜토리얼 전체 관리자"""
    
    def __init__(self, game_manager: GameManager):
        self.game_manager = game_manager
        self.ai_guide_manager = AIGuideManager()
        self.progress: Dict[str, TutorialProgress] = {}
        self.active_tutorials: Dict[str, Any] = {}
        
    async def start_tutorial(self, player: Player, tutorial_type: str = "buffett") -> Dict[str, Any]:
        """튜토리얼 시작"""
        try:
            # 플레이어별 진행 상황 초기화
            if player.id not in self.progress:
                self.progress[player.id] = TutorialProgress()
                
            progress = self.progress[player.id]
            
            # 튜토리얼 타입에 따라 적절한 튜토리얼 생성
            if tutorial_type == "buffett":
                from .buffett_tutorial import BuffettTutorial
                tutorial = BuffettTutorial(self, player)
                self.active_tutorials[player.id] = tutorial
                
            # 첫 스테이지 실행
            result = await self._execute_stage(player, progress.current_stage)
            
            logger.info(f"튜토리얼 시작: {player.name} - {tutorial_type}")
            
            return {
                "success": True,
                "stage": progress.current_stage.value,
                "data": result
            }
            
        except Exception as e:
            logger.error(f"튜토리얼 시작 실패: {e}")
            return {"success": False, "error": str(e)}
            
    async def _execute_stage(self, player: Player, stage: TutorialStage) -> Dict[str, Any]:
        """스테이지 실행"""
        tutorial = self.active_tutorials.get(player.id)
        if not tutorial:
            raise ValueError("활성 튜토리얼이 없습니다")
            
        # 스테이지별 실행
        stage_methods = {
            TutorialStage.WELCOME: tutorial.welcome_stage,
            TutorialStage.MENTOR_SELECTION: tutorial.mentor_selection_stage,
            TutorialStage.FIRST_RISK: tutorial.first_risk_stage,
            TutorialStage.PORTFOLIO_BASICS: tutorial.portfolio_basics_stage,
            TutorialStage.MARKET_SIMULATION: tutorial.market_simulation_stage,
            TutorialStage.GRADUATION: tutorial.graduation_stage
        }
        
        method = stage_methods.get(stage)
        if not method:
            raise ValueError(f"알 수 없는 스테이지: {stage}")
            
        return await method()
        
    async def advance_stage(self, player: Player) -> Dict[str, Any]:
        """다음 스테이지로 진행"""
        try:
            progress = self.progress.get(player.id)
            if not progress:
                return {"success": False, "error": "진행 중인 튜토리얼이 없습니다"}
                
            # 현재 스테이지 완료 처리
            progress.complete_stage(progress.current_stage)
            
            # 다음 스테이지 찾기
            stages = list(TutorialStage)
            current_index = stages.index(progress.current_stage)
            
            if current_index < len(stages) - 1:
                progress.current_stage = stages[current_index + 1]
                result = await self._execute_stage(player, progress.current_stage)
                
                return {
                    "success": True,
                    "stage": progress.current_stage.value,
                    "completion_rate": progress.completion_rate,
                    "data": result
                }
            else:
                # 튜토리얼 완료
                return await self.complete_tutorial(player)
                
        except Exception as e:
            logger.error(f"스테이지 진행 실패: {e}")
            return {"success": False, "error": str(e)}
            
    async def complete_tutorial(self, player: Player) -> Dict[str, Any]:
        """튜토리얼 완료 처리"""
        try:
            progress = self.progress.get(player.id)
            if not progress:
                return {"success": False, "error": "진행 중인 튜토리얼이 없습니다"}
                
            # 완료 보상 지급
            rewards = {
                "experience": 1000,
                "title": "투자 입문자",
                "unlock_features": ["real_portfolio", "advanced_risks"],
                "completion_time": (datetime.now() - progress.start_time).total_seconds()
            }
            
            # 게임 매니저에 완료 기록
            await self.game_manager.unlock_features(player.id, rewards["unlock_features"])
            
            # 정리
            del self.active_tutorials[player.id]
            del self.progress[player.id]
            
            logger.info(f"튜토리얼 완료: {player.name}")
            
            return {
                "success": True,
                "completed": True,
                "rewards": rewards
            }
            
        except Exception as e:
            logger.error(f"튜토리얼 완료 처리 실패: {e}")
            return {"success": False, "error": str(e)}
            
    def get_progress(self, player_id: str) -> Optional[TutorialProgress]:
        """플레이어의 튜토리얼 진행 상황 조회"""
        return self.progress.get(player_id)
        
    async def skip_tutorial(self, player: Player) -> Dict[str, Any]:
        """튜토리얼 건너뛰기"""
        try:
            # 기본 보상만 지급
            basic_rewards = {
                "experience": 500,
                "unlock_features": ["real_portfolio"]
            }
            
            await self.game_manager.unlock_features(player.id, basic_rewards["unlock_features"])
            
            # 정리
            if player.id in self.active_tutorials:
                del self.active_tutorials[player.id]
            if player.id in self.progress:
                del self.progress[player.id]
                
            logger.info(f"튜토리얼 건너뛰기: {player.name}")
            
            return {
                "success": True,
                "skipped": True,
                "rewards": basic_rewards
            }
            
        except Exception as e:
            logger.error(f"튜토리얼 건너뛰기 실패: {e}")
            return {"success": False, "error": str(e)}