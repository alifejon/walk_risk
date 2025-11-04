#!/usr/bin/env python3
"""Walk Risk Tutorial Demo - 튜토리얼 데모 실행"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from walk_risk.core.game_state.game_manager import GameManager
from walk_risk.tutorials.tutorial_manager import TutorialManager
from walk_risk.ui.tutorial_cli import TutorialCLI
from walk_risk.models.player.base import Player
from walk_risk.utils.logger import setup_logger

logger = setup_logger(__name__)


async def run_tutorial_demo():
    """튜토리얼 데모 실행"""
    try:
        # Game Manager 초기화 (간단한 설정으로)
        game_manager = GameManager()
        
        # Tutorial Manager 생성
        tutorial_manager = TutorialManager(game_manager)
        
        # Tutorial CLI 생성
        tutorial_cli = TutorialCLI(tutorial_manager)
        
        # 테스트 플레이어 생성
        test_player = Player(
            id="test_player_001",
            name="김초보",
            level=1,
            experience=0,
            risk_mastery={},
            achievements=[],
            portfolio_value=1_000_000  # 100만원 시작
        )
        
        logger.info(f"튜토리얼 시작: {test_player.name}")
        
        # 튜토리얼 흐름 실행
        await tutorial_cli.start_tutorial_flow(test_player)
        
        logger.info("튜토리얼 데모 종료")
        
    except KeyboardInterrupt:
        logger.info("\n튜토리얼 중단")
    except Exception as e:
        logger.error(f"튜토리얼 실행 오류: {e}", exc_info=True)
        raise


def main():
    """메인 진입점"""
    print("""
🎮 Walk Risk: 언락 리스크 마스터 - 튜토리얼 데모
===========================================

🏛️ 워런 버핏과 함께하는 투자 여정을 시작합니다!
    """)
    
    # 비동기 함수 실행
    asyncio.run(run_tutorial_demo())


if __name__ == "__main__":
    main()