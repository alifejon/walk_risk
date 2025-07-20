"""
Command Line Interface for Walk Risk
"""
import asyncio
import click
from datetime import datetime
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
import json

from ..core.game_state.game_manager import GameManager, GameConfig, GameMode, GameState
from ..models.player.base import Player, PlayerClass
from ..models.risk.base import RiskLevel, RiskCategory
from ..utils.logger import logger

console = Console()


class WalkRiskCLI:
    """Command Line Interface for Walk Risk"""
    
    def __init__(self):
        self.game_manager: Optional[GameManager] = None
        self.current_player: Optional[Player] = None
        self.is_running = False
    
    async def initialize(self, config: GameConfig = None) -> bool:
        """Initialize the CLI and game manager"""
        try:
            console.print("[bold blue]🎮 언락: 리스크 마스터 초기화 중...[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                init_task = progress.add_task("게임 엔진 초기화...", total=None)
                
                self.game_manager = GameManager(config)
                success = await self.game_manager.initialize()
                
                progress.update(init_task, description="초기화 완료!")
            
            if success:
                console.print("[bold green]✅ 초기화 성공![/bold green]")
                self.is_running = True
                return True
            else:
                console.print("[bold red]❌ 초기화 실패![/bold red]")
                return False
                
        except Exception as e:
            console.print(f"[bold red]❌ 초기화 오류: {e}[/bold red]")
            return False
    
    async def run_main_menu(self) -> None:
        """Run the main menu loop"""
        while self.is_running:
            try:
                self._display_main_menu()
                choice = Prompt.ask("선택하세요", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])
                
                if choice == "1":
                    await self._login_or_create_player()
                elif choice == "2":
                    await self._show_risk_dashboard()
                elif choice == "3":
                    await self._start_risk_session()
                elif choice == "4":
                    await self._show_player_profile()
                elif choice == "5":
                    await self._show_market_data()
                elif choice == "6":
                    await self._show_game_statistics()
                elif choice == "7":
                    await self._show_settings()
                elif choice == "8":
                    await self._show_help()
                elif choice == "9":
                    await self._shutdown()
                    break
                
            except KeyboardInterrupt:
                if Confirm.ask("정말로 종료하시겠습니까?"):
                    await self._shutdown()
                    break
            except Exception as e:
                console.print(f"[bold red]오류 발생: {e}[/bold red]")
                logger.error(f"CLI 오류: {e}")
    
    def _display_main_menu(self) -> None:
        """Display main menu"""
        console.clear()
        
        # Header
        header = Panel.fit(
            "[bold cyan]🎮 언락: 리스크 마스터[/bold cyan]\n"
            "[italic]실시간 시장 데이터 기반 리스크 마스터리 게임[/italic]",
            border_style="cyan"
        )
        console.print(header)
        
        # Player info
        if self.current_player:
            player_info = (
                f"플레이어: [bold]{self.current_player.username}[/bold] | "
                f"레벨: [bold]{self.current_player.stats.level}[/bold] | "
                f"경험치: [bold]{self.current_player.stats.experience}[/bold] | "
                f"클래스: [bold]{self.current_player.player_class.value}[/bold]"
            )
            console.print(Panel(player_info, border_style="green"))
        
        # Game status
        if self.game_manager:
            status = (
                f"게임 상태: [bold]{self.game_manager.state.value}[/bold] | "
                f"모드: [bold]{self.game_manager.current_mode.value}[/bold] | "
                f"활성 리스크: [bold]{len(self.game_manager.global_risks)}[/bold]"
            )
            console.print(Panel(status, border_style="blue"))
        
        # Menu options
        menu = Table.grid(padding=1)
        menu.add_column(style="bold cyan", justify="right")
        menu.add_column(style="white")
        
        menu.add_row("1.", "로그인 / 플레이어 생성")
        menu.add_row("2.", "리스크 대시보드")
        menu.add_row("3.", "리스크 세션 시작")
        menu.add_row("4.", "플레이어 프로필")
        menu.add_row("5.", "시장 데이터")
        menu.add_row("6.", "게임 통계")
        menu.add_row("7.", "설정")
        menu.add_row("8.", "도움말")
        menu.add_row("9.", "종료")
        
        console.print(Panel(menu, title="메인 메뉴", border_style="white"))
    
    async def _login_or_create_player(self) -> None:
        """Login or create new player"""
        console.clear()
        console.print("[bold cyan]플레이어 로그인/생성[/bold cyan]")
        
        username = Prompt.ask("사용자명을 입력하세요")
        
        # Try to find existing player
        player = self.game_manager.get_player_by_username(username)
        
        if player:
            console.print(f"[green]기존 플레이어를 찾았습니다: {username}[/green]")
            self.current_player = player
            console.print(f"환영합니다, {player.username}님! (레벨 {player.stats.level})")
        else:
            console.print(f"[yellow]새 플레이어를 생성합니다: {username}[/yellow]")
            email = Prompt.ask("이메일 (선택사항)", default="")
            
            self.current_player = await self.game_manager.create_player(username, email)
            console.print(f"[green]플레이어 생성 완료! 환영합니다, {username}님![/green]")
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_risk_dashboard(self) -> None:
        """Show risk dashboard"""
        console.clear()
        console.print("[bold cyan]📊 리스크 대시보드[/bold cyan]")
        
        if not self.current_player:
            console.print("[red]먼저 로그인해주세요.[/red]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        # Get available risks
        risks = self.game_manager.get_available_risks(self.current_player.id)
        
        if not risks:
            console.print("[yellow]현재 이용 가능한 리스크가 없습니다.[/yellow]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        # Display risks table
        table = Table(title="이용 가능한 리스크")
        table.add_column("ID", style="cyan", width=8)
        table.add_column("이름", style="white")
        table.add_column("카테고리", style="blue")
        table.add_column("심각도", style="red")
        table.add_column("복잡도", style="yellow")
        table.add_column("레벨", style="green")
        
        for i, risk in enumerate(risks[:10]):  # Show top 10
            severity_bar = "█" * int(risk.severity * 10)
            complexity_bar = "█" * int(risk.complexity * 10)
            
            table.add_row(
                str(i + 1),
                risk.name[:30] + "..." if len(risk.name) > 30 else risk.name,
                risk.category.value,
                f"{risk.severity:.2f} {severity_bar}",
                f"{risk.complexity:.2f} {complexity_bar}",
                risk.level.value
            )
        
        console.print(table)
        
        # Risk details
        choice = Prompt.ask("리스크 상세 정보를 보시겠습니까? (번호 입력 또는 엔터)", default="")
        if choice.isdigit() and 1 <= int(choice) <= len(risks):
            risk = risks[int(choice) - 1]
            await self._show_risk_details(risk)
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_risk_details(self, risk) -> None:
        """Show detailed risk information"""
        console.print(f"\n[bold cyan]📋 리스크 상세 정보: {risk.name}[/bold cyan]")
        
        details = Table.grid(padding=1)
        details.add_column(style="bold cyan", justify="right")
        details.add_column(style="white")
        
        details.add_row("ID:", risk.id[:8] + "...")
        details.add_row("카테고리:", risk.category.value)
        details.add_row("레벨:", risk.level.value)
        details.add_row("심각도:", f"{risk.severity:.2f}")
        details.add_row("복잡도:", f"{risk.complexity:.2f}")
        details.add_row("빈도:", f"{risk.frequency:.2f}")
        details.add_row("생성 시간:", risk.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        
        if risk.metrics:
            details.add_row("변동성:", f"{risk.metrics.volatility:.2%}" if risk.metrics.volatility else "N/A")
            details.add_row("베타:", f"{risk.metrics.beta:.2f}" if risk.metrics.beta else "N/A")
            details.add_row("VaR(95%):", f"{risk.metrics.var_95:.2%}" if risk.metrics.var_95 else "N/A")
        
        console.print(Panel(details, title="리스크 정보", border_style="cyan"))
        
        console.print(f"\n[bold]설명:[/bold]\n{risk.description}")
        
        if risk.required_keys:
            console.print(f"\n[bold]필요 키:[/bold]")
            for key in risk.required_keys:
                console.print(f"  • {key.name} ({key.key_type})")
    
    async def _start_risk_session(self) -> None:
        """Start a risk analysis session"""
        console.clear()
        console.print("[bold cyan]🚀 리스크 세션 시작[/bold cyan]")
        
        if not self.current_player:
            console.print("[red]먼저 로그인해주세요.[/red]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        # Choose game mode
        console.print("\n게임 모드를 선택하세요:")
        console.print("1. 연습 모드 (Practice)")
        console.print("2. 실시간 모드 (Real-time)")
        console.print("3. 시뮬레이션 모드 (Simulation)")
        
        mode_choice = Prompt.ask("모드 선택", choices=["1", "2", "3"], default="1")
        
        mode_map = {
            "1": GameMode.PRACTICE,
            "2": GameMode.REAL_TIME,
            "3": GameMode.SIMULATION
        }
        
        mode = mode_map[mode_choice]
        
        # Start session
        session = await self.game_manager.start_session(self.current_player.id, mode)
        
        if session:
            console.print(f"[green]세션 시작: {session.id}[/green]")
            console.print(f"모드: {mode.value}")
            console.print(f"시작 시간: {session.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Session loop
            await self._run_risk_session(session.id)
        else:
            console.print("[red]세션 시작 실패[/red]")
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _run_risk_session(self, session_id: str) -> None:
        """Run risk session loop"""
        console.print("\n[bold green]리스크 세션 진행 중...[/bold green]")
        
        while True:
            console.print("\n세션 메뉴:")
            console.print("1. 이용 가능한 리스크 보기")
            console.print("2. 리스크 언락 시도")
            console.print("3. 세션 상태 확인")
            console.print("4. 세션 종료")
            
            choice = Prompt.ask("선택", choices=["1", "2", "3", "4"])
            
            if choice == "1":
                await self._show_risk_dashboard()
            elif choice == "2":
                await self._attempt_risk_unlock()
            elif choice == "3":
                await self._show_session_status(session_id)
            elif choice == "4":
                await self.game_manager.end_session(session_id)
                console.print("[green]세션이 종료되었습니다.[/green]")
                break
    
    async def _attempt_risk_unlock(self) -> None:
        """Attempt to unlock a risk"""
        risks = self.game_manager.get_available_risks(self.current_player.id)
        
        if not risks:
            console.print("[yellow]이용 가능한 리스크가 없습니다.[/yellow]")
            return
        
        # Show available risks
        console.print("\n언락 가능한 리스크:")
        for i, risk in enumerate(risks[:5]):
            console.print(f"{i + 1}. {risk.name} (심각도: {risk.severity:.2f})")
        
        choice = Prompt.ask("리스크 선택 (번호)", choices=[str(i) for i in range(1, min(6, len(risks) + 1))])
        selected_risk = risks[int(choice) - 1]
        
        # Show required keys
        if selected_risk.required_keys:
            console.print(f"\n필요한 키:")
            for key in selected_risk.required_keys:
                console.print(f"  • {key.name}")
            
            # For demo, assume player has all keys
            keys_used = [key.name for key in selected_risk.required_keys]
            
            success = await self.game_manager.unlock_risk(
                self.current_player.id,
                selected_risk.id,
                keys_used
            )
            
            if success:
                console.print(f"[bold green]🎉 리스크 언락 성공: {selected_risk.name}![/bold green]")
                console.print(f"경험치 획득: {int(selected_risk.severity * 100)}")
            else:
                console.print(f"[red]❌ 리스크 언락 실패[/red]")
        else:
            console.print("[yellow]이 리스크는 키가 필요하지 않습니다.[/yellow]")
    
    async def _show_session_status(self, session_id: str) -> None:
        """Show current session status"""
        session = self.game_manager.active_sessions.get(session_id)
        
        if not session:
            console.print("[red]세션을 찾을 수 없습니다.[/red]")
            return
        
        status = Table.grid(padding=1)
        status.add_column(style="bold cyan", justify="right")
        status.add_column(style="white")
        
        status.add_row("세션 ID:", session.id[:8] + "...")
        status.add_row("모드:", session.mode.value)
        status.add_row("시작 시간:", session.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        status.add_row("진행 시간:", str(session.duration()))
        status.add_row("조우한 리스크:", str(len(session.risks_encountered)))
        status.add_row("언락한 리스크:", str(len(session.risks_unlocked)))
        status.add_row("획득 경험치:", str(session.experience_gained))
        
        console.print(Panel(status, title="세션 상태", border_style="green"))
    
    async def _show_player_profile(self) -> None:
        """Show player profile"""
        console.clear()
        console.print("[bold cyan]👤 플레이어 프로필[/bold cyan]")
        
        if not self.current_player:
            console.print("[red]먼저 로그인해주세요.[/red]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        player = self.current_player
        
        # Player info
        info = Table.grid(padding=1)
        info.add_column(style="bold cyan", justify="right")
        info.add_column(style="white")
        
        info.add_row("사용자명:", player.username)
        info.add_row("이메일:", player.email or "N/A")
        info.add_row("클래스:", player.player_class.value)
        info.add_row("레벨:", str(player.stats.level))
        info.add_row("경험치:", str(player.stats.experience))
        info.add_row("언락한 리스크:", str(player.stats.total_risks_unlocked))
        info.add_row("마스터한 리스크:", str(player.stats.total_risks_mastered))
        info.add_row("성공한 예측:", str(player.stats.successful_predictions))
        info.add_row("실패한 예측:", str(player.stats.failed_predictions))
        info.add_row("정확도:", f"{player.stats.calculate_accuracy():.2%}")
        info.add_row("가입일:", player.created_at.strftime("%Y-%m-%d"))
        info.add_row("마지막 활동:", player.last_active.strftime("%Y-%m-%d %H:%M:%S"))
        
        console.print(Panel(info, title="플레이어 정보", border_style="green"))
        
        # Skills
        if player.unlocked_skills:
            console.print(f"\n[bold]언락된 스킬:[/bold]")
            for skill_id, level in player.unlocked_skills.items():
                console.print(f"  • {skill_id}: 레벨 {level}")
        
        # Keys
        if player.owned_keys:
            console.print(f"\n[bold]보유 키:[/bold]")
            for key in player.owned_keys:
                console.print(f"  • {key.name} ({key.key_type})")
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_market_data(self) -> None:
        """Show market data"""
        console.clear()
        console.print("[bold cyan]📈 시장 데이터[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("시장 데이터 로딩...", total=None)
            
            # Get market indices
            indices = await self.game_manager.data_manager.get_market_indices()
            
            progress.update(task, description="데이터 로드 완료!")
        
        if not indices:
            console.print("[yellow]시장 데이터를 가져올 수 없습니다.[/yellow]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        # Display market data
        table = Table(title="주요 시장 지수")
        table.add_column("지수", style="cyan")
        table.add_column("심볼", style="blue")
        table.add_column("가격", style="white")
        table.add_column("변동성", style="red")
        table.add_column("거래량", style="yellow")
        table.add_column("시간", style="green")
        
        for name, data in indices.items():
            table.add_row(
                name,
                data.symbol,
                f"{data.price:.2f}",
                f"{data.volatility:.2%}" if data.volatility else "N/A",
                f"{data.volume:,}" if data.volume else "N/A",
                data.timestamp.strftime("%H:%M:%S")
            )
        
        console.print(table)
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_game_statistics(self) -> None:
        """Show game statistics"""
        console.clear()
        console.print("[bold cyan]📊 게임 통계[/bold cyan]")
        
        stats = self.game_manager.get_game_statistics()
        
        # System stats
        system_table = Table(title="시스템 정보")
        system_table.add_column("항목", style="cyan")
        system_table.add_column("값", style="white")
        
        system_table.add_row("게임 상태", stats['system']['state'])
        system_table.add_row("게임 모드", stats['system']['mode'])
        system_table.add_row("가동 시간", stats['system']['uptime_formatted'])
        
        console.print(system_table)
        
        # Player stats
        player_table = Table(title="플레이어 통계")
        player_table.add_column("항목", style="cyan")
        player_table.add_column("값", style="white")
        
        player_table.add_row("총 플레이어", str(stats['players']['total']))
        player_table.add_row("활성 플레이어 (24h)", str(stats['players']['active_24h']))
        player_table.add_row("평균 레벨", f"{stats['players']['average_level']:.1f}")
        player_table.add_row("최고 레벨", str(stats['players']['max_level']))
        
        console.print(player_table)
        
        # Risk stats
        risk_table = Table(title="리스크 통계")
        risk_table.add_column("항목", style="cyan")
        risk_table.add_column("값", style="white")
        
        risk_table.add_row("생성된 리스크", str(stats['risks']['total_created']))
        risk_table.add_row("언락된 리스크", str(stats['risks']['total_unlocked']))
        risk_table.add_row("활성 리스크", str(stats['risks']['active']))
        risk_table.add_row("평균 심각도", f"{stats['risks']['average_severity']:.2f}")
        
        console.print(risk_table)
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_settings(self) -> None:
        """Show and modify settings"""
        console.clear()
        console.print("[bold cyan]⚙️ 설정[/bold cyan]")
        
        if not self.game_manager:
            console.print("[red]게임 매니저가 초기화되지 않았습니다.[/red]")
            Prompt.ask("계속하려면 Enter를 누르세요")
            return
        
        config = self.game_manager.config
        
        settings_table = Table(title="현재 설정")
        settings_table.add_column("설정", style="cyan")
        settings_table.add_column("값", style="white")
        
        settings_table.add_row("자동 저장 간격", f"{config.auto_save_interval}초")
        settings_table.add_row("최대 동시 리스크", str(config.max_concurrent_risks))
        settings_table.add_row("경험치 배수", f"{config.experience_multiplier}x")
        settings_table.add_row("난이도 스케일링", f"{config.difficulty_scaling}x")
        settings_table.add_row("튜토리얼 활성화", "예" if config.tutorial_enabled else "아니오")
        settings_table.add_row("실시간 모드", "예" if config.real_time_mode else "아니오")
        settings_table.add_row("데이터 소스", ", ".join(config.data_sources))
        
        console.print(settings_table)
        
        if Confirm.ask("설정을 변경하시겠습니까?"):
            # Simple setting modification
            console.print("\n변경 가능한 설정:")
            console.print("1. 경험치 배수")
            console.print("2. 실시간 모드 토글")
            
            choice = Prompt.ask("변경할 설정", choices=["1", "2"], default="")
            
            if choice == "1":
                new_multiplier = Prompt.ask("새 경험치 배수", default=str(config.experience_multiplier))
                try:
                    config.experience_multiplier = float(new_multiplier)
                    console.print(f"[green]경험치 배수를 {new_multiplier}로 변경했습니다.[/green]")
                except ValueError:
                    console.print("[red]유효하지 않은 값입니다.[/red]")
            elif choice == "2":
                config.real_time_mode = not config.real_time_mode
                console.print(f"[green]실시간 모드: {'활성화' if config.real_time_mode else '비활성화'}[/green]")
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _show_help(self) -> None:
        """Show help information"""
        console.clear()
        console.print("[bold cyan]❓ 도움말[/bold cyan]")
        
        help_content = """
[bold]언락: 리스크 마스터 게임 가이드[/bold]

[bold cyan]게임 개요:[/bold cyan]
이 게임은 실시간 금융 시장 데이터를 기반으로 리스크 관리 기술을 학습하는 게임입니다.

[bold cyan]주요 개념:[/bold cyan]
• [bold]리스크[/bold]: 시장에서 발생하는 다양한 위험 요소
• [bold]언락[/bold]: 리스크를 이해하고 대처 방법을 학습하는 과정
• [bold]키[/bold]: 리스크를 언락하는 데 필요한 지식, 경험, 지혜
• [bold]레벨[/bold]: 플레이어의 리스크 마스터리 수준

[bold cyan]리스크 레벨:[/bold cyan]
• 🔒 [red]Locked[/red]: 아직 이해하지 못한 리스크
• 🔓 [yellow]Unlocking[/yellow]: 분석 중인 리스크
• 🔑 [green]Unlocked[/green]: 정복한 리스크
• 💎 [cyan]Mastered[/cyan]: 기회로 전환한 리스크

[bold cyan]리스크 카테고리:[/bold cyan]
• [blue]Market[/blue]: 시장 리스크 (변동성, 상관관계 등)
• [green]Credit[/green]: 신용 리스크 (채무불이행 등)
• [yellow]Operational[/yellow]: 운영 리스크 (시스템 장애 등)
• [red]Strategic[/red]: 전략적 리스크 (규제 변화 등)
• [cyan]Liquidity[/cyan]: 유동성 리스크 (거래량 부족 등)

[bold cyan]게임 모드:[/bold cyan]
• [green]Practice[/green]: 연습 모드 (시뮬레이션 데이터)
• [red]Real-time[/red]: 실시간 모드 (실제 시장 데이터)
• [blue]Simulation[/blue]: 시뮬레이션 모드 (가상 시나리오)

[bold cyan]조작법:[/bold cyan]
• 메인 메뉴에서 숫자 키로 선택
• Enter: 확인
• Ctrl+C: 중단/종료
        """
        
        console.print(Panel(help_content, border_style="white"))
        
        Prompt.ask("계속하려면 Enter를 누르세요")
    
    async def _shutdown(self) -> None:
        """Shutdown the CLI and game manager"""
        console.print("[bold yellow]🔄 종료 중...[/bold yellow]")
        
        if self.game_manager:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                shutdown_task = progress.add_task("게임 데이터 저장 중...", total=None)
                
                await self.game_manager.shutdown()
                
                progress.update(shutdown_task, description="종료 완료!")
        
        self.is_running = False
        console.print("[bold green]👋 안전하게 종료되었습니다. 또 만나요![/bold green]")


# CLI Commands
@click.group()
def cli():
    """언락: 리스크 마스터 - 실시간 시장 데이터 기반 리스크 마스터리 게임"""
    pass


@cli.command()
@click.option('--demo', is_flag=True, help='데모 모드로 실행')
@click.option('--real-time', is_flag=True, help='실시간 모드 활성화')
@click.option('--config', type=click.Path(), help='설정 파일 경로')
def start(demo: bool, real_time: bool, config: Optional[str]):
    """게임 시작"""
    async def run_game():
        # Load config
        game_config = GameConfig()
        
        if demo:
            game_config.data_sources = ["demo"]
            game_config.real_time_mode = False
        elif real_time:
            game_config.data_sources = ["yahoo", "demo"]
            game_config.real_time_mode = True
        
        if config:
            try:
                with open(config, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(game_config, key):
                            setattr(game_config, key, value)
            except Exception as e:
                console.print(f"[red]설정 파일 로드 실패: {e}[/red]")
        
        # Start CLI
        cli_app = WalkRiskCLI()
        
        if await cli_app.initialize(game_config):
            await cli_app.run_main_menu()
        else:
            console.print("[red]게임 초기화 실패[/red]")
    
    asyncio.run(run_game())


@cli.command()
def version():
    """버전 정보 표시"""
    console.print("[bold cyan]언락: 리스크 마스터 v0.1.0[/bold cyan]")
    console.print("실시간 시장 데이터 기반 리스크 마스터리 게임")


if __name__ == "__main__":
    cli()