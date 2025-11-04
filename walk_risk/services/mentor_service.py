"""Mentor Service - AI 멘토 시스템 서비스"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import BaseService
from ..ai.mentor_personas import BuffettPersona, LynchPersona, GrahamPersona, DalioPersona, WoodPersona


class MentorService(BaseService):
    """AI 멘토 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        super().__init__()

        # 멘토 인스턴스들
        self.mentors = {
            "buffett": BuffettPersona(),
            "lynch": LynchPersona(),
            "graham": GrahamPersona(),
            "dalio": DalioPersona(),
            "wood": WoodPersona()
        }

        # 플레이어별 멘토 상호작용 기록
        self.interaction_history: Dict[str, List[Dict[str, Any]]] = {}

    async def _setup(self):
        """서비스 초기화"""
        self.logger.info("MentorService setup completed")

    async def get_available_mentors(self) -> Dict[str, Any]:
        """사용 가능한 멘토 목록 조회"""
        try:
            self._validate_initialized()

            mentor_list = []
            for mentor_id, mentor in self.mentors.items():
                mentor_info = {
                    "id": mentor_id,
                    "name": mentor.name,
                    "specialty": getattr(mentor, 'specialty', 'Investment Strategy'),
                    "description": getattr(mentor, 'description', f'{mentor.name}의 투자 철학을 따라 배우세요'),
                    "personality_traits": getattr(mentor, 'personality_traits', ['wise', 'experienced']),
                    "is_available": True
                }
                mentor_list.append(mentor_info)

            return self._create_response(
                success=True,
                data={"mentors": mentor_list}
            )

        except Exception as e:
            return self._handle_error(e, "get_available_mentors")

    async def ask_mentor(
        self,
        player_id: str,
        mentor_id: str,
        context: str,
        question: str,
        current_situation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """멘토에게 조언 요청"""
        try:
            self._validate_initialized()

            if mentor_id not in self.mentors:
                return self._create_response(
                    success=False,
                    message="Mentor not found",
                    error_code="MENTOR_NOT_FOUND"
                )

            mentor = self.mentors[mentor_id]

            # 상황에 따른 멘토 응답 생성
            response = await self._generate_mentor_response(
                mentor, context, question, current_situation
            )

            # 상호작용 기록
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "mentor_id": mentor_id,
                "context": context,
                "question": question,
                "response": response,
                "situation": current_situation
            }

            if player_id not in self.interaction_history:
                self.interaction_history[player_id] = []

            self.interaction_history[player_id].append(interaction)

            # 상호작용 수 계산
            mentor_interactions = len([
                i for i in self.interaction_history[player_id]
                if i["mentor_id"] == mentor_id
            ])

            return self._create_response(
                success=True,
                data={
                    "mentor_response": response,
                    "context_updates": {
                        "interaction_count": mentor_interactions,
                        "mentor_relationship": self._get_relationship_level(mentor_interactions)
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "ask_mentor")

    async def _generate_mentor_response(
        self,
        mentor,
        context: str,
        question: str,
        situation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """멘토 응답 생성"""

        # 컨텍스트별 응답 생성
        if context == "puzzle":
            return await self._generate_puzzle_advice(mentor, question, situation)
        elif context == "general":
            return await self._generate_general_advice(mentor, question)
        elif context == "portfolio":
            return await self._generate_portfolio_advice(mentor, question, situation)
        else:
            return await self._generate_general_advice(mentor, question)

    async def _generate_puzzle_advice(
        self,
        mentor,
        question: str,
        situation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """퍼즐 관련 조언 생성"""

        if not situation:
            situation = {}

        discovered_clues = situation.get("discovered_clues", [])
        player_state = situation.get("player_state", "investigating")

        # BuffettPersona의 퍼즐 힌트 기능 활용
        if hasattr(mentor, 'give_puzzle_hint'):
            puzzle_data = situation.get("puzzle_data", {})
            hint_response = mentor.give_puzzle_hint(puzzle_data, discovered_clues, {
                "clue_count": len(discovered_clues),
                "player_state": player_state
            })

            return {
                "message": hint_response,
                "advice_type": "hint",
                "personality_note": f"{mentor.name}의 차분하고 신중한 조언",
                "suggested_actions": self._get_suggested_actions(len(discovered_clues))
            }
        else:
            # 기본 조언
            return {
                "message": f"{mentor.name}: {question}에 대해 신중하게 생각해보세요. 모든 정보를 종합적으로 분석하는 것이 중요합니다.",
                "advice_type": "general",
                "personality_note": f"{mentor.name}의 투자 철학 기반 조언",
                "suggested_actions": ["더 많은 정보 수집", "객관적 분석"]
            }

    async def _generate_general_advice(self, mentor, question: str) -> Dict[str, Any]:
        """일반적인 투자 조언 생성"""

        # 멘토별 특성 반영
        if mentor.name == "Warren Buffett":
            message = "가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것입니다. 장기적 관점에서 기업의 본질적 가치를 파악하는 것이 중요합니다."
        elif mentor.name == "Peter Lynch":
            message = "당신이 이해할 수 있는 회사에 투자하세요. 일상에서 만나는 좋은 제품이나 서비스를 제공하는 회사를 주목해보세요."
        else:
            message = f"{mentor.name}의 투자 철학: 시장을 이해하고 인내심을 가지는 것이 성공의 열쇠입니다."

        return {
            "message": message,
            "advice_type": "philosophy",
            "personality_note": f"{mentor.name}의 핵심 투자 철학",
            "suggested_actions": ["학습 지속", "인내심 유지"]
        }

    async def _generate_portfolio_advice(
        self,
        mentor,
        question: str,
        situation: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """포트폴리오 관련 조언 생성"""

        portfolio_data = situation or {}
        holdings = portfolio_data.get("holdings", [])

        advice = f"현재 {len(holdings)}개 종목을 보유하고 계시네요. "

        if mentor.name == "Warren Buffett":
            advice += "다양화보다는 확신이 서는 소수의 우량 기업에 집중하는 것을 추천합니다."
        elif mentor.name == "Peter Lynch":
            advice += "각 종목에 투자한 이유를 명확히 설명할 수 있어야 합니다."
        else:
            advice += "리스크 관리를 위해 포트폴리오의 균형을 유지하세요."

        return {
            "message": advice,
            "advice_type": "portfolio_analysis",
            "personality_note": f"{mentor.name}의 포트폴리오 관리 철학",
            "suggested_actions": ["포트폴리오 리뷰", "리스크 점검"]
        }

    def _get_suggested_actions(self, clue_count: int) -> List[str]:
        """단서 수에 따른 제안 액션"""
        if clue_count == 0:
            return ["뉴스 조사 시작", "기본 정보 수집"]
        elif clue_count == 1:
            return ["추가 단서 탐색", "다른 관점에서 분석"]
        elif clue_count == 2:
            return ["패턴 분석", "종합적 판단"]
        else:
            return ["가설 수립", "결론 도출"]

    def _get_relationship_level(self, interaction_count: int) -> str:
        """상호작용 수에 따른 관계 레벨"""
        if interaction_count < 3:
            return "초기"
        elif interaction_count < 10:
            return "발전중"
        elif interaction_count < 25:
            return "신뢰"
        else:
            return "멘토십"

    async def get_mentor_interaction_history(
        self,
        player_id: str,
        mentor_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """멘토 상호작용 기록 조회"""
        try:
            self._validate_initialized()

            if player_id not in self.interaction_history:
                return self._create_response(
                    success=True,
                    data={"interactions": [], "total": 0}
                )

            interactions = self.interaction_history[player_id]

            # 특정 멘토로 필터링
            if mentor_id:
                interactions = [i for i in interactions if i["mentor_id"] == mentor_id]

            # 최신순 정렬 및 제한
            interactions = sorted(interactions, key=lambda x: x["timestamp"], reverse=True)
            total = len(interactions)
            interactions = interactions[:limit]

            return self._create_response(
                success=True,
                data={
                    "interactions": interactions,
                    "total": total,
                    "has_more": total > limit
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_mentor_interaction_history")

    async def get_mentor_recommendations(
        self,
        player_id: str,
        player_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """플레이어 프로필 기반 멘토 추천"""
        try:
            self._validate_initialized()

            level = player_profile.get("level", 1)
            experience = player_profile.get("experience", 0)
            current_class = player_profile.get("current_class", "Risk Novice")

            recommendations = []

            # 초보자에게는 Buffett 추천
            if level < 5:
                recommendations.append({
                    "mentor_id": "buffett",
                    "reason": "안정적이고 체계적인 학습에 적합",
                    "compatibility": 95
                })

            # 중급자에게는 Lynch 추천
            if 5 <= level < 15:
                recommendations.append({
                    "mentor_id": "lynch",
                    "reason": "실용적이고 적극적인 투자 학습",
                    "compatibility": 90
                })

            # 고급자에게는 다양한 멘토 추천
            if level >= 15:
                recommendations.extend([
                    {
                        "mentor_id": "graham",
                        "reason": "깊이 있는 분석 기법 학습",
                        "compatibility": 85
                    },
                    {
                        "mentor_id": "dalio",
                        "reason": "거시경제적 관점 개발",
                        "compatibility": 80
                    }
                ])

            return self._create_response(
                success=True,
                data={"recommendations": recommendations}
            )

        except Exception as e:
            return self._handle_error(e, "get_mentor_recommendations")