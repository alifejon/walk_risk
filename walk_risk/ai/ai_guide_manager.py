"""AI Guide Manager - Simple version for tutorial"""

from typing import Dict, Any, Optional


class AIGuideManager:
    """튜토리얼용 간단한 AI 가이드 매니저"""
    
    def __init__(self):
        self.mentors = {
            "buffett": "Warren Buffett",
            "lynch": "Peter Lynch",
            "graham": "Benjamin Graham"
        }
        
    def get_mentor_advice(self, mentor_id: str, context: Dict[str, Any]) -> str:
        """멘토 조언 반환"""
        return f"{self.mentors.get(mentor_id, 'Mentor')}의 조언입니다."