"""Puzzle Service - 퍼즐 시스템 서비스"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import random

from .base import BaseService
from ..core.risk_puzzle.puzzle_engine import PuzzleEngine, RiskPuzzle, PuzzleDifficulty, PuzzleType
from ..core.risk_puzzle.investigation import InvestigationEngine, Clue, ClueType
from ..core.risk_puzzle.hypothesis import HypothesisEngine, Hypothesis, HypothesisType, ActionType


class PuzzleService(BaseService):
    """퍼즐 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        super().__init__()
        self.puzzle_engine = PuzzleEngine()
        self.investigation_engine = InvestigationEngine()
        self.hypothesis_engine = HypothesisEngine()

        # 활성 퍼즐들
        self.active_puzzles: Dict[str, RiskPuzzle] = {}

        # 플레이어별 퍼즐 진행 상황
        self.player_progress: Dict[str, Dict[str, Any]] = {}

    async def _setup(self):
        """서비스 초기화"""
        # 샘플 퍼즐들 생성
        await self._create_sample_puzzles()
        self.logger.info("PuzzleService setup completed")

    async def _create_sample_puzzles(self):
        """샘플 퍼즐들 생성"""
        # 초보자용 퍼즐
        beginner_puzzle = RiskPuzzle(
            puzzle_id=str(uuid.uuid4()),
            title="삼성전자 -6.2% 미스터리",
            description="삼성전자가 갑자기 6.2% 하락했습니다. 무엇이 원인일까요?",
            puzzle_type=PuzzleType.PRICE_DROP,
            difficulty=PuzzleDifficulty.BEGINNER,
            target_symbol="005930.KS",
            event_data={
                "price_change": -6.2,
                "volume": 15000000,
                "date": "2025-09-30",
                "market_context": "코스피 -1.2%"
            },
            hidden_truth="반도체 수요 회복 신호",
            correct_hypothesis="일시적 과매도"
        )

        # 단서들 추가
        beginner_puzzle.available_clues = [
            Clue(
                clue_id=str(uuid.uuid4()),
                source="news",
                clue_type=ClueType.NEWS,
                title="뉴스 조사",
                description="최신 뉴스를 확인해보세요",
                content="삼성전자가 새로운 반도체 투자 계획을 발표했습니다...",
                reliability=0.85,
                relevance_score=0.85,
                cost=0,
                cost_energy=0,
                cost_time=5
            ),
            Clue(
                clue_id=str(uuid.uuid4()),
                source="financials",
                clue_type=ClueType.FINANCIAL,
                title="재무 분석",
                description="재무 지표를 분석해보세요",
                content="매출과 영업이익이 전년 대비 증가 추세입니다...",
                reliability=0.70,
                relevance_score=0.70,
                cost=2,
                cost_energy=2,
                cost_time=10
            )
        ]

        self.active_puzzles[beginner_puzzle.puzzle_id] = beginner_puzzle

    async def get_available_puzzles(
        self,
        player_id: str,
        difficulty: Optional[str] = None,
        puzzle_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """사용 가능한 퍼즐 목록 조회"""
        try:
            self._validate_initialized()

            puzzles = list(self.active_puzzles.values())

            # 필터링
            if difficulty:
                puzzles = [p for p in puzzles if p.difficulty.value == difficulty]

            if puzzle_type:
                puzzles = [p for p in puzzles if p.puzzle_type.value == puzzle_type]

            # 페이지네이션
            total = len(puzzles)
            puzzles = puzzles[offset:offset + limit]

            # 플레이어 진행 상황 확인
            player_progress = self.player_progress.get(player_id, {})

            puzzle_list = []
            for puzzle in puzzles:
                puzzle_progress = player_progress.get(puzzle.puzzle_id, {})

                puzzle_list.append({
                    "puzzle_id": puzzle.puzzle_id,
                    "title": puzzle.title,
                    "description": puzzle.description,
                    "difficulty": puzzle.difficulty.value,
                    "type": puzzle.puzzle_type.value,
                    "target_symbol": puzzle.target_symbol,
                    "estimated_time": 15,  # 추정 소요 시간 (분)
                    "reward_xp": puzzle.base_reward_xp,
                    "is_solved": puzzle_progress.get("is_solved", False),
                    "created_at": "2025-09-30T09:00:00Z"  # TODO: 실제 생성 시간
                })

            return self._create_response(
                success=True,
                data={
                    "puzzles": puzzle_list,
                    "total": total,
                    "has_more": offset + len(puzzles) < total
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_available_puzzles")

    async def get_puzzle_details(
        self,
        puzzle_id: str,
        player_id: str
    ) -> Dict[str, Any]:
        """특정 퍼즐 상세 조회"""
        try:
            self._validate_initialized()

            if puzzle_id not in self.active_puzzles:
                return self._create_response(
                    success=False,
                    message="Puzzle not found",
                    error_code="PUZZLE_NOT_FOUND"
                )

            puzzle = self.active_puzzles[puzzle_id]
            player_progress = self.player_progress.get(player_id, {}).get(puzzle_id, {})

            # 사용 가능한 단서들
            available_clues = []
            for clue in puzzle.available_clues:
                available_clues.append({
                    "clue_id": clue.clue_id,
                    "source": clue.source,
                    "title": clue.title,
                    "description": clue.description,
                    "cost": clue.cost,
                    "is_discovered": clue.clue_id in player_progress.get("discovered_clues", [])
                })

            # 발견된 단서들
            discovered_clues = []
            for clue in puzzle.discovered_clues:
                if clue.clue_id in player_progress.get("discovered_clues", []):
                    discovered_clues.append({
                        "clue_id": clue.clue_id,
                        "source": clue.source,
                        "content": clue.content,
                        "relevance_score": clue.relevance_score,
                        "discovery_time": player_progress.get("clue_discovery_times", {}).get(clue.clue_id)
                    })

            return self._create_response(
                success=True,
                data={
                    "puzzle_id": puzzle.puzzle_id,
                    "title": puzzle.title,
                    "description": puzzle.description,
                    "difficulty": puzzle.difficulty.value,
                    "type": puzzle.puzzle_type.value,
                    "target_symbol": puzzle.target_symbol,
                    "event_data": puzzle.event_data,
                    "available_clues": available_clues,
                    "discovered_clues": discovered_clues,
                    "player_progress": {
                        "investigation_count": player_progress.get("investigation_count", 0),
                        "hypothesis_submitted": player_progress.get("hypothesis_submitted", False),
                        "start_time": player_progress.get("start_time"),
                        "is_solved": player_progress.get("is_solved", False)
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_puzzle_details")

    async def investigate_clue(
        self,
        puzzle_id: str,
        player_id: str,
        clue_id: str,
        investigation_type: str
    ) -> Dict[str, Any]:
        """단서 조사 실행"""
        try:
            self._validate_initialized()

            if puzzle_id not in self.active_puzzles:
                return self._create_response(
                    success=False,
                    message="Puzzle not found",
                    error_code="PUZZLE_NOT_FOUND"
                )

            puzzle = self.active_puzzles[puzzle_id]

            # 단서 찾기
            clue = None
            for c in puzzle.available_clues:
                if c.clue_id == clue_id:
                    clue = c
                    break

            if not clue:
                return self._create_response(
                    success=False,
                    message="Clue not found",
                    error_code="CLUE_NOT_FOUND"
                )

            # 플레이어 진행 상황 초기화
            if player_id not in self.player_progress:
                self.player_progress[player_id] = {}

            if puzzle_id not in self.player_progress[player_id]:
                self.player_progress[player_id][puzzle_id] = {
                    "start_time": datetime.now().isoformat(),
                    "investigation_count": 0,
                    "discovered_clues": [],
                    "clue_discovery_times": {},
                    "hypothesis_submitted": False,
                    "is_solved": False
                }

            progress = self.player_progress[player_id][puzzle_id]

            # 이미 발견한 단서인지 확인
            if clue_id in progress["discovered_clues"]:
                return self._create_response(
                    success=False,
                    message="Clue already discovered",
                    error_code="CLUE_ALREADY_DISCOVERED"
                )

            # 조사 실행
            investigation_result = await self.investigation_engine.investigate(
                puzzle, clue, investigation_type
            )

            # 단서 발견 처리
            progress["discovered_clues"].append(clue_id)
            progress["clue_discovery_times"][clue_id] = datetime.now().isoformat()
            progress["investigation_count"] += 1

            # 발견된 단서를 퍼즐에 추가
            puzzle.discovered_clues.append(clue)

            return self._create_response(
                success=True,
                data={
                    "clue": {
                        "clue_id": clue.clue_id,
                        "source": clue.source,
                        "content": clue.content,
                        "relevance_score": clue.relevance_score,
                        "discovery_time": progress["clue_discovery_times"][clue_id]
                    },
                    "investigation_result": {
                        "new_insights": investigation_result.get("insights", []),
                        "energy_consumed": clue.cost,
                        "remaining_energy": 90  # TODO: 실제 에너지 시스템 연동
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "investigate_clue")

    async def submit_hypothesis(
        self,
        puzzle_id: str,
        player_id: str,
        hypothesis_text: str,
        confidence: int,
        evidence: List[str],
        predicted_outcome: str
    ) -> Dict[str, Any]:
        """가설 제출"""
        try:
            self._validate_initialized()

            if puzzle_id not in self.active_puzzles:
                return self._create_response(
                    success=False,
                    message="Puzzle not found",
                    error_code="PUZZLE_NOT_FOUND"
                )

            puzzle = self.active_puzzles[puzzle_id]
            progress = self.player_progress.get(player_id, {}).get(puzzle_id, {})

            if not progress:
                return self._create_response(
                    success=False,
                    message="Player has not started this puzzle",
                    error_code="PUZZLE_NOT_STARTED"
                )

            # 가설 객체 생성
            confidence_value = confidence
            if confidence_value > 1:
                confidence_value = max(0, min(confidence_value, 100)) / 100
            else:
                confidence_value = max(0.0, min(1.0, confidence_value))

            hypothesis_type = self._infer_hypothesis_type(
                hypothesis_text,
                predicted_outcome
            )

            recommended_action = {
                HypothesisType.BULLISH: ActionType.BUY,
                HypothesisType.BEARISH: ActionType.SELL,
                HypothesisType.CONTRARIAN: ActionType.SHORT,
            }.get(hypothesis_type, ActionType.HOLD)

            hypothesis = Hypothesis(
                hypothesis_id=str(uuid.uuid4()),
                puzzle_id=puzzle_id,
                statement=hypothesis_text,
                supporting_clues=evidence,
                confidence_level=confidence_value,
                predicted_outcome=predicted_outcome,
                hypothesis_type=hypothesis_type,
                recommended_action=recommended_action,
                player_id=player_id
            )

            # 가설 검증
            validation_result = await self.hypothesis_engine.validate_hypothesis(
                hypothesis, puzzle, puzzle.discovered_clues
            )

            # 진행 상황 업데이트
            progress["hypothesis_submitted"] = True
            progress["is_solved"] = validation_result.is_correct

            # 점수 계산
            accuracy_score = validation_result.accuracy_score
            base_xp = puzzle.base_reward_xp

            # 시간 보너스 계산
            start_time = datetime.fromisoformat(progress["start_time"])
            completion_time = datetime.now()
            time_taken = (completion_time - start_time).total_seconds() / 60  # 분 단위

            time_bonus = 0
            if time_taken < 10:  # 10분 내 완료
                time_bonus = int(base_xp * 0.5)
            elif time_taken < 20:  # 20분 내 완료
                time_bonus = int(base_xp * 0.2)

            total_xp = base_xp + time_bonus

            # 스킬 해제 결정
            skills_unlocked = []
            if validation_result.is_correct:
                if puzzle.difficulty == PuzzleDifficulty.BEGINNER:
                    skills_unlocked.append("market_analysis_basic")

            return self._create_response(
                success=True,
                data={
                    "hypothesis_id": hypothesis.hypothesis_id,
                    "validation_result": {
                        "accuracy_score": accuracy_score,
                        "correct_aspects": validation_result.correct_aspects,
                        "missed_aspects": validation_result.missed_aspects,
                        "mentor_feedback": validation_result.feedback,
                        "is_correct": validation_result.is_correct
                    },
                    "rewards": {
                        "xp_gained": total_xp,
                        "time_bonus": time_bonus,
                        "skills_unlocked": skills_unlocked,
                        "achievements": ["puzzle_solver"] if validation_result.is_correct else []
                    }
                }
            )

        except Exception as e:
            return self._handle_error(e, "submit_hypothesis")

    def _infer_hypothesis_type(
        self,
        hypothesis_text: str,
        predicted_outcome: str
    ) -> HypothesisType:
        """텍스트에서 가설 타입 추론"""
        combined = f"{hypothesis_text} {predicted_outcome}".lower()

        bearish_keywords = ["하락", "하락", "sell", "매도", "bear", "감소", " 떨어"]
        bullish_keywords = ["상승", "증가", "buy", "매수", "rise", "bull", "오르"]
        contrarian_keywords = ["역발상", "contrarian", "short"]

        if any(keyword in combined for keyword in bearish_keywords):
            return HypothesisType.BEARISH
        if any(keyword in combined for keyword in bullish_keywords):
            return HypothesisType.BULLISH
        if any(keyword in combined for keyword in contrarian_keywords):
            return HypothesisType.CONTRARIAN
        return HypothesisType.NEUTRAL

    async def create_daily_puzzles(self) -> Dict[str, Any]:
        """일일 퍼즐 생성 (실시간 시장 데이터 기반)"""
        try:
            self._validate_initialized()

            # TODO: 실제 시장 데이터를 기반으로 퍼즐 생성
            # 현재는 샘플 퍼즐 생성

            new_puzzles = await self.puzzle_engine.generate_daily_puzzles()

            for puzzle in new_puzzles:
                self.active_puzzles[puzzle.puzzle_id] = puzzle

            return self._create_response(
                success=True,
                data={
                    "created_puzzles": len(new_puzzles),
                    "puzzle_ids": [p.puzzle_id for p in new_puzzles]
                },
                message="Daily puzzles created"
            )

        except Exception as e:
            return self._handle_error(e, "create_daily_puzzles")
