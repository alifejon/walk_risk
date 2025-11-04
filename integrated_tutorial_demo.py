#!/usr/bin/env python3
"""Integrated Tutorial Demo - 퍼즐 시스템이 통합된 새로운 튜토리얼"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from walk_risk.tutorials.puzzle_tutorial import PuzzleTutorial, PuzzleTutorialProgress
from walk_risk.tutorials.tutorial_manager import TutorialManager
from walk_risk.core.game_state.game_manager import GameManager
from walk_risk.ai.mentor_personas import BuffettPersona
from walk_risk.models.player.base import Player
from walk_risk.utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class IntegratedTutorialDemo:
    """퍼즐 시스템이 통합된 새로운 튜토리얼 데모"""
    
    def __init__(self):
        self.console = console
        
        # 기존 시스템들
        self.game_manager = GameManager()
        self.tutorial_manager = TutorialManager(self.game_manager)
        
        # 새로운 퍼즐 시스템
        self.puzzle_tutorial = PuzzleTutorial(self.tutorial_manager, self.game_manager)
        
        # 업그레이드된 멘토
        self.buffett_mentor = BuffettPersona()
        
        # 플레이어
        self.player = None
        
    async def run_integrated_demo(self):
        """통합 튜토리얼 데모 실행"""
        try:
            self._show_intro()
            
            # 플레이어 생성
            self.player = Player(
                id="puzzle_tutorial_player",
                name="퍼즐 마스터",
                level=1,
                experience=0,
                portfolio_value=1_000_000
            )
            
            # 1단계: 전통적 환영 인사
            await self._stage_1_traditional_welcome()
            
            # 2단계: 퍼즐 컨셉 소개 (NEW!)
            await self._stage_2_puzzle_introduction()
            
            # 3단계: 첫 번째 퍼즐 체험 (NEW!)
            await self._stage_3_first_puzzle()
            
            # 4단계: 가이드된 조사 과정 (NEW!)
            await self._stage_4_guided_investigation()
            
            # 5단계: 가설 수립 훈련 (NEW!)
            await self._stage_5_hypothesis_training()
            
            # 6단계: 검증 및 학습 (NEW!)
            await self._stage_6_validation_learning()
            
            # 7단계: 졸업 및 다음 단계
            await self._stage_7_graduation()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]👋 튜토리얼을 중단합니다.[/yellow]")
        except Exception as e:
            logger.error(f"튜토리얼 실행 오류: {e}", exc_info=True)
            
    def _show_intro(self):
        """새로운 튜토리얼 인트로"""
        intro_panel = Panel(
            """
[bold yellow]🎮 Walk Risk: 진화한 투자 학습 게임[/bold yellow]
[bold cyan]통합 퍼즐 튜토리얼[/bold cyan]

이제 Walk Risk가 진짜 게임이 되었습니다!

[bold green]🆕 새로운 기능들:[/bold green]
• 🔍 리스크 퍼즐 시스템
• 🕵️ 탐정식 단서 수집
• 💡 가설 수립 및 검증  
• 🏛️ 멘토의 실시간 힌트

[cyan]이제 투자는 "도박"이 아닌 "지적 탐구"입니다![/cyan]

워런 버핏과 함께 첫 번째 투자 미스터리를 풀어보세요.
            """.strip(),
            title="🚀 새로운 Walk Risk 체험",
            border_style="bright_green"
        )
        self.console.print(intro_panel)
        time.sleep(3)
        
    async def _stage_1_traditional_welcome(self):
        """1단계: 전통적 환영 인사"""
        self.console.print("\n[bold yellow]📍 1단계: 환영 인사[/bold yellow]")
        time.sleep(1)
        
        welcome_panel = Panel(
            f"""
🏛️ 워런 버핏: "{self.player.name}님, Walk Risk의 새로운 세계에 오신 것을 환영합니다!

저는 워런 버핏입니다. 50년 넘게 투자 세계에서 살아왔죠.

오늘부터 제가 당신의 멘토가 되어 
진정한 투자의 세계를 보여드리겠습니다.

