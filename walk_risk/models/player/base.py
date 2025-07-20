"""
Player model and progression system
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

from ..risk.base import RiskKey, RiskCategory, RiskLevel


class PlayerClass(Enum):
    """Player class evolution"""
    RISK_NOVICE = "risk_novice"
    RISK_WALKER = "risk_walker"
    RISK_MASTER = "risk_master"
    RISK_TRANSCENDER = "risk_transcender"


class SkillPath(Enum):
    """Skill tree paths"""
    MARKET_RISK_MASTER = "market_risk_master"
    CREDIT_RISK_GUARDIAN = "credit_risk_guardian"
    OPERATIONAL_RISK_CONTROLLER = "operational_risk_controller"
    STRATEGIC_RISK_VISIONARY = "strategic_risk_visionary"


@dataclass
class PlayerStats:
    """Player statistics"""
    level: int = 1
    experience: int = 0
    total_risks_unlocked: int = 0
    total_risks_mastered: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    
    # Category-specific stats
    risks_by_category: Dict[RiskCategory, int] = field(default_factory=dict)
    mastery_by_category: Dict[RiskCategory, float] = field(default_factory=dict)
    
    # Time-based stats
    total_play_time: int = 0  # seconds
    longest_streak: int = 0
    current_streak: int = 0
    
    def calculate_accuracy(self) -> float:
        """Calculate prediction accuracy"""
        total = self.successful_predictions + self.failed_predictions
        return self.successful_predictions / total if total > 0 else 0.0
    
    def get_category_mastery(self, category: RiskCategory) -> float:
        """Get mastery level for specific risk category"""
        return self.mastery_by_category.get(category, 0.0)


@dataclass
class SkillTreeNode:
    """Individual skill in the skill tree"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    path: SkillPath = SkillPath.MARKET_RISK_MASTER
    level: int = 0
    max_level: int = 99
    
    # Requirements
    prerequisite_skills: List[str] = field(default_factory=list)
    required_experience: int = 0
    required_category_mastery: Dict[RiskCategory, float] = field(default_factory=dict)
    
    # Effects
    stat_bonuses: Dict[str, float] = field(default_factory=dict)
    special_abilities: List[str] = field(default_factory=list)
    
    def can_upgrade(self, player_stats: PlayerStats, unlocked_skills: Dict[str, int]) -> bool:
        """Check if skill can be upgraded"""
        if self.level >= self.max_level:
            return False
            
        # Check experience requirement
        if player_stats.experience < self.required_experience:
            return False
            
        # Check prerequisite skills
        for prereq in self.prerequisite_skills:
            if unlocked_skills.get(prereq, 0) == 0:
                return False
        
        # Check category mastery requirements
        for category, required_mastery in self.required_category_mastery.items():
            if player_stats.get_category_mastery(category) < required_mastery:
                return False
        
        return True


@dataclass
class Player:
    """Player profile and progression"""
    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    email: str = ""
    
    # Game progression
    player_class: PlayerClass = PlayerClass.RISK_NOVICE
    stats: PlayerStats = field(default_factory=PlayerStats)
    
    # Skills and abilities
    unlocked_skills: Dict[str, int] = field(default_factory=dict)  # skill_id -> level
    active_skill_path: Optional[SkillPath] = None
    
    # Inventory
    owned_keys: List[RiskKey] = field(default_factory=list)
    active_risks: List[str] = field(default_factory=list)  # risk_ids
    completed_risks: List[str] = field(default_factory=list)
    
    # Portfolio reference
    portfolio_id: Optional[str] = None
    
    # Achievements and badges
    achievements: List[str] = field(default_factory=list)
    badges: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    def add_experience(self, amount: int) -> None:
        """Add experience and handle level up"""
        self.stats.experience += amount
        
        # Simple level calculation (100 exp per level)
        new_level = (self.stats.experience // 100) + 1
        if new_level > self.stats.level:
            self.stats.level = new_level
            self._check_class_evolution()
    
    def _check_class_evolution(self) -> None:
        """Check if player can evolve to next class"""
        if self.stats.level >= 50 and self.player_class == PlayerClass.RISK_NOVICE:
            self.player_class = PlayerClass.RISK_WALKER
        elif self.stats.level >= 100 and self.player_class == PlayerClass.RISK_WALKER:
            self.player_class = PlayerClass.RISK_MASTER
        elif self.stats.level >= 200 and self.player_class == PlayerClass.RISK_MASTER:
            self.player_class = PlayerClass.RISK_TRANSCENDER
    
    def unlock_skill(self, skill_id: str) -> bool:
        """Unlock or upgrade a skill"""
        current_level = self.unlocked_skills.get(skill_id, 0)
        self.unlocked_skills[skill_id] = current_level + 1
        return True
    
    def add_key(self, key: RiskKey) -> None:
        """Add a risk key to inventory"""
        self.owned_keys.append(key)
    
    def complete_risk(self, risk_id: str, mastery_level: RiskLevel) -> None:
        """Mark risk as completed and update stats"""
        if risk_id in self.active_risks:
            self.active_risks.remove(risk_id)
        
        if risk_id not in self.completed_risks:
            self.completed_risks.append(risk_id)
            self.stats.total_risks_unlocked += 1
            
            if mastery_level == RiskLevel.MASTERED:
                self.stats.total_risks_mastered += 1
        
        self.last_active = datetime.now()