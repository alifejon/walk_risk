"""실시간 퍼즐 생성 시스템 데모 - 라이브 시장 데이터로 자동 퍼즐 생성"""

import asyncio
import time
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich import box

from walk_risk.core.auto_puzzle_manager import auto_puzzle_manager
from walk_risk.data.market_data.market_event_detector import market_event_detector
from walk_risk.core.game_state.game_manager import GameManager
from walk_risk.models.player.base import Player
from walk_risk.ai.mentor_personas import BuffettPersona

console = Console()


async def demonstrate_real_time_puzzle_system():
    """실시간 퍼즐 시스템 전체 데모"""
    
    console.print(Panel.fit(
        "🔥 Walk Risk 실시간 퍼즐 생성 시스템 데모",
        style="bold red"
    ))
    
    # 시스템 초기화
    console.print("\n🚀 시스템 초기화 중...")
    
    game_manager = GameManager()
    player = Player(
        id="demo_player",
        name="퍼즐 마스터",
        level=15  # 모든 조사 도구 사용 가능
    )
    
    buffett = BuffettPersona()
    
    console.print("✅ 게임 매니저 준비 완료")
    console.print("✅ 플레이어 생성 완료")
    console.print("✅ 버핏 멘토 준비 완료")
    
    await asyncio.sleep(1)
    
    # 1단계: 현재 활성 퍼즐 확인
    await show_current_puzzles()
    
    # 2단계: 실시간 이벤트 감지 시뮬레이션
    await simulate_market_monitoring()
    
    # 3단계: 강제 이벤트 감지 및 퍼즐 생성
    await force_puzzle_generation()
    
    # 4단계: 새로 생성된 퍼즐 체험
    await experience_new_puzzle(player, buffett)
    
    # 5단계: 자동 관리 시스템 데모
    await demonstrate_auto_management()


async def show_current_puzzles():
    """현재 활성 퍼즐 표시"""
    console.print(Panel.fit(
        "📊 1단계: 현재 활성 퍼즐 확인",
        style="bold blue"
    ))
    
    active_puzzles = auto_puzzle_manager.get_active_puzzles()
    
    if not active_puzzles:
        console.print("🔍 현재 활성화된 퍼즐이 없습니다.")
        console.print("💡 실시간 시장 이벤트를 감지하여 새로운 퍼즐을 생성하겠습니다.")
    else:
        table = Table(title="현재 활성 퍼즐 목록")
        table.add_column("제목", style="cyan")
        table.add_column("신선도", style="green")
        table.add_column("난이도", style="yellow")
        table.add_column("종목", style="magenta")
        
        for live_puzzle in active_puzzles:
            freshness = f"{live_puzzle.get_freshness_score():.1%}"
            table.add_row(
                live_puzzle.puzzle.title,
                freshness,
                live_puzzle.puzzle.difficulty.value,
                live_puzzle.source_event.symbol
            )
        
        console.print(table)
    
    await asyncio.sleep(2)


async def simulate_market_monitoring():
    """시장 모니터링 시뮬레이션"""
    console.print(Panel.fit(
        "📡 2단계: 실시간 시장 모니터링",
        style="bold blue"
    ))
    
    console.print("🔄 15개 한국 주식을 실시간 모니터링 중...")
    console.print("📈 급락(-5% 이상), 급등(+5% 이상), 거래량 급증(2.5배 이상) 감지")
    
    # 모니터링 시뮬레이션 - 실제로는 5분마다 실행
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        monitor_task = progress.add_task(
            description="시장 데이터 분석 중...", 
            total=100
        )
        
        monitoring_stocks = [
            "삼성전자", "SK하이닉스", "NAVER", "카카오", "현대차",
            "기아", "LG화학", "셀트리온", "포스코홀딩스", "삼성SDI"
        ]
        
        for i, stock in enumerate(monitoring_stocks):
            progress.update(monitor_task, advance=10)
            console.print(f"  📊 {stock} 분석 중...")
            await asyncio.sleep(0.3)
    
    console.print("✅ 시장 스캔 완료")
    await asyncio.sleep(1)


