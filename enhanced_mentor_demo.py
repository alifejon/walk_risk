"""개선된 멀티 멘토 시스템 데모 - 토론 & 단계별 심화 분석"""

import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from rich.columns import Columns

from walk_risk.ai.mentor_personas import (
    MentorFactory, MentorDebate, StepByStepAnalysis
)
from walk_risk.data.market_data.market_event_detector import MarketEvent, EventType

console = Console()

async def demonstrate_enhanced_mentor_system():
    """개선된 멀티 멘토 시스템 데모"""
    
    console.print(Panel.fit(
        "🌟 Walk Risk 개선된 멀티 멘토 시스템\n"
        "💥 NEW: 멘토 간 토론 & 단계별 심화 분석",
        style="bold yellow"
    ))
    
    # 공통 퍼즐 시나리오
    sample_event = create_enhanced_scenario()
    
    console.print("\n🎯 어떤 기능을 체험하시겠습니까?")
    console.print("1. 🥊 멘토 간 토론 대결")
    console.print("2. 📊 단계별 심화 분석") 
    console.print("3. 🔄 둘 다 체험")
    
    # 데모에서는 자동으로 모든 기능 체험
    console.print("\n[dim]데모에서는 모든 기능을 순서대로 체험합니다...[/dim]")
    await asyncio.sleep(1)
    
    # 1. 멘토 간 토론 대결
    await demonstrate_mentor_debate(sample_event)
    
    # 2. 단계별 심화 분석
    await demonstrate_step_analysis(sample_event)


def create_enhanced_scenario():
    """강화된 시나리오 생성"""
    return MarketEvent(
        event_id="ENHANCED_DEMO_035420",
        event_type=EventType.SHARP_DROP,
        symbol="035420.KS", 
        company_name="NAVER",
        trigger_price=185000,
        change_percent=-8.5,
        volume_ratio=3.2,
        market_sentiment="bearish",
        sector_performance={"IT서비스": -6.2, "게임": -4.8},
        peer_comparison={"035720.KS": -7.1, "181710.KS": -5.3},
        severity="critical",
        puzzle_worthiness=0.92
    )


async def demonstrate_mentor_debate(sample_event: MarketEvent):
    """멘토 간 토론 데모"""
    console.print(Panel.fit(
        "🥊 1부: 멘토 간 토론 대결",
        style="bold red"
    ))
    
    console.print("📊 상황: NAVER -8.5% 급락에 대한 투자 거장들의 격론!")
    
    # 토론 조합 선택
    debate_pairs = [
        ("buffett", "wood", "🏛️ 안정 vs 🚀 혁신"),
        ("lynch", "graham", "📈 성장 vs 🎓 가치"),
        ("dalio", "lynch", "🌍 거시 vs 📈 개별")
    ]
    
    for i, (mentor1, mentor2, description) in enumerate(debate_pairs, 1):
        console.print(f"\n[bold cyan]═══ 토론 {i}: {description} ═══[/bold cyan]")
        
        # 토론 생성
        debate = MentorFactory.create_mentor_debate(
            sample_event.to_puzzle_data(), mentor1, mentor2
        )
        
        # 토론 시나리오 소개
        scenario = debate.generate_debate_scenario()
        console.print(Panel(scenario, border_style="yellow"))
        
        # 3라운드 토론
        for round_num in range(1, 4):
            console.print(f"\n[bold magenta]📢 Round {round_num}[/bold magenta]")
            
            round_result = debate.conduct_debate_round(round_num)
            
            # 두 멘토의 발언을 나란히 표시
            left_panel = Panel(
                round_result['mentor1_statement'], 
                title=f"{debate.mentor1.name}",
                border_style="blue",
                width=60
            )
            right_panel = Panel(
                round_result['mentor2_statement'],
                title=f"{debate.mentor2.name}", 
                border_style="green",
                width=60
            )
            
            console.print(Columns([left_panel, right_panel]))
            await asyncio.sleep(2)
        
        # 토론 결과 요약
        console.print(Panel.fit(
            f"🏆 토론 완료!\n"
            f"• {debate.mentor1.name}: {debate.mentor1.philosophy}\n" 
            f"• {debate.mentor2.name}: {debate.mentor2.philosophy}\n\n"
            f"🤔 어느 쪽 관점이 더 설득력 있나요?",
            style="bold yellow"
        ))
        
        if i < len(debate_pairs):
            await asyncio.sleep(2)


