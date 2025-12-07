"""Player base model - 밸런스 조정된 성장 시스템"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# 레벨별 필요 경험치 테이블 (초반은 빠르게, 후반은 느리게)
LEVEL_XP_TABLE = {
    1: 50,      # 첫 레벨은 쉽게
    2: 80,
    3: 120,
    4: 170,
    5: 230,     # 레벨 5 마일스톤
    6: 300,
    7: 380,
    8: 470,
    9: 570,
    10: 700,    # 레벨 10 마일스톤
    11: 850,
    12: 1020,
    13: 1210,
    14: 1420,
    15: 1700,   # 레벨 15 마일스톤 (마스터 투자자)
    16: 2000,
    17: 2350,
    18: 2750,
    19: 3200,
    20: 4000,   # 레벨 20 마일스톤 (리스크 초월자)
}


def get_xp_for_level(level: int) -> int:
    """레벨별 필요 경험치 반환"""
    if level in LEVEL_XP_TABLE:
        return LEVEL_XP_TABLE[level]
    # 20레벨 이후는 점진적 증가
    return 4000 + (level - 20) * 500


# 레벨별 칭호
LEVEL_TITLES = {
    1: "초보 투자자",
    2: "견습 분석가",
    3: "주니어 분석가",
    4: "분석가",
    5: "시니어 분석가",
    6: "리스크 스카우트",
    7: "리스크 헌터",
    8: "리스크 전문가",
    9: "리스크 마스터",
    10: "시장 통찰자",
    11: "시장 해석가",
    12: "트렌드 리더",
    13: "베테랑 투자자",
    14: "엘리트 투자자",
    15: "마스터 투자자",
    16: "투자 전략가",
    17: "시장 현자",
    18: "월스트리트 베테랑",
    19: "투자 레전드",
    20: "리스크 초월자"
}


@dataclass
class Player:
    """플레이어 기본 모델 - 밸런스 조정됨"""

    id: str
    username: str = ""
    email: str = ""
    name: Optional[str] = None
    level: int = 1
    experience: int = 0
    current_class: str = "Risk Novice"
    energy: int = 100
    max_energy: int = 100
    unlocked_skills: List[str] = field(default_factory=list)
    risk_mastery: Dict[str, int] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    portfolio_value: float = 1_000_000  # 기본 100만원
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    # 추가 통계
    total_puzzles_completed: int = 0
    total_puzzles_correct: int = 0
    current_streak: int = 0
    best_streak: int = 0
    total_xp_earned: int = 0

    def __post_init__(self) -> None:
        """Ensure backwards compatibility with legacy CLI usage."""
        if self.name is None:
            self.name = self.username or "Player"
        if not self.username and self.name:
            self.username = self.name
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def add_experience(self, amount: int, source: str = "puzzle") -> Tuple[int, bool, Optional[str]]:
        """경험치 추가

        Args:
            amount: 기본 경험치
            source: 경험치 출처 (puzzle, streak_bonus, daily_bonus 등)

        Returns:
            (현재 레벨, 레벨업 여부, 새 칭호 or None)
        """
        old_level = self.level
        self.experience += amount
        self.total_xp_earned += amount

        leveled_up = False
        new_title = None

        # 레벨업 체크 (테이블 기반)
        while self.experience >= get_xp_for_level(self.level):
            self.experience -= get_xp_for_level(self.level)
            self.level += 1
            self._update_class_by_level()
            leveled_up = True

        if leveled_up:
            new_title = self.get_title()

        return self.level, leveled_up, new_title

    def get_xp_to_next_level(self) -> int:
        """다음 레벨까지 필요한 경험치"""
        return get_xp_for_level(self.level)

    def get_xp_progress_percent(self) -> float:
        """현재 레벨 진행률 (0~100)"""
        needed = get_xp_for_level(self.level)
        if needed <= 0:
            return 100.0
        return min(100.0, (self.experience / needed) * 100)

    def get_title(self) -> str:
        """현재 칭호 반환"""
        return LEVEL_TITLES.get(self.level, f"레벨 {self.level}")

    def add_achievement(self, achievement: str) -> bool:
        """업적 추가

        Returns:
            새로 추가되었으면 True
        """
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            return True
        return False

    def record_puzzle_result(self, is_correct: bool) -> Dict[str, Any]:
        """퍼즐 결과 기록

        Returns:
            결과 정보 (연속 기록, 보너스 등)
        """
        self.total_puzzles_completed += 1

        result = {
            "streak_broken": False,
            "new_best_streak": False,
            "streak_bonus_xp": 0
        }

        if is_correct:
            self.total_puzzles_correct += 1
            self.current_streak += 1

            # 최고 기록 갱신
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
                result["new_best_streak"] = True

            # 연속 보너스 XP
            if self.current_streak >= 3:
                result["streak_bonus_xp"] = self._calculate_streak_bonus()
        else:
            if self.current_streak > 0:
                result["streak_broken"] = True
            self.current_streak = 0

        return result

    def _calculate_streak_bonus(self) -> int:
        """연속 성공 보너스 XP 계산"""
        if self.current_streak >= 10:
            return 100  # 10연속: +100 XP
        elif self.current_streak >= 7:
            return 50   # 7연속: +50 XP
        elif self.current_streak >= 5:
            return 30   # 5연속: +30 XP
        elif self.current_streak >= 3:
            return 15   # 3연속: +15 XP
        return 0

    def get_accuracy(self) -> float:
        """정확도 계산 (0~100)"""
        if self.total_puzzles_completed == 0:
            return 0.0
        return (self.total_puzzles_correct / self.total_puzzles_completed) * 100

    def add_mastery(self, puzzle_type: str, amount: int = 1) -> Tuple[int, bool]:
        """숙련도 추가

        Args:
            puzzle_type: 퍼즐 유형
            amount: 증가량

        Returns:
            (현재 숙련도, 숙련도 레벨업 여부)
        """
        if puzzle_type not in self.risk_mastery:
            self.risk_mastery[puzzle_type] = 0

        old_level = self.risk_mastery[puzzle_type] // 5  # 5포인트당 1레벨
        self.risk_mastery[puzzle_type] += amount
        new_level = self.risk_mastery[puzzle_type] // 5

        return self.risk_mastery[puzzle_type], new_level > old_level

    def get_mastery_level(self, puzzle_type: str) -> int:
        """특정 퍼즐 유형의 숙련도 레벨 (0~5)"""
        points = self.risk_mastery.get(puzzle_type, 0)
        return min(5, points // 5)

    def _update_class_by_level(self) -> None:
        """레벨에 따른 플레이어 클래스 업데이트"""
        if self.level >= 20:
            self.current_class = "Risk Transcender"
        elif self.level >= 15:
            self.current_class = "Risk Master"
        elif self.level >= 10:
            self.current_class = "Risk Expert"
        elif self.level >= 5:
            self.current_class = "Risk Walker"
        else:
            self.current_class = "Risk Novice"


# 보상 계산 유틸리티 함수
def calculate_puzzle_reward(
    base_xp: int,
    accuracy: float,
    time_taken_seconds: float,
    difficulty: str,
    streak_count: int = 0,
    mastery_level: int = 0
) -> Dict[str, int]:
    """퍼즐 보상 계산

    Args:
        base_xp: 기본 경험치
        accuracy: 정확도 (0~1)
        time_taken_seconds: 소요 시간 (초)
        difficulty: 난이도 (beginner, intermediate, advanced, master)
        streak_count: 현재 연속 성공 횟수
        mastery_level: 해당 유형 숙련도 레벨

    Returns:
        보상 상세 내역
    """
    # 기본 보상
    xp = base_xp

    # 정확도 보너스 (최대 2배)
    accuracy_bonus = int(xp * accuracy)
    xp += accuracy_bonus

    # 시간 보너스 (빠를수록 높음)
    time_bonus = 0
    if time_taken_seconds < 30:
        time_bonus = int(xp * 0.5)  # 30초 이내: +50%
    elif time_taken_seconds < 60:
        time_bonus = int(xp * 0.25)  # 1분 이내: +25%
    elif time_taken_seconds < 120:
        time_bonus = int(xp * 0.1)  # 2분 이내: +10%
    xp += time_bonus

    # 난이도 보너스
    difficulty_multipliers = {
        "beginner": 1.0,
        "intermediate": 1.3,
        "advanced": 1.7,
        "master": 2.5
    }
    difficulty_mult = difficulty_multipliers.get(difficulty.lower(), 1.0)
    difficulty_bonus = int(xp * (difficulty_mult - 1))
    xp += difficulty_bonus

    # 연속 성공 보너스
    streak_bonus = 0
    if streak_count >= 10:
        streak_bonus = 100
    elif streak_count >= 7:
        streak_bonus = 50
    elif streak_count >= 5:
        streak_bonus = 30
    elif streak_count >= 3:
        streak_bonus = 15
    xp += streak_bonus

    # 숙련도 보너스 (레벨당 5%)
    mastery_bonus = int(base_xp * (mastery_level * 0.05))
    xp += mastery_bonus

    return {
        "total_xp": xp,
        "base_xp": base_xp,
        "accuracy_bonus": accuracy_bonus,
        "time_bonus": time_bonus,
        "difficulty_bonus": difficulty_bonus,
        "streak_bonus": streak_bonus,
        "mastery_bonus": mastery_bonus
    }