async def force_puzzle_generation():
    """강제 퍼즐 생성 데모"""
    console.print(Panel.fit(
        "⚡ 3단계: 실시간 이벤트 감지 및 퍼즐 생성",
        style="bold blue"
    ))
    
    console.print("🚨 강제 이벤트 감지 실행...")
    
    # 실제 시장 데이터로 이벤트 감지 및 퍼즐 생성
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        detection_task = progress.add_task(
            description="Yahoo Finance API로 실시간 데이터 수집...", 
            total=100
        )
        
        # 실제 이벤트 감지 실행
        progress.update(detection_task, advance=30)
        console.print("📡 Yahoo Finance 연결...")
        
        progress.update(detection_task, advance=30)
        console.print("📊 주가 데이터 분석...")
        
        progress.update(detection_task, advance=20)
        console.print("🔍 이벤트 패턴 감지...")
        
        progress.update(detection_task, advance=20)
        console.print("🎯 퍼즐 생성...")
        
        # 실제 이벤트 감지 및 퍼즐 생성
        new_puzzles = await auto_puzzle_manager.force_detection_cycle()
        
    if new_puzzles:
        console.print(f"🎉 {len(new_puzzles)}개의 새로운 퍼즐이 생성되었습니다!")
        
        for live_puzzle in new_puzzles:
            event = live_puzzle.source_event
            console.print(f"""
📍 새 퍼즐 발견!
  🏢 종목: {event.company_name}
  📈 변동: {event.change_percent:+.1f}%
  📊 거래량: 평소 대비 {event.volume_ratio:.1f}배
  🔥 심각도: {event.severity.upper()}
  ⏰ 감지 시간: {event.detected_at.strftime('%H:%M:%S')}
            """)
    else:
        console.print("⚠️  현재 시장에서 퍼즐 생성에 적합한 이벤트를 찾지 못했습니다.")
        console.print("💡 실제 거래 시간에는 더 많은 이벤트가 감지됩니다.")
        
        # 데모용 가상 퍼즐 생성
        console.print("\n🎭 데모를 위해 가상 시나리오를 생성합니다...")
        await create_demo_puzzle()
    
    await asyncio.sleep(2)


async def create_demo_puzzle():
    """데모용 가상 퍼즐 생성"""
    from walk_risk.core.risk_puzzle.puzzle_engine import PuzzleEngine, PuzzleDifficulty
    from walk_risk.data.market_data.market_event_detector import MarketEvent, EventType
    from datetime import datetime
    
    # 가상 이벤트 생성
    demo_event = MarketEvent(
        event_id="DEMO_005930_20250803_1430",
        event_type=EventType.SHARP_DROP,
        symbol="005930.KS",
        company_name="삼성전자",
        trigger_price=71500,
        change_percent=-6.8,
        volume_ratio=3.2,
        market_sentiment="bearish",
        sector_performance={"반도체": -4.2, "전자부품": -3.1},
        peer_comparison={"000660.KS": -5.1, "006400.KS": -4.8},
        severity="high",
        puzzle_worthiness=0.85
    )
    
    # 퍼즐 생성
    puzzle_engine = PuzzleEngine()
    puzzle = await market_event_detector.create_puzzle_from_event(demo_event)
    
    if puzzle:
        await auto_puzzle_manager._add_live_puzzle(puzzle, demo_event)
        console.print("✅ 데모 퍼즐 생성 완료: 삼성전자 -6.8% 미스터리")