async def demonstrate_step_analysis(sample_event: MarketEvent):
    """단계별 심화 분석 데모"""
    console.print(Panel.fit(
        "📊 2부: 단계별 심화 분석",
        style="bold blue"
    ))
    
    console.print("🎯 Peter Lynch와 함께 5단계 심화 분석을 진행합니다.")
    
    # Lynch 멘토 선택
    lynch = MentorFactory.get_mentor("lynch")
    analysis = StepByStepAnalysis(lynch, sample_event.to_puzzle_data())
    
    # 가상의 단서 수집 시뮬레이션
    discovered_clues = []
    clue_progression = [
        "뉴스 분석",
        "재무 데이터", 
        "기술적 분석",
        "업종 비교",
        "시장 심리"
    ]
    
    for step in range(1, 6):
        console.print(f"\n[bold green]📈 {step}단계: {get_step_name(step)}[/bold green]")
        
        # 단서 추가 (단계별로)
        if step > 1 and step-2 < len(clue_progression):
            discovered_clues.append(clue_progression[step-2])
            console.print(f"🔍 새로운 단서 발견: {clue_progression[step-2]}")
        
        # 단계별 가이드 제공
        guidance = analysis.get_step_guidance(step, discovered_clues)
        console.print(Panel(guidance, border_style="cyan"))
        
        # 단계별 진행 상황 표시
        progress_bar = "█" * step + "░" * (5-step)
        console.print(f"📊 진행률: [{progress_bar}] {step}/5 ({step*20}%)")
        
        await asyncio.sleep(2.5)
    
    # 최종 요약
    console.print(Panel.fit(
        "🎊 5단계 심화 분석 완료!\n\n"
        "✅ 체계적 분석 프로세스 체험\n"
        "✅ 단계별 맞춤 가이드 확인\n" 
        "✅ 점진적 통찰 획득\n\n"
        "💡 이제 더 정교하고 체계적인 투자 분석이 가능합니다!",
        style="bold green"
    ))


def get_step_name(step: int) -> str:
    """단계 이름 반환"""
    step_names = {
        1: "초기 상황 평가",
        2: "데이터 심화 분석", 
        3: "비교 분석",
        4: "리스크 평가",
        5: "최종 결론"
    }
    return step_names.get(step, f"{step}단계")


async def bonus_feature_preview():
    """보너스: 향후 기능 미리보기"""
    console.print(Panel.fit(
        "🔮 Coming Soon: 향후 추가될 기능들",
        style="bold purple"
    ))
    
    features = [
        "🤝 멘토 협업 모드 - 2명 멘토가 함께 분석",
        "⚡ 실시간 토론 - 시장 이벤트 발생 시 즉시 토론",
        "🏆 사용자 투표 - 어느 멘토가 더 설득력있는지 투표",
        "📈 성과 추적 - 각 멘토 조언의 실제 수익률 비교",
        "🎮 토너먼트 모드 - 16강, 8강식 멘토 토너먼트"
    ]
    
    for feature in features:
        console.print(f"  {feature}")
        await asyncio.sleep(0.5)


async def main():
    """메인 실행 함수"""
    await demonstrate_enhanced_mentor_system()
    await bonus_feature_preview()
    
    console.print(Panel.fit(
        "🌟 Walk Risk 개선된 멀티 멘토 시스템 데모 완료!\n\n"
        "🎯 새로운 기능들:\n"
        "• 🥊 멘토 간 실시간 토론 대결\n"
        "• 📊 5단계 체계적 심화 분석\n"
        "• 🔄 단계별 맞춤 가이드\n"
        "• 💭 상대방 의견에 대한 반박\n\n"
        "💡 이제 Walk Risk는 진정한 투자 교육 플랫폼입니다!",
        style="bold green"
    ))


if __name__ == "__main__":
    asyncio.run(main())