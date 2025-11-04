#!/usr/bin/env python3
"""Risk Puzzle Demo - 리스크 퍼즐 시스템 데모"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from datetime import datetime
from typing import List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from walk_risk.core.risk_puzzle.puzzle_engine import (
    PuzzleEngine, RiskPuzzle, PuzzleDifficulty, PuzzleType
)
from walk_risk.core.risk_puzzle.investigation import (
    InvestigationSystem, Clue, ClueType
)
from walk_risk.core.risk_puzzle.hypothesis import (
    Hypothesis, HypothesisValidator, HypothesisType, ActionType
)

console = Console()


class RiskPuzzleDemo:
    """리스크 퍼즐 게임 데모"""
    
    def __init__(self):
        self.console = console
        self.puzzle_engine = PuzzleEngine()
        self.investigation_system = InvestigationSystem(player_level=5)
        self.hypothesis_validator = HypothesisValidator()
        
        self.current_puzzle = None
        self.discovered_clues = []
        self.start_time = None
        
    def run(self):
        """데모 실행"""
        self._show_intro()
        
        # 샘플 퍼즐 생성
        self.current_puzzle = self._create_sample_puzzle()
        self.start_time = time.time()
        
        # 게임 루프
        while not self.current_puzzle.is_solved:
            self._show_puzzle_status()
            self._show_menu()
            
            choice = Prompt.ask(
                "\n[bold cyan]선택[/bold cyan]",
                choices=["1", "2", "3", "4", "5", "0"],
                default="1"
            )
            
            if choice == "1":
                self._investigate_clue()
            elif choice == "2":
                self._connect_clues()
            elif choice == "3":
                self._synthesize_clues()
            elif choice == "4":
                self._submit_hypothesis()
            elif choice == "5":
                self._show_help()
            elif choice == "0":
                if Confirm.ask("정말 종료하시겠습니까?"):
                    break
        
        if self.current_puzzle.is_solved:
            self._show_result()
    
    def _show_intro(self):
        """인트로 화면"""
        intro_panel = Panel(
            """
[bold yellow]🔍 Walk Risk: 리스크 퍼즐 시스템[/bold yellow]

투자는 퍼즐입니다. 
단서를 모으고, 가설을 세우고, 검증하세요.

[cyan]당신의 임무:[/cyan]
주가 급락의 진짜 이유를 찾아내고
올바른 투자 결정을 내리는 것입니다.

[dim]레벨 5 투자자 | 에너지: 12 | 조사 속도: 1.5x[/dim]
            """.strip(),
            title="🎮 리스크 퍼즐 게임",
            border_style="bright_blue"
        )
        self.console.print(intro_panel)
        
    def _create_sample_puzzle(self) -> RiskPuzzle:
        """샘플 퍼즐 생성"""
        market_event = {
            'symbol': '삼성전자',
            'change_percent': -8.5,
            'volume_ratio': 2.3,
            'market_sentiment': 'bearish',
            'time': '장중'
        }
        
        puzzle = self.puzzle_engine.create_puzzle(
            symbol='삼성전자',
            market_event=market_event,
            difficulty=PuzzleDifficulty.INTERMEDIATE
        )
        
        self.console.print(f"\n[red]❗ 긴급 상황 발생![/red]")
        self.console.print(Panel(
            puzzle.description,
            title=f"🔒 {puzzle.title}",
            border_style="red"
        ))
        
        return puzzle
    
    def _show_puzzle_status(self):
        """퍼즐 상태 표시"""
        self.console.clear()
        
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        
        status_table = Table(title="📊 퍼즐 진행 상황", box=None)
        status_table.add_column("항목", style="cyan")
        status_table.add_column("상태", style="white")
        
        status_table.add_row("대상", self.current_puzzle.target_symbol)
        status_table.add_row("난이도", self.current_puzzle.difficulty.value)
        status_table.add_row("경과 시간", f"{minutes:02d}:{seconds:02d}")
        status_table.add_row("에너지", f"{self.investigation_system.energy}/12")
        status_table.add_row("발견한 단서", f"{len(self.discovered_clues)}개")
        
        clue_progress = len(self.discovered_clues) / len(self.current_puzzle.available_clues)
        status_table.add_row("조사 진행도", f"{clue_progress:.0%}")
        
        self.console.print(status_table)
        
    def _show_menu(self):
        """메뉴 표시"""
        menu_text = """
[bold cyan]🎯 행동 선택[/bold cyan]

