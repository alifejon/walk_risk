"""멀티 멘토 시스템 데모 - 5명 투자 거장들의 다양한 관점 체험"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box

from walk_risk.ai.mentor_personas import MentorFactory
from walk_risk.core.auto_puzzle_manager import auto_puzzle_manager
from walk_risk.data.market_data.market_event_detector import MarketEvent, EventType
from walk_risk.core.risk_puzzle.puzzle_engine import PuzzleEngine
from walk_risk.models.player.base import Player

console = Console()

async def demonstrate_multi_mentor_system():
    """멀티 멘토 시스템 종합 데모"""
    
    console.print(Panel.fit(
        "🌟 Walk Risk 멀티 멘토 시스템 데모\n5명의 투자 거장들이 같은 상황을 어떻게 다르게 해석하는지 체험하세요!",
        style="bold yellow"
    ))
    
    # 1단계: 멘토 소개
    await introduce_all_mentors()
    
    # 2단계: 공통 퍼즐 상황 제시
    puzzle_scenario = await create_sample_puzzle()
    
    # 3단계: 각 멘토의 다른 관점 비교
    await compare_mentor_perspectives(puzzle_scenario)
    
    # 4단계: 사용자 멘토 선택 체험
    await interactive_mentor_selection(puzzle_scenario)
    
    # 5단계: 멘토별 특화 조언 데모
    await specialized_advice_demo()


async def introduce_all_mentors():
    """모든 멘토 소개"""
    console.print(Panel.fit(
        "📚 1단계: 투자 거장들을 만나보세요",
        style="bold blue"
    ))
    
    mentors = MentorFactory.get_all_mentors()
    
    table = Table(title="Walk Risk 투자 멘토단", box=box.ROUNDED)
    table.add_column("멘토", style="cyan", width=15)
    table.add_column("타이틀", style="magenta", width=20) 
    table.add_column("투자 철학", style="green", width=40)
    table.add_column("전문 분야", style="yellow", width=25)
    
    mentor_specialties = {
        "buffett": "가치투자, 장기투자, 안전마진",
        "lynch": "성장주, 소비자 관점, 10-Bagger",
        "graham": "정량분석, 내재가치, 안전투자",
        "dalio": "거시경제, 포트폴리오, 리스크관리",
        "wood": "혁신기술, 파괴적혁신, 미래성장"
    }
    
    for key, mentor in mentors.items():
        table.add_row(
            mentor.name,
            mentor.title,
            mentor.philosophy,
            mentor_specialties[key]
        )
    
    console.print(table)
    console.print("\n💡 각 멘토는 완전히 다른 관점으로 같은 상황을 분석합니다!")
    
    await asyncio.sleep(2)


async def create_sample_puzzle():
    """샘플 퍼즐 시나리오 생성"""
    console.print(Panel.fit(
        "🧩 2단계: 공통 퍼즐 상황",
        style="bold blue"
    ))
    
    # 실제와 유사한 시나리오 생성
    sample_event = MarketEvent(
        event_id="MULTI_DEMO_005930",
        event_type=EventType.SHARP_DROP,
        symbol="005930.KS",
        company_name="삼성전자",
        trigger_price=68500,
        change_percent=-7.2,
        volume_ratio=2.8,
        market_sentiment="bearish",
        sector_performance={"반도체": -5.1, "전자부품": -4.3},
        peer_comparison={"000660.KS": -4.8, "006400.KS": -6.1},
        severity="high",
        puzzle_worthiness=0.89
    )
    
    console.print(Panel(f"""
🚨 [긴급 상황]

📊 삼성전자가 -7.2% 급락했습니다!
📈 거래량: 평소 대비 2.8배 급증
🌍 시장 분위기: 하락세 (bearish)
📉 반도체 업종 전체 -5.1% 하락
⚡ 심각도: HIGH

