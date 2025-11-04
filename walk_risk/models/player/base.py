"""Player base model"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Player:
    """플레이어 기본 모델"""

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

    def __post_init__(self) -> None:
        """Ensure backwards compatibility with legacy CLI usage."""
        if self.name is None:
            self.name = self.username or "Player"
        if not self.username and self.name:
            self.username = self.name
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def add_experience(self, amount: int) -> int:
        """경험치 추가"""
        self.experience += amount

        # 레벨업 체크 (간단한 공식)
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            self._update_class_by_level()

        return self.level

    def add_achievement(self, achievement: str) -> None:
        """업적 추가"""
        if achievement not in self.achievements:
            self.achievements.append(achievement)

    def _update_class_by_level(self) -> None:
        """레벨에 따른 플레이어 클래스 업데이트"""
        if self.level >= 25:
            self.current_class = "Risk Transcender"
        elif self.level >= 15:
            self.current_class = "Risk Master"
        elif self.level >= 5:
            self.current_class = "Risk Walker"
        else:
            self.current_class = "Risk Novice"
