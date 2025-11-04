"""Tutorial CLI - 튜토리얼 사용자 인터페이스"""

import asyncio
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich import box
import time

from ..tutorials.tutorial_manager import TutorialManager, TutorialStage
from ..models.player.base import Player
from ..utils.logger import setup_logger

logger = setup_logger(__name__)
console = Console()


class TutorialCLI:
    """튜토리얼 사용자 인터페이스"""
    
    def __init__(self, tutorial_manager: TutorialManager):
        self.tutorial_manager = tutorial_manager
        self.console = console
        self.current_stage_data = None
        
    async def start_tutorial_flow(self, player: Player):
        """튜토리얼 흐름 시작"""
        self.console.clear()
        
        # 환영 화면
        self._display_welcome_screen()
        
        # 튜토리얼 시작 확인
        if not Confirm.ask(
            "\n[bold cyan]튜토리얼을 시작하시겠습니까?[/bold cyan]",
            default=True
        ):
            # 튜토리얼 건너뛰기
            result = await self.tutorial_manager.skip_tutorial(player)
            self._display_skip_message(result)
            return
            
        # 튜토리얼 메인 루프
        await self._run_tutorial_loop(player)
        
    def _display_welcome_screen(self):
        """환영 화면 표시"""
        welcome_text = """
[bold yellow]🎯 Walk Risk: 언락 리스크 마스터[/bold yellow]

[cyan]투자의 세계에 오신 것을 환영합니다![/cyan]

이 튜토리얼에서는:
• 🏛️ 워런 버핏과 함께 투자의 기초를 배웁니다
• 🔓 리스크를 기회로 바꾸는 방법을 익힙니다
• 💼 첫 포트폴리오를 구성해봅니다
• 📈 실시간 시장 시뮬레이션을 체험합니다
        """
        
        panel = Panel(
            welcome_text,
            title="🎆 WELCOME 🎆",
            border_style="bright_blue",
            box=box.DOUBLE
        )
        self.console.print(panel)
        
    async def _run_tutorial_loop(self, player: Player):
        """튜토리얼 메인 루프"""
        # 튜토리얼 시작
        result = await self.tutorial_manager.start_tutorial(player, "buffett")
        
        if not result["success"]:
            self.console.print(f"[red]❌ 튜토리얼 시작 실패: {result.get('error')}[/red]")
            return
            
        # 스테이지별 진행
        while True:
            progress = self.tutorial_manager.get_progress(player.id)
            if not progress:
                break
                
            # 현재 스테이지 표시
            await self._display_stage(progress.current_stage, result.get("data", {}))
            
            # 사용자 입력 대기
            if not await self._wait_for_user_action(player, progress.current_stage):
                break
                
            # 다음 스테이지로 진행
            result = await self.tutorial_manager.advance_stage(player)
            
            if result.get("completed"):
                # 튜토리얼 완료
                await self._display_completion(result)
                break
            elif not result["success"]:
                self.console.print(f"[red]❌ 오류: {result.get('error')}[/red]")
                break
                
    async def _display_stage(self, stage: TutorialStage, data: Dict[str, Any]):
        """스테이지 표시"""
        self.console.clear()
        self.current_stage_data = data
        
        # 스테이지별 표시 처리
        stage_displays = {
            TutorialStage.WELCOME: self._display_welcome_stage,
            TutorialStage.MENTOR_SELECTION: self._display_mentor_stage,
            TutorialStage.FIRST_RISK: self._display_first_risk_stage,
            TutorialStage.PORTFOLIO_BASICS: self._display_portfolio_stage,
            TutorialStage.MARKET_SIMULATION: self._display_simulation_stage,
            TutorialStage.GRADUATION: self._display_graduation_stage
        }
        
        display_func = stage_displays.get(stage)
        if display_func:
            await display_func(data)
            
    async def _display_welcome_stage(self, data: Dict[str, Any]):
        """환영 스테이지 표시"""
        # 버핏 멘토 메시지
        message_panel = Panel(
            data["message"],
            title="🏛️ 워런 버핏",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(message_panel)
        
        # 초기 자본금 표시
        self.console.print(f"\n💵 [bold]초기 자본금:[/bold] {data['initial_capital']:,}원")
        
        # 감정 상태 표시
        self._display_emotional_state(data["emotional_state"])
        
    async def _display_mentor_stage(self, data: Dict[str, Any]):
        """멘토 선택 스테이지 표시"""
        # 버핏 소개
        intro_panel = Panel(
            data["mentor_info"],
            title="🏛️ 멘토 소개",
            border_style="yellow",
            box=box.ROUNDED
        )
        self.console.print(intro_panel)
        
        # 다음 단계 안내
        self.console.print(f"\n[cyan]{data['next_step']}[/cyan]")
        
    async def _display_first_risk_stage(self, data: Dict[str, Any]):
        """첫 리스크 스테이지 표시"""
        # 리스크 소개
        risk_panel = Panel(
            data["risk_intro"],
            title="🔒 첫 번째 리스크",
            border_style="red",
            box=box.HEAVY
        )
        self.console.print(risk_panel)
        
        # 시장 역사 표시
        if "market_history" in data:
            history_table = Table(title="📊 시장 폭락 역사", box=box.SIMPLE)
            history_table.add_column("연도", style="cyan")
            history_table.add_column("하락률", style="red")
            history_table.add_column("회복 기간", style="green")
            history_table.add_column("교훈", style="yellow")
            
            for event in data["market_history"]:
                history_table.add_row(
                    event["year"],
                    event["drop"],
                    event["recovery"],
                    event["lesson"]
                )
                
            self.console.print(history_table)
            
        # 시뮬레이션 시나리오 표시
        if "simulation_scenario" in data:
            scenario = data["simulation_scenario"]
            sim_panel = Panel(
                f"""
📊 시뮬레이션 상황:
• 회사: {scenario['company']}
• 매수가: {scenario['buy_price']:,}원
• 현재가: {scenario['current_price']:,}원 ({scenario['loss_percent']:.1f}%)
• 평가손실: {scenario['loss']:,}원
                """,
                title="🚨 긴급 상황",
                border_style="bright_red"
            )
            self.console.print(sim_panel)
            
        # 버핏 조언
        if "buffett_advice" in data:
            self.console.print(f"\n{data['buffett_advice']}")
            
    async def _display_portfolio_stage(self, data: Dict[str, Any]):
        """포트폴리오 스테이지 표시"""
        # 포트폴리오 학습 내용
        lesson_panel = Panel(
            data["lesson"],
            title="💼 포트폴리오 기초",
            border_style="green",
            box=box.ROUNDED
        )
        self.console.print(lesson_panel)
        
        # 추천 포트폴리오
        if "recommended_portfolio" in data:
            portfolio_table = Table(title="📊 추천 포트폴리오", box=box.SIMPLE_HEAD)
            portfolio_table.add_column("종목", style="cyan")
            portfolio_table.add_column("업종", style="yellow")
            portfolio_table.add_column("비중", style="green")
            portfolio_table.add_column("이유", style="white")
            
            for asset in data["recommended_portfolio"]:
                portfolio_table.add_row(
                    asset["name"],
                    asset["sector"],
                    asset["allocation"],
                    asset["reason"]
                )
                
            self.console.print(portfolio_table)
            
        # 버핏 팁
        if "buffett_tip" in data:
            self.console.print(f"\n{data['buffett_tip']}")
            
    async def _display_simulation_stage(self, data: Dict[str, Any]):
        """시뮬레이션 스테이지 표시"""
        # 현재 이벤트
        current_event = data["current_event"]
        event_panel = Panel(
            f"""
📅 Day {current_event['day']}: {current_event['event']}
📈 시장 변화: {current_event['market_change']}
💼 포트폴리오 변화: {current_event['portfolio_change']}
            """,
            title="🎯 시장 상황",
            border_style="bright_yellow"
        )
        self.console.print(event_panel)
        
        # 포트폴리오 현황
        status = data["portfolio_status"]
        status_table = Table(title="💼 포트폴리오 현황", box=box.SIMPLE)
        status_table.add_column("항목", style="cyan")
        status_table.add_column("값", style="white")
        
        status_table.add_row("초기 자산", f"{status['initial_value']:,}원")
        status_table.add_row("현재 자산", f"{status['current_value']:,}원")
        status_table.add_row("수익률", f"{status['return_percent']:.1f}%")
        status_table.add_row(
            "최고 성과", 
            f"{status['best_performer']['name']} ({status['best_performer']['return']})"
        )
        status_table.add_row(
            "최저 성과", 
            f"{status['worst_performer']['name']} ({status['worst_performer']['return']})"
        )
        
        self.console.print(status_table)
        
        # 버핏 조언
        if "buffett_advice" in data:
            advice_panel = Panel(
                data["buffett_advice"],
                border_style="yellow",
                box=box.DOUBLE
            )
            self.console.print(advice_panel)
            
        # 선택지 표시
        if "choices" in data:
            self.console.print("\n[bold]선택하세요:[/bold]")
            for i, choice in enumerate(data["choices"], 1):
                self.console.print(f"{i}. {choice['label']}")
                
    async def _display_graduation_stage(self, data: Dict[str, Any]):
        """졸업 스테이지 표시"""
        # 졸업 메시지
        grad_panel = Panel(
            data["graduation_message"],
            title="🎆 축하합니다! 🎆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(grad_panel)
        
        # 최종 성과
        results = data["final_results"]
        results_table = Table(title="🏆 최종 성과", box=box.ROUNDED)
        results_table.add_column("항목", style="cyan")
        results_table.add_column("값", style="white")
        
        results_table.add_row("투자 수익률", f"+{results['return_percent']}%")
        results_table.add_row("해제한 리스크", f"{len(results['risks_unlocked'])}개")
        results_table.add_row("획듍 경험치", f"{results['experience_gained']} XP")
        
        self.console.print(results_table)
        
        # 보상
        rewards = data["rewards"]
        rewards_panel = Panel(
            f"""
🏆 획듍한 보상:
• 칭호: {rewards['title']}
• 배지: {rewards['badge']}
• 특별 아이템: {rewards['special_item']}
• 해제된 기능: {', '.join(rewards['unlock_features'])}
            """,
            title="🎁 보상",
            border_style="bright_yellow"
        )
        self.console.print(rewards_panel)
        
    def _display_emotional_state(self, emotions: Dict[str, int]):
        """감정 상태 표시"""
        emotion_panel = Panel(
            f"""
😎 자신감: {'■' * emotions['confidence']}{'□' * (10 - emotions['confidence'])} {emotions['confidence']}/10
😰 두려움: {'■' * emotions['fear']}{'□' * (10 - emotions['fear'])} {emotions['fear']}/10
🤑 탐욕: {'■' * emotions['greed']}{'□' * (10 - emotions['greed'])} {emotions['greed']}/10
⏳ 인내심: {'■' * emotions['patience']}{'□' * (10 - emotions['patience'])} {emotions['patience']}/10
            """,
            title="📊 감정 상태",
            border_style="blue"
        )
        self.console.print(emotion_panel)
        
    async def _wait_for_user_action(self, player: Player, stage: TutorialStage) -> bool:
        """사용자 입력 대기"""
        # 스테이지별 입력 처리
        if stage == TutorialStage.MARKET_SIMULATION and "choices" in self.current_stage_data:
            # 선택지가 있는 경우
            choice = Prompt.ask(
                "\n[bold]선택[/bold]",
                choices=[str(i) for i in range(1, len(self.current_stage_data["choices"]) + 1)],
                default="1"
            )
            
            # 선택 처리
            choice_id = self.current_stage_data["choices"][int(choice) - 1]["id"]
            tutorial = self.tutorial_manager.active_tutorials.get(player.id)
            
            if tutorial:
                result = await tutorial.handle_choice(
                    choice_id, 
                    self.current_stage_data
                )
                
                # 피드백 표시
                if "buffett_feedback" in result:
                    feedback_panel = Panel(
                        result["buffett_feedback"],
                        border_style="yellow"
                    )
                    self.console.print(feedback_panel)
                    
                # 감정 상태 업데이트 표시
                if "emotional_state" in result:
                    self._display_emotional_state(result["emotional_state"])
                    
        # 계속 진행 확인
        return Confirm.ask(
            "\n[bold cyan]계속하시겠습니까?[/bold cyan]",
            default=True
        )
        
    async def _display_completion(self, result: Dict[str, Any]):
        """튜토리얼 완료 표시"""
        # 완료 애니메이션
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("튜토리얼 완료 처리 중...", total=100)
            for i in range(100):
                progress.update(task, advance=1)
                time.sleep(0.01)
                
        # 완료 메시지
        completion_panel = Panel(
            f"""
🎉 튜토리얼을 성공적으로 완료하셨습니다!

획듍한 보상:
• 경험치: {result['rewards']['experience']} XP
• 칭호: {result['rewards']['title']}
• 해제된 기능: {', '.join(result['rewards']['unlock_features'])}

이제 실전 투자를 시작할 준비가 되었습니다!
            """,
            title="🏆 튜토리얼 완료 🏆",
            border_style="bright_green",
            box=box.DOUBLE
        )
        self.console.print(completion_panel)
        
        # 다음 단계 안내
        next_steps = [
            "1. 실전 포트폴리오 구성하기",
            "2. 고급 리스크 도전하기",
            "3. 커뮤니티 참여하기",
            "4. 다른 멘토 탐색하기"
        ]
        
        self.console.print("\n[bold cyan]다음 단계:[/bold cyan]")
        for step in next_steps:
            self.console.print(f"  {step}")
            
    def _display_skip_message(self, result: Dict[str, Any]):
        """튜토리얼 건너뛰기 메시지"""
        skip_panel = Panel(
            f"""
튜토리얼을 건너뛰었습니다.

기본 보상:
• 경험치: {result['rewards']['experience']} XP
• 해제된 기능: {', '.join(result['rewards']['unlock_features'])}

필요하면 언제든지 튜토리얼을 다시 시작할 수 있습니다.
            """,
            title="🚀 튜토리얼 건너뛰기",
            border_style="yellow"
        )
        self.console.print(skip_panel)