1. 🔍 단서 조사하기
2. 🔗 단서 연결하기
3. 🧩 단서 종합하기
4. 💡 가설 제출하기
5. ❓ 도움말
0. 🚪 종료
        """
        self.console.print(menu_text)
    
    def _investigate_clue(self):
        """단서 조사"""
        # 조사 가능한 단서 표시
        available = [c for c in self.current_puzzle.available_clues 
                    if not c.is_discovered]
        
        if not available:
            self.console.print("[yellow]모든 단서를 발견했습니다![/yellow]")
            return
        
        self.console.print("\n[bold]조사 가능한 단서 유형:[/bold]")
        
        clue_table = Table(box=None)
        clue_table.add_column("#", style="dim")
        clue_table.add_column("유형", style="cyan")
        clue_table.add_column("에너지", style="yellow")
        clue_table.add_column("시간", style="green")
        
        for i, clue in enumerate(available[:5], 1):  # 최대 5개만 표시
            clue_table.add_row(
                str(i),
                clue.clue_type.value,
                f"{clue.cost_energy}",
                f"{clue.cost_time}초"
            )
        
        self.console.print(clue_table)
        
        try:
            choice = int(Prompt.ask("조사할 단서 번호", default="1")) - 1
            if 0 <= choice < len(available):
                selected_clue = available[choice]
                
                # 조사 실행
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task(
                        f"[cyan]{selected_clue.clue_type.value} 조사 중...",
                        total=None
                    )
                    time.sleep(1)  # 시뮬레이션
                
                success, message, result = self.investigation_system.investigate(
                    selected_clue
                )
                
                if success:
                    self.discovered_clues.append(selected_clue)
                    
                    # 결과 표시
                    result_panel = Panel(
                        f"""
📄 {result['clue_content']}

💡 통찰: {', '.join(result['insights'])}
신뢰도: {result['reliability']:.0%}
                        """.strip(),
                        title=f"✅ {selected_clue.clue_type.value} 조사 완료",
                        border_style="green"
                    )
                    self.console.print(result_panel)
                    
                    # 보너스 통찰
                    if 'bonus_insight' in result:
                        self.console.print(f"[yellow]💎 {result['bonus_insight']}[/yellow]")
                else:
                    self.console.print(f"[red]❌ {message}[/red]")
                    
        except (ValueError, IndexError):
            self.console.print("[red]잘못된 선택입니다[/red]")
    
    def _connect_clues(self):
        """단서 연결"""
        if len(self.discovered_clues) < 2:
            self.console.print("[yellow]연결하려면 최소 2개의 단서가 필요합니다[/yellow]")
            return
        
        self.console.print("\n[bold]발견한 단서들:[/bold]")
        for i, clue in enumerate(self.discovered_clues, 1):
            self.console.print(f"{i}. [{clue.clue_type.value}] {clue.content[:50]}...")
        
        try:
            first = int(Prompt.ask("첫 번째 단서 번호")) - 1
            second = int(Prompt.ask("두 번째 단서 번호")) - 1
            
            if 0 <= first < len(self.discovered_clues) and \
               0 <= second < len(self.discovered_clues) and \
               first != second:
                
                connection = self.investigation_system.connect_clues(
                    self.discovered_clues[first],
                    self.discovered_clues[second]
                )
                
                if connection:
                    self.console.print(Panel(
                        connection,
                        title="🔗 단서 연결 성공",
                        border_style="cyan"
                    ))
                else:
                    self.console.print("[dim]연결점을 찾을 수 없습니다[/dim]")
        except (ValueError, IndexError):
            self.console.print("[red]잘못된 선택입니다[/red]")
    
    def _synthesize_clues(self):
        """단서 종합"""
        if not self.discovered_clues:
            self.console.print("[yellow]아직 발견한 단서가 없습니다[/yellow]")
            return
        
        synthesis = self.investigation_system.synthesize_clues(self.discovered_clues)
        
        synthesis_panel = Panel(
            f"""
📊 종합 분석

{synthesis['summary']}

신뢰도: {synthesis['confidence']:.0%}
단서 수: {synthesis['clue_count']}개
조사 범위: {synthesis['coverage']:.0%}

