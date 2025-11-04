#!/usr/bin/env python3
"""Risk Puzzle Auto Demo - 리스크 퍼즐 시스템 자동 데모"""

import asyncio
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from datetime import datetime
import random

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


class RiskPuzzleAutoDemo:
    """리스크 퍼즐 게임 자동 데모"""
    
    def __init__(self):
        self.console = console
        self.puzzle_engine = PuzzleEngine()
        self.investigation_system = InvestigationSystem(player_level=5)
        self.hypothesis_validator = HypothesisValidator()
        
        self.current_puzzle = None
        self.discovered_clues = []
        self.start_time = None
        
    def run(self):
        """자동 데모 실행"""
        self._show_intro()
        
        # 샘플 퍼즐 생성
        self.console.print("\n[bold yellow]📍 1단계: 리스크 발견[/bold yellow]")
        self.current_puzzle = self._create_sample_puzzle()
        self.start_time = time.time()
        
        # 자동 플레이 시나리오
        self.console.print("\n[bold yellow]📍 2단계: 단서 조사[/bold yellow]")
        self._auto_investigate()
        
        self.console.print("\n[bold yellow]📍 3단계: 단서 연결[/bold yellow]")
        self._auto_connect_clues()
        
        self.console.print("\n[bold yellow]📍 4단계: 단서 종합[/bold yellow]")
        self._auto_synthesize()
        
        self.console.print("\n[bold yellow]📍 5단계: 가설 수립 및 검증[/bold yellow]")
        self._auto_submit_hypothesis()
        
        self.console.print("\n[bold yellow]📍 6단계: 결과 및 학습[/bold yellow]")
        self._show_final_result()
    
    def _show_intro(self):
        """인트로 화면"""
        intro_panel = Panel(
            """
[bold yellow]🔍 Walk Risk: 리스크 퍼즐 시스템[/bold yellow]
[bold cyan]자동 데모 모드[/bold cyan]

이것이 새로운 게임의 핵심입니다:
투자는 단순 매매가 아닌 [bold]"퍼즐 풀기"[/bold]입니다.

[cyan]데모 시나리오:[/cyan]
삼성전자가 갑자기 -8.5% 폭락했습니다.
왜일까요? 단서를 찾고 진실을 밝혀내세요!

[dim]플레이어: 레벨 5 | 에너지: 12 | 조사 속도: 1.5x[/dim]
            """.strip(),
            title="🎮 리스크 퍼즐 게임",
            border_style="bright_blue"
        )
        self.console.print(intro_panel)
        time.sleep(2)
        
    def _create_sample_puzzle(self) -> RiskPuzzle:
        """샘플 퍼즐 생성"""
        market_event = {
            'symbol': '삼성전자',
            'change_percent': -8.5,
            'volume_ratio': 2.3,
            'market_sentiment': 'bearish',
            'time': '장중',
            'sector_divergence': True
        }
        
        puzzle = self.puzzle_engine.create_puzzle(
            symbol='삼성전자',
            market_event=market_event,
            difficulty=PuzzleDifficulty.INTERMEDIATE
        )
        
        self.console.print(f"\n[red]❗ 긴급 상황 발생![/red]")
        self.console.print(Panel(
            f"""
{puzzle.description}

[yellow]숨겨진 진실:[/yellow] [dim](플레이어는 모름)[/dim]
"{puzzle.hidden_truth}"

[yellow]정답 가설:[/yellow] [dim](플레이어는 모름)[/dim]
"{puzzle.correct_hypothesis}"
            """.strip(),
            title=f"🔒 {puzzle.title}",
            border_style="red"
        ))
        
        time.sleep(2)
        return puzzle
    
    def _auto_investigate(self):
        """자동 단서 조사"""
        self.console.print("\n🔍 단서 조사를 시작합니다...")
        time.sleep(1)
        
        # 3개의 단서를 자동으로 조사
        available = [c for c in self.current_puzzle.available_clues 
                    if not c.is_discovered]
        
        for i, clue in enumerate(available[:3], 1):
            self.console.print(f"\n[cyan]단서 {i}: {clue.clue_type.value} 조사 중...[/cyan]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task(
                    f"[cyan]{clue.clue_type.value} 데이터 수집...",
                    total=None
                )
                time.sleep(1)
            
            # 조사 실행
            success, message, result = self.investigation_system.investigate(clue)
            
            if success:
                self.discovered_clues.append(clue)
                
                # 결과 표시
                result_panel = Panel(
                    f"""
📄 {result['clue_content']}

💡 {result['insights'][0]}
신뢰도: {result['reliability']:.0%}
                    """.strip(),
                    title=f"✅ 단서 {i} 발견",
                    border_style="green"
                )
                self.console.print(result_panel)
                time.sleep(1)
        
        # 현재 상태 표시
        self.console.print(f"\n[green]✅ {len(self.discovered_clues)}개 단서 수집 완료[/green]")
        self.console.print(f"남은 에너지: {self.investigation_system.energy}/12")
    
    def _auto_connect_clues(self):
        """자동 단서 연결"""
        if len(self.discovered_clues) < 2:
            return
        
        self.console.print("\n🔗 단서들 사이의 연관성을 찾는 중...")
        time.sleep(1)
        
        # 첫 두 단서 연결
        clue1 = self.discovered_clues[0]
        clue2 = self.discovered_clues[1]
        
        self.console.print(f"[cyan]'{clue1.clue_type.value}'와 '{clue2.clue_type.value}' 연결 시도...[/cyan]")
        
        connection = self.investigation_system.connect_clues(clue1, clue2)
        
        if connection:
            self.console.print(Panel(
                connection,
                title="🔗 연결 성공!",
                border_style="cyan"
            ))
        else:
            self.console.print("[dim]직접적인 연결점을 찾지 못했습니다[/dim]")
        
        time.sleep(1)
    
    def _auto_synthesize(self):
        """자동 단서 종합"""
        self.console.print("\n🧩 발견한 모든 단서를 종합 분석 중...")
        time.sleep(1)
        
        synthesis = self.investigation_system.synthesize_clues(self.discovered_clues)
        
        synthesis_panel = Panel(
            f"""
📊 종합 분석 결과

{synthesis['summary']}

• 신뢰도: {synthesis['confidence']:.0%}
• 수집한 단서: {synthesis['clue_count']}개
• 조사 범위: {synthesis['coverage']:.0%}

💡 AI 추천: {synthesis['recommendation']}
            """.strip(),
            title="🧩 단서 종합 완료",
            border_style="magenta"
        )
        
        self.console.print(synthesis_panel)
        time.sleep(2)
    
    def _auto_submit_hypothesis(self):
        """자동 가설 제출"""
        self.console.print("\n💡 수집한 단서를 바탕으로 가설을 세웁니다...")
        time.sleep(1)
        
        # 플레이어의 가설 (약간 틀린 버전)
        player_statement = "삼성전자 하락은 반도체 업종 전체 조정으로 인한 일시적 과매도"
        player_hypothesis_type = HypothesisType.BULLISH
        player_action = ActionType.BUY
        player_confidence = 0.7
        
        self.console.print(Panel(
            f"""
🎯 플레이어의 가설:
"{player_statement}"

• 예상: {player_hypothesis_type.value} (상승)
• 행동: {player_action.value} (매수)
• 확신도: {player_confidence:.0%}
• 포지션: 10% 
• 손절: -5% / 익절: +10%
            """.strip(),
            title="💭 가설 수립",
            border_style="yellow"
        ))
        
        time.sleep(2)
        
        # 가설 생성
        hypothesis = Hypothesis(
            hypothesis_id=f"hyp_{datetime.now().timestamp()}",
            puzzle_id=self.current_puzzle.puzzle_id,
            statement=player_statement,
            reasoning="업종 전체 하락 + 펀더멘털 양호",
            hypothesis_type=player_hypothesis_type,
            supporting_clues=[str(id(c)) for c in self.discovered_clues],
            contradicting_clues=[],
            confidence_level=player_confidence,
            predicted_outcome="1주 내 5% 반등",
            time_horizon=7,
            recommended_action=player_action,
            position_size=10.0,
            stop_loss=-5.0,
            take_profit=10.0
        )
        
        # 검증
        self.console.print("\n[yellow]🔬 가설 검증 중...[/yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]시장 시뮬레이션 실행 중...", total=None)
            time.sleep(2)
        
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
            border_style="green" if success else "yellow"
        ))
        
        # 퍼즐 완료
        elapsed_time = time.time() - self.start_time
        xp_earned, skill_gained = self.current_puzzle.calculate_reward(
            elapsed_time,
            accuracy
        )
        
        self.current_puzzle.is_solved = True
        self.current_puzzle.solve_time = elapsed_time
        self.current_puzzle.player_hypothesis = player_statement
        
        time.sleep(2)
        
        self.console.print(f"\n[green]✅ 퍼즐 해결![/green]")
        self.console.print(f"• 획득 경험치: [yellow]{xp_earned} XP[/yellow]")
        self.console.print(f"• 획득 스킬: [cyan]{skill_gained}[/cyan]")
        self.console.print(f"• 정확도: [{'green' if accuracy > 0.6 else 'yellow'}]{accuracy:.0%}[/]")
    
    def _show_final_result(self):
        """최종 결과 및 교훈"""
        result_panel = Panel(
            f"""
🏆 퍼즐 완료!

[bold]숨겨진 진실:[/bold]
"{self.current_puzzle.hidden_truth}"

[bold]올바른 판단:[/bold]
"{self.current_puzzle.correct_hypothesis}"

[bold]플레이어의 가설:[/bold]
"{self.current_puzzle.player_hypothesis}"

⏱️ 소요 시간: {self.current_puzzle.solve_time:.0f}초

[bold yellow]🎓 핵심 교훈:[/bold yellow]
투자는 정보를 수집하고, 연결하고, 검증하는 과정입니다.
단순히 차트를 보고 매매하는 것이 아니라,
"왜?"라는 질문에 답을 찾는 것이 진정한 투자입니다.

[bold cyan]💡 이것이 "투자의 길을 걷는다"는 의미입니다.[/bold cyan]
            """.strip(),
            title="🎊 데모 완료",
            border_style="gold1"
        )
        self.console.print(result_panel)
        
        # 게임 차별화 포인트
        self.console.print("\n" + "="*60)
        self.console.print(Panel(
            """
[bold yellow]🎮 이 게임의 핵심 차별점:[/bold yellow]

1️⃣ [bold]매매가 아닌 "조사"가 게임플레이[/bold]
   - 단서 수집에 에너지 소모
   - 레벨업으로 더 많은 조사 도구 해금
   
2️⃣ [bold]리스크 = 풀어야 할 퍼즐[/bold]
   - 각 시장 이벤트가 하나의 퀘스트
   - 숨겨진 진실을 찾는 탐정 게임
   
3️⃣ [bold]실패해도 배우는 시스템[/bold]
   - 틀려도 구체적인 피드백 제공
   - 경험치는 항상 획득 (정확도에 따라 차등)
   
4️⃣ [bold]점진적 성장 경로[/bold]
   - Lv1: 뉴스만 → Lv30: 모든 조사 도구
   - 초급 퍼즐 → 마스터 퍼즐로 진화

[bold cyan]"이제 플레이어는 진짜로 투자를 '배웁니다'"[/bold cyan]
            """.strip(),
            title="🚀 Walk Risk: 투자 퍼즐 게임",
            border_style="bright_magenta"
        ))


if __name__ == "__main__":
    demo = RiskPuzzleAutoDemo()
    demo.run()
    
    print("\n" + "🎯"*30)
    print("\n🎮 자동 데모가 완료되었습니다!")
    print("실제 게임에서는 플레이어가 직접 단서를 선택하고 가설을 세웁니다.\n")