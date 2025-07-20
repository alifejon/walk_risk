"""
AI Guide System Demonstration
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from walk_risk.ai.ai_guide_manager import AIGuideManager, AIGuideConfig
from walk_risk.ai.ai_guide_engine import GuideContext, GuidanceType
from walk_risk.models.player.base import Player, PlayerClass, PlayerStats
from walk_risk.models.risk.base import Risk, RiskCategory, RiskLevel


async def demo_ai_guide_system():
    """Demonstrate the AI guide system"""
    
    print("🤖 AI 가이드 시스템 데모")
    print("=" * 50)
    
    # Create AI guide manager
    config = AIGuideConfig(
        proactive_guidance=True,
        guidance_frequency=60,  # Faster for demo
        max_daily_guidance=10,
        educational_mode=True
    )
    
    guide_manager = AIGuideManager(config)
    
    # Create demo player
    player = Player(
        username="김투자",
        email="investor@example.com",
        player_class=PlayerClass.ANALYST
    )
    player.stats.level = 15
    player.stats.successful_predictions = 8
    player.stats.failed_predictions = 3
    
    # Register player
    guide_manager.register_player(player)
    
    # Start guide manager
    await guide_manager.start()
    
    try:
        # Demo 1: Request general advice
        print("\n1. 일반 투자 조언 요청")
        print("-" * 30)
        
        response = await guide_manager.request_guidance(
            player_id=player.id,
            context=GuideContext.GENERAL_ADVICE,
            guidance_type=GuidanceType.ADVICE
        )
        
        print(f"멘토: {response.mentor_name}")
        print(f"조언: {response.message}")
        if response.quote:
            print(f"명언: '{response.quote}'")
        print(f"신뢰도: {response.confidence:.2f}")
        
        # Demo 2: Request risk analysis guidance
        print("\n2. 리스크 분석 가이드 요청")
        print("-" * 30)
        
        # Create sample risk
        sample_risk = Risk(
            name="시장 변동성 리스크",
            description="높은 시장 변동성으로 인한 포트폴리오 가치 변동",
            category=RiskCategory.MARKET,
            severity=0.7,
            complexity=0.6
        )
        
        response = await guide_manager.request_risk_guidance(
            player_id=player.id,
            risk=sample_risk,
            analysis_data={
                'risk_level': 'high',
                'market_volatility': 0.25,
                'portfolio_exposure': 0.8
            }
        )
        
        print(f"멘토: {response.mentor_name}")
        print(f"리스크 분석: {response.message}")
        if response.quote:
            print(f"명언: '{response.quote}'")
        
        # Demo 3: Request portfolio review
        print("\n3. 포트폴리오 검토 요청")
        print("-" * 30)
        
        portfolio_data = {
            'allocation': {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1},
            'total_value': 100000,
            'volatility': 0.18,
            'health_score': 0.75
        }
        
        response = await guide_manager.request_portfolio_review(
            player_id=player.id,
            portfolio_data=portfolio_data
        )
        
        print(f"멘토: {response.mentor_name}")
        print(f"포트폴리오 리뷰: {response.message}")
        if response.follow_up_questions:
            print("추가 질문:")
            for question in response.follow_up_questions:
                print(f"  • {question}")
        
        # Demo 4: Request challenge hint
        print("\n4. 도전 과제 힌트 요청")
        print("-" * 30)
        
        response = await guide_manager.request_challenge_hint(
            player_id=player.id,
            challenge_id="volatility_analysis",
            challenge_data={
                'difficulty': 0.8,
                'challenge_type': 'market_analysis',
                'current_step': 2
            }
        )
        
        print(f"멘토: {response.mentor_name}")
        print(f"힌트: {response.message}")
        
        # Demo 5: Request market event analysis
        print("\n5. 시장 이벤트 분석 요청")
        print("-" * 30)
        
        market_data = {
            'event_type': 'crash',
            'market_change': -0.08,
            'vix': 35.0,
            'volume_spike': True
        }
        
        response = await guide_manager.request_market_analysis(
            player_id=player.id,
            market_data=market_data
        )
        
        print(f"멘토: {response.mentor_name}")
        print(f"시장 분석: {response.message}")
        if response.quote:
            print(f"명언: '{response.quote}'")
        
        # Demo 6: Get mentor recommendations
        print("\n6. 추천 멘토 목록")
        print("-" * 30)
        
        recommendations = guide_manager.get_mentor_recommendations(player.id)
        
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec['name']} ({rec['title']})")
            print(f"   투자 스타일: {rec['investment_style']}")
            print(f"   성격: {rec['personality']}")
            print(f"   추천도: {rec['recommendation_score']:.2f}")
        
        # Demo 7: View guidance history
        print("\n7. 가이드 이력")
        print("-" * 30)
        
        history = guide_manager.get_guidance_history(player.id, limit=3)
        
        for i, guidance in enumerate(history, 1):
            print(f"{i}. {guidance['mentor_name']}: {guidance['message'][:50]}...")
            print(f"   시간: {guidance['timestamp']}")
        
        # Demo 8: Player guidance statistics
        print("\n8. 플레이어 가이드 통계")
        print("-" * 30)
        
        stats = guide_manager.get_player_guidance_stats(player.id)
        
        print(f"오늘 받은 가이드: {stats['daily_guidance_count']}/{stats['daily_limit']}")
        print(f"남은 가이드 횟수: {stats['remaining_guidance']}")
        print(f"총 받은 가이드: {stats['total_guidance_received']}")
        
        # Demo 9: System analytics
        print("\n9. 시스템 분석")
        print("-" * 30)
        
        analytics = guide_manager.get_analytics()
        
        print(f"총 가이드 요청: {analytics['manager_stats']['total_guidance_requests']}")
        print(f"활성 플레이어: {analytics['active_players']}")
        print(f"일일 가이드 사용량: {analytics['daily_guidance_usage']}")
        
        if analytics['engine_stats']['most_popular_mentor']:
            print(f"인기 멘토: {analytics['engine_stats']['most_popular_mentor']}")
        
        # Demo 10: Submit feedback
        print("\n10. 멘토 피드백 제출")
        print("-" * 30)
        
        feedback_success = await guide_manager.submit_mentor_feedback(
            player_id=player.id,
            guidance_id="demo_guidance_1",
            feedback="매우 도움이 되었습니다!",
            rating=5
        )
        
        if feedback_success:
            print("✅ 피드백이 성공적으로 제출되었습니다")
        else:
            print("❌ 피드백 제출에 실패했습니다")
        
        # Demo 11: Update mentor preference
        print("\n11. 멘토 선호도 업데이트")
        print("-" * 30)
        
        preference_updated = guide_manager.update_mentor_preference(
            player_id=player.id,
            mentor_id="buffett",
            preference="like"
        )
        
        if preference_updated:
            print("✅ Warren Buffett를 선호 멘토로 설정했습니다")
        
        # Wait a bit to show proactive guidance (if enabled)
        print("\n12. 능동적 가이드 대기 중... (5초)")
        print("-" * 30)
        
        # Set up event handler to capture proactive guidance
        proactive_guidance_received = False
        
        def handle_proactive_guidance(data):
            nonlocal proactive_guidance_received
            print(f"🔔 능동적 가이드 수신!")
            print(f"멘토: {data['guidance']['mentor_name']}")
            print(f"메시지: {data['guidance']['message']}")
            proactive_guidance_received = True
        
        guide_manager.add_event_handler('proactive_guidance', handle_proactive_guidance)
        
        # Update player's last activity to trigger proactive guidance
        player.last_active = datetime.now()
        guide_manager.update_player(player)
        
        # Wait for proactive guidance
        for i in range(5):
            await asyncio.sleep(1)
            if proactive_guidance_received:
                break
            print(f"대기 중... {5-i}초 남음")
        
        if not proactive_guidance_received:
            print("능동적 가이드가 아직 발송되지 않았습니다. (조건에 따라 결정됨)")
        
    finally:
        # Clean up
        await guide_manager.stop()
    
    print("\n" + "=" * 50)
    print("🎉 AI 가이드 시스템 데모 완료!")


def demo_mentor_library():
    """Demonstrate mentor library features"""
    
    print("\n🧠 멘토 라이브러리 데모")
    print("=" * 50)
    
    from walk_risk.ai.mentor_personas import MentorLibrary, InvestmentStyle, MentorPersonality
    
    library = MentorLibrary()
    
    # Show all mentors
    print("\n사용 가능한 멘토들:")
    print("-" * 30)
    
    for mentor_id, mentor in library.mentors.items():
        print(f"• {mentor.name} ({mentor.title})")
        print(f"  투자 스타일: {mentor.investment_style.value}")
        print(f"  성격: {mentor.personality.value}")
        print(f"  철학: {mentor.philosophy}")
        print()
    
    # Get mentors by style
    print("가치투자 멘토들:")
    print("-" * 30)
    
    value_mentors = library.get_mentors_by_style(InvestmentStyle.VALUE)
    for mentor in value_mentors:
        print(f"• {mentor.name}: {mentor.philosophy}")
    
    # Get mentor recommendation
    print("\n멘토 추천 (초보자용):")
    print("-" * 30)
    
    recommended = library.recommend_mentor_for_player(
        player_level=5,
        risk_tolerance=0.3,
        investment_experience="beginner"
    )
    
    print(f"추천 멘토: {recommended.name}")
    print(f"이유: 초보자에게 적합한 {recommended.personality.value} 스타일")
    
    # Compare mentors
    print("\nBuffett vs Lynch 비교:")
    print("-" * 30)
    
    comparison = library.get_mentor_comparison("buffett", "lynch")
    if comparison:
        print(f"Buffett: {comparison['mentor1']['style']}, 리스크 허용도: {comparison['mentor1']['risk_tolerance']}")
        print(f"Lynch: {comparison['mentor2']['style']}, 리스크 허용도: {comparison['mentor2']['risk_tolerance']}")
        print(f"리스크 허용도 차이: {comparison['differences']['risk_tolerance_diff']:.2f}")


async def main():
    """Main demo function"""
    
    print("🎯 Walk Risk AI 가이드 시스템 종합 데모")
    print("=" * 60)
    
    # Demo mentor library
    demo_mentor_library()
    
    # Demo AI guide system
    await demo_ai_guide_system()


if __name__ == "__main__":
    asyncio.run(main())