💡 권장사항: {synthesis['recommendation']}
            """.strip(),
            title="🧩 단서 종합",
            border_style="magenta"
        )
        
        self.console.print(synthesis_panel)
    
    def _submit_hypothesis(self):
        """가설 제출"""
        self.console.print("\n[bold yellow]💡 가설 수립[/bold yellow]\n")
        
        # 가설 입력
        statement = Prompt.ask("가설을 입력하세요")
        
        # 가설 타입 선택
        self.console.print("\n가설 유형:")
        self.console.print("1. 📈 상승 예상 (Bullish)")
        self.console.print("2. 📉 하락 예상 (Bearish)")
        self.console.print("3. ➡️ 횡보 예상 (Neutral)")
        self.console.print("4. 🔄 역발상 (Contrarian)")
        
        type_choice = Prompt.ask("선택", choices=["1", "2", "3", "4"], default="1")
        hypothesis_types = [
            HypothesisType.BULLISH,
            HypothesisType.BEARISH,
            HypothesisType.NEUTRAL,
            HypothesisType.CONTRARIAN
        ]
        hypothesis_type = hypothesis_types[int(type_choice) - 1]
        
        # 행동 선택
        self.console.print("\n권장 행동:")
        self.console.print("1. 💰 매수")
        self.console.print("2. 💸 매도")
        self.console.print("3. 🤲 보유")
        self.console.print("4. ⏳ 관망")
        
        action_choice = Prompt.ask("선택", choices=["1", "2", "3", "4"], default="4")
        actions = [ActionType.BUY, ActionType.SELL, ActionType.HOLD, ActionType.WAIT]
        recommended_action = actions[int(action_choice) - 1]
        
        # 확신도
        confidence = float(Prompt.ask("확신도 (0-100%)", default="50")) / 100
        
        # 가설 생성
        hypothesis = Hypothesis(
            hypothesis_id=f"hyp_{datetime.now().timestamp()}",
            puzzle_id=self.current_puzzle.puzzle_id,
            statement=statement,
            reasoning="플레이어의 분석",
            hypothesis_type=hypothesis_type,
            supporting_clues=[str(id(c)) for c in self.discovered_clues],
            contradicting_clues=[],
            confidence_level=confidence,
            predicted_outcome="플레이어 예측",
            time_horizon=7,
            recommended_action=recommended_action,
            position_size=10.0,
            stop_loss=-5.0,
            take_profit=10.0
        )
        
        # 검증
        self.console.print("\n[yellow]가설 검증 중...[/yellow]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]시장 시뮬레이션 실행 중...", total=None)
            time.sleep(2)  # 시뮬레이션
        
        # 검증 실행
        market_data = {
            'sentiment': 'bearish',
            'trend': 'down'
        }
        
        success, accuracy, feedback = self.hypothesis_validator.validate_hypothesis(
            hypothesis,
            market_data,
            self.discovered_clues
        )
        
        # 결과 표시
        self.console.print(Panel(
            feedback,
            title="📊 가설 검증 결과",
            border_style="green" if success else "red"
        ))
        
        # 퍼즐 완료
        elapsed_time = time.time() - self.start_time
        xp_earned, skill_gained = self.current_puzzle.calculate_reward(
            elapsed_time,
            accuracy
        )
        
        self.current_puzzle.is_solved = True
        self.current_puzzle.solve_time = elapsed_time
        self.current_puzzle.player_hypothesis = statement
        
        self.console.print(f"\n[green]✅ 퍼즐 해결![/green]")
        self.console.print(f"획득 경험치: {xp_earned} XP")
        self.console.print(f"획득 스킬: {skill_gained}")
    
    def _show_help(self):
        """도움말 표시"""
        help_panel = Panel(
            """
🎮 게임 방법

1. 단서 조사: 다양한 정보원에서 단서를 수집하세요
2. 단서 연결: 단서들 사이의 연관성을 찾으세요
3. 종합 분석: 전체 그림을 파악하세요
4. 가설 수립: 시장의 움직임을 예측하세요

💡 팁:
• 에너지를 효율적으로 사용하세요
• 신뢰도 높은 단서를 우선시하세요
• 모순되는 정보에 주의하세요
• 빠른 해결은 보너스를 줍니다
            """.strip(),
            title="❓ 도움말",
            border_style="blue"
        )
        self.console.print(help_panel)
    
    def _show_result(self):
        """최종 결과 표시"""
        if not self.current_puzzle.is_solved:
            return
        
        result_panel = Panel(
            f"""
🏆 퍼즐 완료!

📊 숨겨진 진실: {self.current_puzzle.hidden_truth}
💡 올바른 가설: {self.current_puzzle.correct_hypothesis}

⏱️ 소요 시간: {self.current_puzzle.solve_time:.0f}초
🎯 정확도: {self.current_puzzle.player_hypothesis}

🎓 배운 교훈:
리스크는 이해할 수 있는 퍼즐입니다.
단서를 모으고, 연결하고, 검증하면
불확실성을 기회로 바꿀 수 있습니다.
            """.strip(),
            title="🎊 게임 종료",
            border_style="gold1"
        )
        self.console.print(result_panel)


if __name__ == "__main__":
    demo = RiskPuzzleDemo()
    demo.run()