#!/usr/bin/env python3
"""Walk Risk Auto Tutorial Demo - 자동 진행 튜토리얼 데모"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich import box
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from walk_risk.core.game_state.game_manager import GameManager
from walk_risk.tutorials.tutorial_manager import TutorialManager
from walk_risk.models.player.base import Player
from walk_risk.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class AutoTutorialDemo:
    """자동 진행 튜토리얼 데모"""
    
    def __init__(self):
        self.console = console
        
    async def run_auto_demo(self):
        """자동 데모 실행"""
        try:
            # 게임 초기화
            game_manager = GameManager()
            tutorial_manager = TutorialManager(game_manager)
            
            # 테스트 플레이어
            player = Player(
                id="auto_demo_player",
                name="김초보",
                level=1,
                experience=0,
                portfolio_value=1_000_000
            )
            
            self._show_intro()
            await asyncio.sleep(2)
            
            # 튜토리얼 시작
            result = await tutorial_manager.start_tutorial(player, "buffett")
            
            if not result["success"]:
                self.console.print(f"[red]❌ 튜토리얼 시작 실패: {result.get('error')}[/red]")
                return
                
            # 모든 스테이지 자동 진행
            stage_count = 0
            max_stages = 6  # 6개 스테이지
            
            while stage_count < max_stages:
                progress = tutorial_manager.get_progress(player.id)
                if not progress:
                    break
                    
                # 현재 스테이지 표시
                await self._display_auto_stage(progress.current_stage, result.get("data", {}))
                await asyncio.sleep(3)  # 3초 대기
                
                # 다음 스테이지로 진행
                result = await tutorial_manager.advance_stage(player)
                
                if result.get("completed"):
                    await self._display_completion(result)
                    break
                elif not result["success"]:
                    self.console.print(f"[red]❌ 오류: {result.get('error')}[/red]")
                    break
                    
                stage_count += 1
                
            self.console.print("\n[green]🎉 자동 데모 완료![/green]")
            
        except Exception as e:
            logger.error(f"자동 데모 실행 오류: {e}", exc_info=True)
            
    def _show_intro(self):
        """인트로 화면"""
        intro_text = """
[bold yellow]🎯 Walk Risk: 언락 리스크 마스터[/bold yellow]
[bold cyan]자동 튜토리얼 데모[/bold cyan]

[white]🏛️ 워런 버핏과 함께하는 투자 여정을 자동으로 체험해보세요![/white]

🔄 자동 진행 모드: 6개 스테이지를 순차적으로 체험합니다
        """
        
        panel = Panel(
            intro_text,
            title="🎆 자동 데모 시작 🎆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(panel)
        
    async def _display_auto_stage(self, stage, data):
        """스테이지 자동 표시"""
        stage_names = {
            "welcome": "👋 환영 인사",
            "mentor_selection": "🏛️ 멘토 선택",
            "first_risk": "🔒 첫 리스크 도전",
            "portfolio_basics": "💼 포트폴리오 기초",
            "market_simulation": "📈 시장 시뮬레이션",
            "graduation": "🎓 졸업"
        }
        
        stage_name = stage_names.get(stage.value, stage.value)
        
        # 스테이지 헤더
        header_panel = Panel(
            f"[bold cyan]{stage_name}[/bold cyan]\n\n자동 진행로 체험하고 있습니다...",
            title=f"🎯 스테이지: {stage_name}",
            border_style="yellow"
        )
        self.console.print(header_panel)
        
        # 데이터가 있으면 주요 내용 표시
        if data:
            if "message" in data:
                self.console.print(f"\n[white]{data['message'][:200]}...[/white]")
            elif "mentor_info" in data:
                self.console.print(f"\n[white]{data['mentor_info'][:200]}...[/white]")
            elif "risk_intro" in data:
                self.console.print(f"\n[white]{data['risk_intro'][:200]}...[/white]")
            elif "lesson" in data:
                self.console.print(f"\n[white]{data['lesson'][:200]}...[/white]")
            elif "graduation_message" in data:
                self.console.print(f"\n[white]{data['graduation_message'][:200]}...[/white]")
                
        # 감정 상태 표시
        if "emotional_state" in data:
            emotions = data["emotional_state"]
            emotion_text = f"""
📊 감정 상태:
😎 자신감: {emotions.get('confidence', 3)}/10
😰 두려움: {emotions.get('fear', 7)}/10
🤑 탐욕: {emotions.get('greed', 5)}/10
⏳ 인내심: {emotions.get('patience', 2)}/10
            """
            
            emotion_panel = Panel(
                emotion_text.strip(),
                title="📊 감정 상태",
                border_style="blue",
                box=box.SIMPLE
            )
            self.console.print(emotion_panel)
            
    async def _display_completion(self, result):
        """완료 표시"""
        completion_text = f"""
🎉 튜토리얼 완료!

🏆 획득한 보상:
• 경험치: {result['rewards']['experience']} XP
• 칭호: {result['rewards']['title']}
• 해제된 기능: {', '.join(result['rewards']['unlock_features'])}

이제 실전 투자를 시작할 준비가 되었습니다!
        """
        
        completion_panel = Panel(
            completion_text,
            title="🏆 튜토리얼 완료 🏆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(completion_panel)
        
        # 축하 효과
        for i in range(3):
            self.console.print(f"[bright_yellow]{'🎉' * 10}[/bright_yellow]")
            await asyncio.sleep(0.5)
            
            
async def main():
    """메인 함수"""
    demo = AutoTutorialDemo()
    await demo.run_auto_demo()
    
    
if __name__ == "__main__":
    asyncio.run(main())