💭 과연 이 상황을 어떻게 해석해야 할까요?
같은 상황을 5명의 투자 거장들이 어떻게 다르게 보는지 확인해보세요!
    """.strip(), title="🔥 실시간 시장 이벤트", border_style="red"))
    
    await asyncio.sleep(2)
    return sample_event


async def compare_mentor_perspectives(puzzle_scenario: MarketEvent):
    """멘토별 관점 비교"""
    console.print(Panel.fit(
        "🔍 3단계: 5가지 다른 관점 비교",
        style="bold blue"
    ))
    
    mentors = MentorFactory.get_all_mentors()
    puzzle_data = puzzle_scenario.to_puzzle_data()
    
    for i, (key, mentor) in enumerate(mentors.items(), 1):
        console.print(f"\n[bold cyan]═══ {i}. {mentor.name}의 관점 ═══[/bold cyan]")
        
        # 각 멘토의 첫 번째 힌트 (clue_count=0)
        hint = mentor.give_puzzle_hint(
            puzzle_data=puzzle_data,
            discovered_clues=[],
            investigation_progress=0.0
        )
        
        console.print(Panel(hint, border_style="green"))
        await asyncio.sleep(1.5)
    
    console.print(Panel.fit(
        "🤔 같은 상황, 완전히 다른 5가지 접근법!\n"
        "• 버핏: 가치 중심의 신중한 접근\n"
        "• 린치: 소비자 관점의 실용적 분석\n"
        "• 그레이엄: 객관적 데이터 기반 접근\n"
        "• 달리오: 거시경제적 시스템 사고\n"
        "• 우드: 혁신 기술 중심의 미래 지향적 관점",
        style="bold magenta"
    ))


async def interactive_mentor_selection(puzzle_scenario: MarketEvent):
    """대화형 멘토 선택 체험"""
    console.print(Panel.fit(
        "🎮 4단계: 멘토 선택 체험",
        style="bold blue"
    ))
    
    console.print("어떤 멘토의 가이드를 받고 싶으신가요?")
    
    mentors = MentorFactory.get_all_mentors()
    mentor_choices = []
    
    for i, (key, mentor) in enumerate(mentors.items(), 1):
        choice = f"{i}. {mentor.name} - {mentor.title}"
        mentor_choices.append(key)
        console.print(f"  {choice}")
    
    # 자동 선택 (데모용)
    console.print("\n[dim]데모에서는 자동으로 Peter Lynch를 선택합니다...[/dim]")
    await asyncio.sleep(1)
    
    chosen_mentor_key = "lynch"  # 데모용 자동 선택
    chosen_mentor = mentors[chosen_mentor_key]
    
    console.print(f"\n✅ {chosen_mentor.name}을(를) 선택했습니다!")
    console.print(chosen_mentor.get_greeting())
    
    # 선택된 멘토의 상세 가이드
    puzzle_data = puzzle_scenario.to_puzzle_data()
    detailed_guidance = chosen_mentor.give_puzzle_hint(
        puzzle_data=puzzle_data,
        discovered_clues=["news_analysis"],  # 한 단계 진행된 상황
        investigation_progress=0.3
    )
    
    console.print(Panel(detailed_guidance, title=f"📈 {chosen_mentor.name}의 상세 가이드", border_style="cyan"))
    
    await asyncio.sleep(2)


async def specialized_advice_demo():
    """멘토별 특화 조언 데모"""
    console.print(Panel.fit(
        "💡 5단계: 상황별 특화 조언",
        style="bold blue"
    ))
    
    situations = [
        ("market_fear", "😨 시장 공포 상황"),
        ("greed", "🤑 과도한 탐욕 상황"), 
        ("patience", "⏰ 인내가 필요한 상황")
    ]
    
    mentors = MentorFactory.get_all_mentors()
    
    for situation_key, situation_desc in situations:
        console.print(f"\n[bold yellow]═══ {situation_desc} ═══[/bold yellow]")
        
        table = Table(box=box.SIMPLE)
        table.add_column("멘토", style="cyan", width=15)
        table.add_column("조언", style="white", width=60)
        
        for mentor in mentors.values():
            advice = mentor.get_advice({"situation": situation_key})
            # 멘토 이름 제거하고 조언만 표시
            clean_advice = advice.split(": ", 1)[1] if ": " in advice else advice
            table.add_row(mentor.name, clean_advice)
        
        console.print(table)
        await asyncio.sleep(2)
    
    console.print(Panel.fit(
        "🎊 멀티 멘토 시스템 데모 완료!\n\n"
        "🌟 이제 Walk Risk에서는:\n"
        "• 5명의 투자 거장 중 선택 가능\n"
        "• 상황별 맞춤형 조언 제공\n"
        "• 같은 퍼즐, 완전히 다른 관점\n"
        "• 다양한 투자 철학 학습 가능\n\n"
        "💡 각자의 투자 성향에 맞는 멘토를 선택하고,\n"
        "   다양한 관점으로 시장을 바라보세요!",
        style="bold green"
    ))


async def bonus_mentor_comparison():
    """보너스: 멘토 간 의견 대립 시나리오"""
    console.print(Panel.fit(
        "🥊 보너스: 멘토 간 의견 대립",
        style="bold red"
    ))
    
    console.print("같은 가설에 대한 각 멘토의 검증 결과:")
    
    sample_hypothesis = "삼성전자 주가가 단기적으로 회복될 것이다"
    confidence = 0.75
    evidence = 0.6
    
    mentors = MentorFactory.get_all_mentors()
    
    for mentor in mentors.values():
        validation = mentor.validate_hypothesis_thinking(sample_hypothesis, confidence, evidence)
        console.print(Panel(validation, title=f"{mentor.name}의 검증", border_style="yellow"))
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(demonstrate_multi_mentor_system())