하지만 기존의 방식과는 완전히 다를 겁니다.
우리는 이제 투자를 '퍼즐'로 접근할 거예요!"
            """.strip(),
            title="👋 멘토 인사",
            border_style="yellow"
        )
        self.console.print(welcome_panel)
        time.sleep(3)
        
    async def _stage_2_puzzle_introduction(self):
        """2단계: 퍼즐 컨셉 소개"""
        self.console.print("\n[bold yellow]📍 2단계: 새로운 투자 철학[/bold yellow]")
        time.sleep(1)
        
        # 퍼즐 컨셉 소개
        intro_data = await self.puzzle_tutorial.introduce_puzzle_concept(self.player)
        
        concept_panel = Panel(
            intro_data["mentor_message"],
            title="🔍 투자 = 퍼즐 풀기",
            border_style="cyan"
        )
        self.console.print(concept_panel)
        
        # 핵심 개념 표시
        concepts_table = Table(title="🎯 핵심 개념", box=None)
        concepts_table.add_column("개념", style="cyan")
        
        for concept in intro_data["key_concepts"]:
            concepts_table.add_row(concept)
            
        self.console.print(concepts_table)
        time.sleep(4)
        
    async def _stage_3_first_puzzle(self):
        """3단계: 첫 번째 퍼즐 제시"""
        self.console.print("\n[bold yellow]📍 3단계: 첫 번째 미스터리 발견[/bold yellow]")
        time.sleep(1)
        
        # 퍼즐 생성
        puzzle = await self.puzzle_tutorial.create_tutorial_puzzle()
        
        puzzle_panel = Panel(
            puzzle.description,
            title=f"🔒 {puzzle.title}",
            border_style="red"
        )
        self.console.print(puzzle_panel)
        
        # 버핏의 첫 번째 힌트
        hint = self.buffett_mentor.give_puzzle_hint(
            puzzle_data={},
            discovered_clues=[],
            investigation_progress=0.0
        )
        
        hint_panel = Panel(
            hint,
            title="💡 멘토의 첫 번째 힌트",
            border_style="blue"
        )
        self.console.print(hint_panel)
        time.sleep(4)
        
    async def _stage_4_guided_investigation(self):
        """4단계: 가이드된 조사 과정"""
        self.console.print("\n[bold yellow]📍 4단계: 단서 수집 실습[/bold yellow]")
        time.sleep(1)
        
        # 가이드된 조사 실행
        investigation_steps = await self.puzzle_tutorial.guided_investigation(self.player)
        
        for i, step in enumerate(investigation_steps, 1):
            if step["success"]:
                self.console.print(f"\n[cyan]🔍 조사 {i}: {step['clue_type']} 분석[/cyan]")
                self.console.print(step["intro_message"])
                
                # 조사 중 애니메이션
                self.console.print("조사 중...")
                time.sleep(2)
                
                # 결과 표시
                result_panel = Panel(
                    f"""
📄 발견한 정보: {step['clue_content']}

💡 통찰: {step['insights'][0]}
신뢰도: {step['reliability']:.0%}

