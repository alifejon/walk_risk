"""Tutorial Service - 튜토리얼 시스템 서비스"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseService
from ..tutorials.tutorial_manager import TutorialManager, TutorialStage, TutorialProgress
from ..tutorials.puzzle_tutorial import PuzzleTutorial, PuzzleTutorialProgress
from ..core.game_state.game_manager import GameManager


class TutorialService(BaseService):
    """튜토리얼 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        self.tutorial_manager = TutorialManager(game_manager)
        self.puzzle_tutorial = PuzzleTutorial(self.tutorial_manager, game_manager)

        # 플레이어별 튜토리얼 진행 상황
        self.player_progress: Dict[str, Dict[str, Any]] = {}

    async def _setup(self):
        """서비스 초기화"""
        self.logger.info("TutorialService setup completed")

    async def get_tutorial_progress(self, player_id: str) -> Dict[str, Any]:
        """튜토리얼 진행 상황 조회"""
        try:
            self._validate_initialized()

            # 플레이어 진행 상황 초기화
            if player_id not in self.player_progress:
                self.player_progress[player_id] = {
                    "current_stage": TutorialStage.WELCOME.value,
                    "completed_stages": [],
                    "completion_rate": 0.0,
                    "stage_data": {
                        "mentor": "buffett",
                        "puzzles_completed": 0,
                        "skills_learned": []
                    },
                    "puzzle_tutorial_progress": {
                        "has_seen_intro": False,
                        "first_puzzle_completed": False,
                        "investigation_skills_learned": False,
                        "hypothesis_skills_learned": False,
                        "validation_experience_gained": False
                    }
                }

            progress = self.player_progress[player_id]

            # 사용 가능한 다음 단계들 계산
            available_stages = self._get_available_stages(progress["completed_stages"])

            return self._create_response(
                success=True,
                data={
                    "current_stage": progress["current_stage"],
                    "completion_rate": progress["completion_rate"],
                    "completed_stages": progress["completed_stages"],
                    "available_stages": available_stages,
                    "stage_data": progress["stage_data"],
                    "puzzle_tutorial_progress": progress["puzzle_tutorial_progress"]
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_tutorial_progress")

    async def start_tutorial(
        self,
        player_id: str,
        tutorial_type: str = "integrated"
    ) -> Dict[str, Any]:
        """튜토리얼 시작"""
        try:
            self._validate_initialized()

            # 플레이어 진행 상황 초기화
            if player_id not in self.player_progress:
                self.player_progress[player_id] = {
                    "current_stage": TutorialStage.WELCOME.value,
                    "completed_stages": [],
                    "completion_rate": 0.0,
                    "stage_data": {
                        "mentor": "buffett",
                        "puzzles_completed": 0,
                        "skills_learned": [],
                        "start_time": datetime.now().isoformat()
                    },
                    "puzzle_tutorial_progress": {
                        "has_seen_intro": False,
                        "first_puzzle_completed": False,
                        "investigation_skills_learned": False,
                        "hypothesis_skills_learned": False,
                        "validation_experience_gained": False
                    }
                }

            # 첫 번째 환영 메시지 생성
            welcome_message = self._generate_welcome_message(tutorial_type)

            return self._create_response(
                success=True,
                data={
                    "tutorial_started": True,
                    "tutorial_type": tutorial_type,
                    "current_stage": TutorialStage.WELCOME.value,
                    "welcome_message": welcome_message,
                    "next_actions": [
                        "멘토 선택하기",
                        "퍼즐 컨셉 학습하기"
                    ]
                },
                message="Tutorial started successfully"
            )

        except Exception as e:
            return self._handle_error(e, "start_tutorial")

    async def complete_tutorial_stage(
        self,
        player_id: str,
        stage: str,
        stage_results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """튜토리얼 단계 완료"""
        try:
            self._validate_initialized()

            if player_id not in self.player_progress:
                return self._create_response(
                    success=False,
                    message="Tutorial not started",
                    error_code="TUTORIAL_NOT_STARTED"
                )

            progress = self.player_progress[player_id]

            # 단계 검증
            try:
                stage_enum = TutorialStage(stage)
            except ValueError:
                return self._create_response(
                    success=False,
                    message="Invalid tutorial stage",
                    error_code="INVALID_STAGE"
                )

            # 이미 완료된 단계인지 확인
            if stage in progress["completed_stages"]:
                return self._create_response(
                    success=False,
                    message="Stage already completed",
                    error_code="STAGE_ALREADY_COMPLETED"
                )

            # 단계 완료 처리
            progress["completed_stages"].append(stage)
            progress["completion_rate"] = len(progress["completed_stages"]) / len(TutorialStage) * 100

            # 다음 단계 계산
            next_stage = self._get_next_stage(stage_enum)
            if next_stage:
                progress["current_stage"] = next_stage.value

            # 보상 계산
            rewards = self._calculate_stage_rewards(stage_enum, stage_results)

            # 스킬 학습 기록
            if rewards.get("skills_unlocked"):
                progress["stage_data"]["skills_learned"].extend(rewards["skills_unlocked"])

            # 멘토 메시지 생성
            mentor_message = self._generate_completion_message(stage_enum, progress["stage_data"]["mentor"])

            return self._create_response(
                success=True,
                data={
                    "stage_completed": stage,
                    "next_stage": next_stage.value if next_stage else None,
                    "completion_rate": progress["completion_rate"],
                    "rewards": rewards,
                    "mentor_message": mentor_message
                }
            )

        except Exception as e:
            return self._handle_error(e, "complete_tutorial_stage")

    async def start_puzzle_tutorial(self, player_id: str) -> Dict[str, Any]:
        """퍼즐 튜토리얼 시작"""
        try:
            self._validate_initialized()

            if player_id not in self.player_progress:
                # 기본 튜토리얼부터 시작하도록 안내
                return self._create_response(
                    success=False,
                    message="Please start basic tutorial first",
                    error_code="BASIC_TUTORIAL_REQUIRED"
                )

            progress = self.player_progress[player_id]

            # 퍼즐 튜토리얼 진행 상황 업데이트
            if not progress["puzzle_tutorial_progress"]["has_seen_intro"]:
                progress["puzzle_tutorial_progress"]["has_seen_intro"] = True

                # 퍼즐 컨셉 소개 메시지
                intro_message = self._generate_puzzle_intro()

                return self._create_response(
                    success=True,
                    data={
                        "puzzle_tutorial_started": True,
                        "intro_message": intro_message,
                        "next_action": "첫 번째 미스터리 해결하기"
                    }
                )

        except Exception as e:
            return self._handle_error(e, "start_puzzle_tutorial")

    async def complete_puzzle_tutorial_step(
        self,
        player_id: str,
        step: str,
        results: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """퍼즐 튜토리얼 단계별 완료"""
        try:
            self._validate_initialized()

            if player_id not in self.player_progress:
                return self._create_response(
                    success=False,
                    message="Tutorial not found",
                    error_code="TUTORIAL_NOT_FOUND"
                )

            progress = self.player_progress[player_id]
            puzzle_progress = progress["puzzle_tutorial_progress"]

            # 단계별 처리
            if step == "first_puzzle":
                puzzle_progress["first_puzzle_completed"] = True
                progress["stage_data"]["puzzles_completed"] += 1
                reward_xp = 200

            elif step == "investigation_skills":
                puzzle_progress["investigation_skills_learned"] = True
                reward_xp = 100

            elif step == "hypothesis_skills":
                puzzle_progress["hypothesis_skills_learned"] = True
                reward_xp = 150

            elif step == "validation_experience":
                puzzle_progress["validation_experience_gained"] = True
                reward_xp = 100

            else:
                return self._create_response(
                    success=False,
                    message="Invalid puzzle tutorial step",
                    error_code="INVALID_STEP"
                )

            # 전체 퍼즐 튜토리얼 완료 확인
            all_steps_completed = all([
                puzzle_progress["first_puzzle_completed"],
                puzzle_progress["investigation_skills_learned"],
                puzzle_progress["hypothesis_skills_learned"],
                puzzle_progress["validation_experience_gained"]
            ])

            return self._create_response(
                success=True,
                data={
                    "step_completed": step,
                    "xp_gained": reward_xp,
                    "puzzle_tutorial_completed": all_steps_completed,
                    "next_recommendation": self._get_next_puzzle_recommendation(puzzle_progress)
                }
            )

        except Exception as e:
            return self._handle_error(e, "complete_puzzle_tutorial_step")

    def _get_available_stages(self, completed_stages: List[str]) -> List[str]:
        """완료된 단계를 기반으로 사용 가능한 다음 단계들 반환"""
        all_stages = [stage.value for stage in TutorialStage]
        available = []

        for stage in all_stages:
            if stage not in completed_stages:
                # 순차적 진행 체크
                stage_enum = TutorialStage(stage)
                if self._is_stage_accessible(stage_enum, completed_stages):
                    available.append(stage)

        return available

    def _is_stage_accessible(self, stage: TutorialStage, completed_stages: List[str]) -> bool:
        """단계 접근 가능 여부 확인"""
        stage_order = {
            TutorialStage.WELCOME: [],
            TutorialStage.MENTOR_SELECTION: [TutorialStage.WELCOME.value],
            TutorialStage.FIRST_RISK: [TutorialStage.MENTOR_SELECTION.value],
            TutorialStage.PORTFOLIO_BASICS: [TutorialStage.FIRST_RISK.value],
            TutorialStage.MARKET_SIMULATION: [TutorialStage.PORTFOLIO_BASICS.value],
            TutorialStage.GRADUATION: [TutorialStage.MARKET_SIMULATION.value]
        }

        required_stages = stage_order.get(stage, [])
        return all(req_stage in completed_stages for req_stage in required_stages)

    def _get_next_stage(self, current_stage: TutorialStage) -> Optional[TutorialStage]:
        """다음 단계 반환"""
        stage_sequence = [
            TutorialStage.WELCOME,
            TutorialStage.MENTOR_SELECTION,
            TutorialStage.FIRST_RISK,
            TutorialStage.PORTFOLIO_BASICS,
            TutorialStage.MARKET_SIMULATION,
            TutorialStage.GRADUATION
        ]

        try:
            current_index = stage_sequence.index(current_stage)
            if current_index < len(stage_sequence) - 1:
                return stage_sequence[current_index + 1]
        except ValueError:
            pass

        return None

    def _calculate_stage_rewards(
        self,
        stage: TutorialStage,
        results: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """단계별 보상 계산"""
        base_rewards = {
            TutorialStage.WELCOME: {"xp_gained": 50, "features_unlocked": ["mentor_system"]},
            TutorialStage.MENTOR_SELECTION: {"xp_gained": 75, "features_unlocked": ["puzzle_system"]},
            TutorialStage.FIRST_RISK: {"xp_gained": 150, "skills_unlocked": ["basic_investigation"]},
            TutorialStage.PORTFOLIO_BASICS: {"xp_gained": 100, "features_unlocked": ["portfolio_tracking"]},
            TutorialStage.MARKET_SIMULATION: {"xp_gained": 200, "skills_unlocked": ["market_analysis"]},
            TutorialStage.GRADUATION: {"xp_gained": 300, "features_unlocked": ["advanced_puzzles"]}
        }

        rewards = base_rewards.get(stage, {"xp_gained": 50})

        # 결과에 따른 보너스
        if results:
            success_rate = results.get("success_rate", 0.5)
            if success_rate > 0.8:
                rewards["xp_gained"] = int(rewards["xp_gained"] * 1.5)
                rewards["bonus_reason"] = "Excellent performance"

        return rewards

    def _generate_welcome_message(self, tutorial_type: str) -> str:
        """환영 메시지 생성"""
        if tutorial_type == "integrated":
            return """
🎯 **Walk Risk: 투자 학습 게임에 오신 것을 환영합니다!**

여기서는 실제 시장 상황을 바탕으로 한 미스터리를 해결하며
투자 실력을 키워나갈 수 있습니다.

📚 **학습 과정:**
1. 멘토 선택 - 당신만의 투자 가이드
2. 퍼즐 해결 - 시장 미스터리 조사
3. 포트폴리오 관리 - 실전 투자 시뮬레이션
4. 졸업 - 실제 투자 준비 완료

시작할 준비가 되셨나요? 🚀
            """
        else:
            return "Walk Risk 튜토리얼에 오신 것을 환영합니다!"

    def _generate_puzzle_intro(self) -> str:
        """퍼즐 컨셉 소개 메시지"""
        return """
🔍 **투자는 탐정 게임입니다!**

시장에서 일어나는 모든 변화에는 이유가 있습니다.
우리의 목표는 그 이유를 찾아내는 것입니다.

**퍼즐 해결 과정:**
1. 📰 **단서 수집** - 뉴스, 재무제표, 기술적 지표 조사
2. 🤔 **가설 수립** - 수집한 정보를 바탕으로 가설 생성
3. ✅ **검증** - 가설이 맞는지 확인하고 배우기

실패해도 괜찮습니다. 실패는 최고의 선생님이니까요!
        """

    def _generate_completion_message(self, stage: TutorialStage, mentor: str) -> str:
        """단계 완료 메시지 생성"""
        messages = {
            TutorialStage.WELCOME: f"🎉 환영합니다! {mentor} 멘토와 함께 투자 여정을 시작해보세요.",
            TutorialStage.MENTOR_SELECTION: f"✨ 멘토 선택 완료! 이제 첫 번째 도전에 나서보세요.",
            TutorialStage.FIRST_RISK: f"🏆 첫 번째 리스크 정복! 투자자로서 한 걸음 더 나아갔습니다.",
            TutorialStage.PORTFOLIO_BASICS: f"📊 포트폴리오 기초 완료! 이제 실전 준비가 되었습니다.",
            TutorialStage.MARKET_SIMULATION: f"🎯 시장 시뮬레이션 성공! 거의 전문가 수준입니다.",
            TutorialStage.GRADUATION: f"🎓 축하합니다! Walk Risk 튜토리얼을 완주하셨습니다!"
        }

        return messages.get(stage, "단계 완료!")

    def _get_next_puzzle_recommendation(self, puzzle_progress: Dict[str, bool]) -> str:
        """다음 퍼즐 추천"""
        if not puzzle_progress["first_puzzle_completed"]:
            return "첫 번째 퍼즐 도전하기"
        elif not puzzle_progress["investigation_skills_learned"]:
            return "조사 기법 연습하기"
        elif not puzzle_progress["hypothesis_skills_learned"]:
            return "가설 수립 연습하기"
        elif not puzzle_progress["validation_experience_gained"]:
            return "검증 과정 체험하기"
        else:
            return "중급 퍼즐에 도전해보세요!"