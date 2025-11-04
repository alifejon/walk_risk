"""Simple Game Manager for Tutorial Demo"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime


class GameManager:
    """튜토리얼 데모를 위한 간단한 게임 매니저"""
    
    def __init__(self):
        self.players = {}
        self.game_state = {
            "initialized": True,
            "start_time": datetime.now(),
            "features": {}
        }
        
    async def unlock_features(self, player_id: str, features: List[str]) -> bool:
        """플레이어에게 기능 해제"""
        if player_id not in self.game_state["features"]:
            self.game_state["features"][player_id] = []
            
        self.game_state["features"][player_id].extend(features)
        return True
        
    def get_player_features(self, player_id: str) -> List[str]:
        """플레이어의 해제된 기능 조회"""
        return self.game_state["features"].get(player_id, [])