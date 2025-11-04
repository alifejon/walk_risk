"""Player Service - 플레이어 관리 서비스"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .base import BaseService
from ..models.player.base import Player
from ..core.game_state.game_manager import GameManager


class PlayerService(BaseService):
    """플레이어 관련 비즈니스 로직을 처리하는 서비스"""

    def __init__(self, game_manager: GameManager):
        super().__init__()
        self.game_manager = game_manager
        self.players: Dict[str, Player] = {}
        self.player_sessions: Dict[str, Dict[str, Any]] = {}

    async def _setup(self):
        """서비스 초기화"""
        self.logger.info("PlayerService setup completed")

    async def create_player(
        self,
        username: str,
        email: str,
        preferred_mentor: str = "buffett"
    ) -> Dict[str, Any]:
        """새로운 플레이어 생성"""
        try:
            self._validate_initialized()

            # 플레이어 ID 생성
            player_id = str(uuid.uuid4())

            # 플레이어 객체 생성
            player = Player(
                id=player_id,
                username=username,
                email=email,
                level=1,
                experience=0,
                current_class="Risk Novice",
                energy=100,
                max_energy=100,
                unlocked_skills=[],
                created_at=datetime.now()
            )

            # 플레이어 저장
            self.players[player_id] = player

            # 게임 매니저에 등록
            await self.game_manager.unlock_features(player_id, ["basic_tutorial"])

            # 플레이어 세션 초기화
            self.player_sessions[player_id] = {
                "created_at": datetime.now(),
                "last_active": datetime.now(),
                "preferred_mentor": preferred_mentor,
                "settings": {
                    "notifications": True,
                    "difficulty": "beginner"
                }
            }

            player.settings = self.player_sessions[player_id]["settings"].copy()

            self.logger.info(f"Player created: {username} ({player_id})")

            return self._create_response(
                success=True,
                data={
                    "player_id": player_id,
                    "username": username,
                    "email": email,
                    "level": player.level,
                    "current_class": player.current_class,
                    "preferred_mentor": preferred_mentor
                },
                message="Player created successfully"
            )

        except Exception as e:
            return self._handle_error(e, "create_player")

    async def get_player(self, player_id: str) -> Dict[str, Any]:
        """플레이어 정보 조회"""
        try:
            self._validate_initialized()

            if player_id not in self.players:
                return self._create_response(
                    success=False,
                    message="Player not found",
                    error_code="PLAYER_NOT_FOUND"
                )

            player = self.players[player_id]
            session = self.player_sessions.get(player_id, {})
            features = self.game_manager.get_player_features(player_id)
            settings = session.get("settings") or player.settings or {}
            player.settings = settings.copy() if isinstance(settings, dict) else {}

            return self._create_response(
                success=True,
                data={
                    "id": player.id,
                    "username": player.username,
                    "email": player.email,
                    "level": player.level,
                    "experience": player.experience,
                    "current_class": player.current_class,
                    "energy": player.energy,
                    "max_energy": player.max_energy,
                    "unlocked_skills": player.unlocked_skills,
                    "unlocked_features": features,
                    "preferred_mentor": session.get("preferred_mentor", "buffett"),
                    "settings": player.settings,
                    "created_at": player.created_at.isoformat(),
                    "last_active": session.get("last_active", datetime.now()).isoformat()
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_player")

    async def update_player(
        self,
        player_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """플레이어 정보 업데이트"""
        try:
            self._validate_initialized()

            if player_id not in self.players:
                return self._create_response(
                    success=False,
                    message="Player not found",
                    error_code="PLAYER_NOT_FOUND"
                )

            player = self.players[player_id]
            session = self.player_sessions[player_id]

            # 허용된 필드만 업데이트
            allowed_fields = ["preferred_mentor", "settings"]
            session_updates = {}

            for field, value in updates.items():
                if field in allowed_fields:
                    session_updates[field] = value

            # 세션 정보 업데이트
            session.update(session_updates)
            session["last_active"] = datetime.now()
            if "settings" in session_updates and isinstance(session_updates["settings"], dict):
                self.players[player_id].settings = session_updates["settings"].copy()
            elif "settings" not in session_updates and "settings" in session:
                self.players[player_id].settings = session["settings"].copy() if isinstance(session["settings"], dict) else {}

            self.logger.info(f"Player updated: {player_id}")

            return self._create_response(
                success=True,
                data=session_updates,
                message="Player updated successfully"
            )

        except Exception as e:
            return self._handle_error(e, "update_player")

    async def update_player_progress(
        self,
        player_id: str,
        experience_gained: int = 0,
        skills_unlocked: List[str] = None,
        features_unlocked: List[str] = None
    ) -> Dict[str, Any]:
        """플레이어 진행도 업데이트 (게임 내에서 호출)"""
        try:
            self._validate_initialized()

            if player_id not in self.players:
                return self._create_response(
                    success=False,
                    message="Player not found",
                    error_code="PLAYER_NOT_FOUND"
                )

            player = self.players[player_id]

            # 경험치 추가
            if experience_gained > 0:
                player.experience += experience_gained

                # 레벨업 체크 (경험치 100당 레벨 1 증가)
                new_level = 1 + (player.experience // 100)
                if new_level > player.level:
                    old_level = player.level
                    player.level = new_level

                    # 클래스 업그레이드
                    if player.level >= 25:
                        player.current_class = "Risk Transcender"
                    elif player.level >= 15:
                        player.current_class = "Risk Master"
                    elif player.level >= 5:
                        player.current_class = "Risk Walker"

                    self.logger.info(f"Player {player_id} leveled up: {old_level} -> {new_level}")

            # 스킬 해제
            if skills_unlocked:
                for skill in skills_unlocked:
                    if skill not in player.unlocked_skills:
                        player.unlocked_skills.append(skill)

            # 기능 해제
            if features_unlocked:
                await self.game_manager.unlock_features(player_id, features_unlocked)

            # 세션 업데이트
            if player_id in self.player_sessions:
                self.player_sessions[player_id]["last_active"] = datetime.now()

            return self._create_response(
                success=True,
                data={
                    "level": player.level,
                    "experience": player.experience,
                    "current_class": player.current_class,
                    "newly_unlocked_skills": skills_unlocked or [],
                    "newly_unlocked_features": features_unlocked or []
                },
                message="Player progress updated"
            )

        except Exception as e:
            return self._handle_error(e, "update_player_progress")

    async def consume_energy(self, player_id: str, amount: int) -> Dict[str, Any]:
        """플레이어 에너지 소모"""
        try:
            self._validate_initialized()

            if player_id not in self.players:
                return self._create_response(
                    success=False,
                    message="Player not found",
                    error_code="PLAYER_NOT_FOUND"
                )

            player = self.players[player_id]

            if player.energy < amount:
                return self._create_response(
                    success=False,
                    message="Insufficient energy",
                    error_code="INSUFFICIENT_ENERGY"
                )

            player.energy -= amount

            return self._create_response(
                success=True,
                data={
                    "remaining_energy": player.energy,
                    "energy_consumed": amount
                }
            )

        except Exception as e:
            return self._handle_error(e, "consume_energy")

    async def restore_energy(self, player_id: str, amount: int = None) -> Dict[str, Any]:
        """플레이어 에너지 회복 (amount가 None이면 완전 회복)"""
        try:
            self._validate_initialized()

            if player_id not in self.players:
                return self._create_response(
                    success=False,
                    message="Player not found",
                    error_code="PLAYER_NOT_FOUND"
                )

            player = self.players[player_id]

            if amount is None:
                player.energy = player.max_energy
            else:
                player.energy = min(player.energy + amount, player.max_energy)

            return self._create_response(
                success=True,
                data={
                    "current_energy": player.energy,
                    "max_energy": player.max_energy
                }
            )

        except Exception as e:
            return self._handle_error(e, "restore_energy")

    async def get_all_players(self) -> Dict[str, Any]:
        """모든 플레이어 목록 조회 (관리자용)"""
        try:
            self._validate_initialized()

            players_data = []
            for player_id, player in self.players.items():
                session = self.player_sessions.get(player_id, {})
                players_data.append({
                    "id": player.id,
                    "username": player.username,
                    "level": player.level,
                    "experience": player.experience,
                    "current_class": player.current_class,
                    "created_at": player.created_at.isoformat(),
                    "last_active": session.get("last_active", datetime.now()).isoformat()
                })

            return self._create_response(
                success=True,
                data={
                    "players": players_data,
                    "total_count": len(players_data)
                }
            )

        except Exception as e:
            return self._handle_error(e, "get_all_players")