async def experience_new_puzzle(player: Player, buffett: BuffettPersona):
    """새로 생성된 퍼즐 체험"""
    console.print(Panel.fit(
        "🎮 4단계: 실시간 퍼즐 체험",
        style="bold blue"
    ))
    
    # 가장 신선한 퍼즐 선택
    active_puzzles = auto_puzzle_manager.get_active_puzzles(sort_by="freshness", limit=1)
    
    if not active_puzzles:
        console.print("❌ 체험할 수 있는 퍼즐이 없습니다.")
        return
    
    live_puzzle = active_puzzles[0]
    puzzle = live_puzzle.puzzle
    event = live_puzzle.source_event
    
    console.print(f"""
🎯 선택된 퍼즐: {puzzle.title}
📊 신선도: {live_puzzle.get_freshness_score():.1%}
🔥 심각도: {event.severity.upper()}
⚡ 퍼즐 적합도: {event.puzzle_worthiness:.1%}
    """)
    
    console.print(Panel(puzzle.description, title="📋 미스터리 상황", border_style="yellow"))
    
    # 버핏의 초기 조언
    buffett_advice = buffett.give_puzzle_hint(
        puzzle_data=event.to_puzzle_data(),
        discovered_clues=[],
        investigation_progress=0.0
    )
    
    console.print(Panel(buffett_advice, title="🏛️ 워렌 버핏의 조언", border_style="green"))
    
    # 간단한 조사 시뮬레이션
    console.print("\n🔍 자동 조사 시뮬레이션...")
    
    from walk_risk.core.risk_puzzle.investigation import InvestigationSystem
    investigation = InvestigationSystem()
    
    # 뉴스 조사
    if puzzle.available_clues:
        clue = puzzle.available_clues[0]  # 첫 번째 단서 조사
        success, evidence, details = investigation.investigate(clue, use_boost=False)
        
        if success:
            console.print(f"✅ 단서 발견: {evidence}")
            console.print(f"📝 상세 정보: {details.get('details', '추가 정보 없음')}")
            
            # 퍼즐 시도 기록
            auto_puzzle_manager.record_puzzle_attempt(
                puzzle_id=puzzle.puzzle_id,
                accuracy=0.75,
                completed=True
            )
            
            console.print("🎊 퍼즐 완료! 경험치와 스킬을 획득했습니다.")
    
    await asyncio.sleep(2)


async def demonstrate_auto_management():
    """자동 관리 시스템 데모"""
    console.print(Panel.fit(
        "⚙️ 5단계: 자동 관리 시스템",
        style="bold blue"
    ))
    
    # 시스템 통계 표시
    stats = auto_puzzle_manager.get_statistics()
    
    table = Table(title="시스템 통계")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    table.add_row("총 퍼즐 수", str(stats['total_puzzles']))
    table.add_row("활성 퍼즐", str(stats['active_puzzles']))
    table.add_row("완료된 퍼즐", str(stats['completed_puzzles']))
    table.add_row("만료된 퍼즐", str(stats['expired_puzzles']))
    table.add_row("완료율", f"{stats['completion_rate']:.1%}")
    table.add_row("평균 정확도", f"{stats['average_accuracy']:.1%}")
    table.add_row("시스템 실행 중", "✅" if stats['system_running'] else "❌")
    
    console.print(table)
    
    console.print("\n🔄 자동 관리 기능:")
    console.print("  • 5분마다 새로운 이벤트 감지")
    console.print("  • 30분마다 만료된 퍼즐 정리")
    console.print("  • 최대 10개 활성 퍼즐 유지")
    console.print("  • 6시간 퍼즐 수명 관리")
    console.print("  • 중복 이벤트 필터링 (1시간 쿨다운)")
    
    # 백그라운드 시스템 시작 데모
    console.print("\n🚀 백그라운드 자동 시스템 시작 시뮬레이션...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        auto_task = progress.add_task(
            description="자동 시스템 초기화 중...", 
            total=100
        )
        
        progress.update(auto_task, advance=25)
        console.print("  📡 시장 데이터 연결...")
        await asyncio.sleep(1)
        
        progress.update(auto_task, advance=25)
        console.print("  ⚙️ 백그라운드 루프 시작...")
        await asyncio.sleep(1)
        
        progress.update(auto_task, advance=25)
        console.print("  🔍 이벤트 감지 스케줄러 활성화...")
        await asyncio.sleep(1)
        
        progress.update(auto_task, advance=25)
        console.print("  ✅ 자동 시스템 준비 완료!")
    
    console.print(Panel.fit(
        "🎉 실시간 퍼즐 생성 시스템 데모 완료!\n\n"
        "💡 실제 환경에서는:\n"
        "  • 거래 시간 중 실시간 감지\n"
        "  • 무제한 퍼즐 자동 생성\n"
        "  • 플레이어별 맞춤 난이도\n"
        "  • 소셜 기능과 연동",
        style="bold green"
    ))


if __name__ == "__main__":
    asyncio.run(demonstrate_real_time_puzzle_system())