🎓 설명: {step['explanation']}
                    """.strip(),
                    title=f"✅ {step['clue_type']} 조사 완료",
                    border_style="green"
                )
                self.console.print(result_panel)
                
                # 진행 상황에 따른 버핏의 힌트
                hint = self.buffett_mentor.give_puzzle_hint(
                    puzzle_data={},
                    discovered_clues=self.puzzle_tutorial.discovered_clues,
                    investigation_progress=i / 3
                )
                
                hint_panel = Panel(
                    hint,
                    title=f"💬 멘토 조언 #{i}",
                    border_style="blue"
                )
                self.console.print(hint_panel)
                time.sleep(3)
            else:
                self.console.print(f"[red]❌ {step['message']}[/red]")
                
    async def _stage_5_hypothesis_training(self):
        """5단계: 가설 수립 훈련"""
        self.console.print("\n[bold yellow]📍 5단계: 가설 수립 실습[/bold yellow]")
        time.sleep(1)
        
        # 가설 수립 가이드
        guidance = await self.puzzle_tutorial.guide_hypothesis_creation(self.player)
        
        guidance_panel = Panel(
            guidance["mentor_message"],
            title="💡 가설 수립 가이드",
            border_style="magenta"
        )
        self.console.print(guidance_panel)
        
        # 가설 선택지 표시
        hypotheses_table = Table(title="🎯 추천 가설들", box=None)
        hypotheses_table.add_column("#", style="cyan")
        hypotheses_table.add_column("가설", style="white")
        hypotheses_table.add_column("타입", style="yellow")
        
        for i, hyp in enumerate(guidance["suggested_hypotheses"], 1):
            hypotheses_table.add_row(
                str(i),
                hyp["statement"],
                hyp["type"].value
            )
            
        self.console.print(hypotheses_table)
        
        # 자동으로 두 번째 가설 선택 (튜토리얼용)
        selected_choice = 1  # BULLISH 가설
        self.console.print(f"\n[green]✅ 가설 #{selected_choice + 1} 선택: 일시적 조정으로 반등 예상[/green]")
        
        # 선택한 가설에 대한 버핏의 검증
        hypothesis_feedback = self.buffett_mentor.validate_hypothesis_thinking(
            hypothesis="NAVER는 일시적 조정으로 반등 예상",
            confidence=0.7,
            evidence_strength=0.6
        )
        
        feedback_panel = Panel(
            hypothesis_feedback,
            title="🎯 가설 검증",
            border_style="yellow"
        )
        self.console.print(feedback_panel)
        time.sleep(4)
        
    async def _stage_6_validation_learning(self):
        """6단계: 검증 및 학습"""
        self.console.print("\n[bold yellow]📍 6단계: 가설 검증 및 결과 학습[/bold yellow]")
        time.sleep(1)
        
        self.console.print("🔬 시장 시뮬레이션 실행 중...")
        time.sleep(2)
        
        # 가설 검증 실행
        validation_result = await self.puzzle_tutorial.validate_tutorial_hypothesis(
            hypothesis_choice=1,  # BULLISH
            player=self.player
        )
        
        # 검증 결과 표시
        result_panel = Panel(
            validation_result["feedback"],
            title="📊 검증 결과",
            border_style="green" if validation_result["success"] else "red"
        )
        self.console.print(result_panel)
        
        # 버핏의 완료 피드백
        completion_feedback = self.buffett_mentor.puzzle_completion_feedback(
            accuracy=validation_result["accuracy"],
            time_taken=300,  # 5분 가정
            clues_used=len(self.puzzle_tutorial.discovered_clues)
        )
        
        mentor_feedback_panel = Panel(
            completion_feedback,
            title="🏛️ 멘토의 최종 평가",
            border_style="gold1"
        )
        self.console.print(mentor_feedback_panel)
        
        # 보상 표시
        self.console.print(f"\n[green]🎉 퍼즐 해결 보상:[/green]")
        self.console.print(f"• 경험치: [yellow]{validation_result['xp_earned']} XP[/yellow]")
        self.console.print(f"• 새로운 스킬: [cyan]{validation_result['skill_gained']}[/cyan]")
        time.sleep(4)
        
    async def _stage_7_graduation(self):
        """7단계: 졸업 및 다음 단계"""
        self.console.print("\n[bold yellow]📍 7단계: 퍼즐 마스터 졸업[/bold yellow]")
        time.sleep(1)
        
        # 졸업 메시지
        completion_data = await self.puzzle_tutorial.complete_puzzle_tutorial(self.player)
        
        graduation_panel = Panel(
            completion_data["mentor_message"],
            title="🎓 퍼즐 마스터 졸업",
            border_style="gold1"
        )
        self.console.print(graduation_panel)
        
        # 습득한 스킬 표시
        skills_table = Table(title="🎯 습득한 스킬", box=None)
        skills_table.add_column("스킬", style="cyan")
        
        for skill in completion_data["skills_learned"]:
            skills_table.add_row(skill)
            
        self.console.print(skills_table)
        
        # 해금된 기능들
        features_table = Table(title="🔓 해금된 기능", box=None)
        features_table.add_column("기능", style="yellow")
        
        for feature in completion_data["unlocked_features"]:
            features_table.add_row(feature)
            
        self.console.print(features_table)
        
        # 최종 메시지
        final_panel = Panel(
            """
🎊 축하합니다! 이제 당신은 진정한 "퍼즐 마스터"입니다!

🔥 변화된 점:
• 투자 → 미스터리 해결
• 매매 → 정보 수집 & 분석
• 도박 → 지적 탐구

🚀 다음 단계:
실제 시장에서 일어나는 사건들이 
자동으로 퍼즐이 됩니다.

매일 새로운 미스터리를 풀면서
진짜 투자 실력을 키워나가세요!

Welcome to the NEW Walk Risk! 🎮
            """.strip(),
            title="🌟 새로운 여정의 시작",
            border_style="bright_magenta"
        )
        self.console.print(final_panel)


async def main():
    """메인 함수"""
    demo = IntegratedTutorialDemo()
    await demo.run_integrated_demo()


if __name__ == "__main__":
    asyncio.run(main())