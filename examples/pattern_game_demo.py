"""
Pattern Game System Demo - 기술적 분석 패턴 게임화 시연
"""
import asyncio
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from walk_risk.models.patterns import (
    PatternGameEngine, PatternDifficulty, GameMode, ChallengeType,
    PatternType, IndicatorType
)


async def demo_pattern_recognition_game():
    """패턴 인식 게임 데모"""
    
    print("🎯 패턴 인식 게임 시스템 데모")
    print("=" * 60)
    
    # 게임 엔진 초기화
    game_engine = PatternGameEngine()
    
    # 1. 초급 패턴 인식 챌린지 생성
    print("\n1. 초급 패턴 인식 챌린지 생성")
    print("-" * 40)
    
    pattern_challenge = game_engine.create_pattern_recognition_challenge(
        pattern_types=[PatternType.HEAD_AND_SHOULDERS, PatternType.DOUBLE_TOP],
        difficulty=PatternDifficulty.BEGINNER,
        player_id="demo_player"
    )
    
    print(f"✅ 챌린지 생성됨: {pattern_challenge.title}")
    print(f"   - 난이도: {pattern_challenge.difficulty.value}")
    print(f"   - 시간 제한: {pattern_challenge.time_limit}초")
    print(f"   - 질문 수: {len(pattern_challenge.questions)}")
    print(f"   - 학습 목표: {', '.join(pattern_challenge.learning_objectives)}")
    
    # 차트 데이터 정보
    print(f"   - 차트 데이터: {len(pattern_challenge.chart_data)}일")
    print(f"   - 패턴 정보: {pattern_challenge.patterns[0].pattern_type.value}")
    
    # 질문 미리보기
    print("\n📝 챌린지 질문 미리보기:")
    for i, question in enumerate(pattern_challenge.questions[:2], 1):
        print(f"   {i}. {question['question']}")
        print(f"      선택지: {question['options']}")
    
    # 2. 답안 제출 시뮬레이션
    print("\n2. 답안 제출 시뮬레이션")
    print("-" * 40)
    
    # 정답 기반으로 답안 생성 (일부러 틀린 답도 포함)
    simulated_answers = []
    for i, correct_answer in enumerate(pattern_challenge.correct_answers):
        if i == 0:  # 첫 번째 답은 정답
            simulated_answers.append(correct_answer)
        elif i == 1:  # 두 번째 답은 오답
            options = pattern_challenge.questions[i]['options']
            wrong_options = [opt for opt in options if opt != correct_answer]
            simulated_answers.append(wrong_options[0] if wrong_options else correct_answer)
        else:  # 나머지는 정답
            simulated_answers.append(correct_answer)
    
    # 결과 제출
    result = game_engine.submit_challenge_answer(
        challenge_id=pattern_challenge.id,
        player_id="demo_player",
        answers=simulated_answers,
        time_taken=240.5  # 4분 소요
    )
    
    print(f"✅ 챌린지 완료!")
    print(f"   - 최종 점수: {result.calculate_final_score():.1f}/100")
    print(f"   - 성과 등급: {result.get_performance_grade()}")
    print(f"   - 정확도: {result.accuracy:.1%}")
    print(f"   - 속도 보너스: +{result.speed_bonus:.1f}점")
    print(f"   - 획득 경험치: {result.experience_gained}XP")
    
    if result.badges_earned:
        print(f"   - 획득 배지: {', '.join(result.badges_earned)}")
    
    print(f"\n💪 강점: {', '.join(result.strengths)}")
    if result.weaknesses:
        print(f"⚠️  약점: {', '.join(result.weaknesses)}")
    if result.improvement_suggestions:
        print(f"💡 개선 제안:")
        for suggestion in result.improvement_suggestions:
            print(f"     • {suggestion}")


async def demo_indicator_analysis_game():
    """지표 분석 게임 데모"""
    
    print("\n\n🔍 지표 분석 게임 데모")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 지표 분석 챌린지 생성
    indicator_challenge = game_engine.create_indicator_analysis_challenge(
        indicator_types=[IndicatorType.RSI, IndicatorType.MACD],
        difficulty=PatternDifficulty.INTERMEDIATE
    )
    
    print(f"✅ 지표 분석 챌린지 생성: {indicator_challenge.title}")
    print(f"   - 분석할 지표: {len(indicator_challenge.indicators)}개")
    print(f"   - 질문 수: {len(indicator_challenge.questions)}")
    
    # 지표 정보 출력
    for indicator in indicator_challenge.indicators:
        latest_value = indicator.get_latest_value()
        print(f"   - {indicator.name}: {latest_value.value if latest_value else 'N/A'}")
    
    # 질문 미리보기
    print("\n📊 지표 분석 질문:")
    for i, question in enumerate(indicator_challenge.questions, 1):
        print(f"   {i}. {question['question']}")
        print(f"      선택지: {question['options']}")
    
    # 답안 시뮬레이션 (모두 정답)
    correct_answers = indicator_challenge.correct_answers
    
    result = game_engine.submit_challenge_answer(
        challenge_id=indicator_challenge.id,
        player_id="demo_player",
        answers=correct_answers,
        time_taken=180.0  # 3분 소요
    )
    
    print(f"\n✅ 지표 분석 완료!")
    print(f"   - 최종 점수: {result.calculate_final_score():.1f}/100")
    print(f"   - 정확도: {result.accuracy:.1%}")
    print(f"   - 획득 경험치: {result.experience_gained}XP")


async def demo_adaptive_difficulty():
    """적응형 난이도 시스템 데모"""
    
    print("\n\n🎚️ 적응형 난이도 시스템 데모")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 플레이어 성과 기록 시뮬레이션
    player_id = "adaptive_player"
    
    # 초기 성과 (낮음)
    initial_scores = [45, 52, 48, 55, 60]
    for score in initial_scores:
        game_engine._update_player_performance(player_id, score)
    
    difficulty1 = game_engine.get_adaptive_difficulty(player_id)
    print(f"📈 초기 성과 (평균 {sum(initial_scores)/len(initial_scores):.1f}점)")
    print(f"   → 추천 난이도: {difficulty1.value}")
    
    # 성과 향상 시뮬레이션
    improved_scores = [70, 75, 78, 80, 85]
    for score in improved_scores:
        game_engine._update_player_performance(player_id, score)
    
    difficulty2 = game_engine.get_adaptive_difficulty(player_id)
    print(f"\n📈 향상된 성과 (평균 {sum(improved_scores)/len(improved_scores):.1f}점)")
    print(f"   → 추천 난이도: {difficulty2.value}")
    
    # 고급 수준 시뮬레이션
    expert_scores = [88, 92, 90, 95, 93]
    for score in expert_scores:
        game_engine._update_player_performance(player_id, score)
    
    difficulty3 = game_engine.get_adaptive_difficulty(player_id)
    print(f"\n📈 전문가 수준 (평균 {sum(expert_scores)/len(expert_scores):.1f}점)")
    print(f"   → 추천 난이도: {difficulty3.value}")


async def demo_challenge_recommendations():
    """챌린지 추천 시스템 데모"""
    
    print("\n\n🎯 맞춤형 챌린지 추천 시스템")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 다양한 수준의 플레이어들에게 추천
    player_levels = [
        ("beginner_player", PatternDifficulty.BEGINNER),
        ("intermediate_player", PatternDifficulty.INTERMEDIATE),
        ("advanced_player", PatternDifficulty.ADVANCED)
    ]
    
    for player_id, difficulty in player_levels:
        # 해당 난이도로 성과 기록 설정
        if difficulty == PatternDifficulty.BEGINNER:
            scores = [50, 55, 60]
        elif difficulty == PatternDifficulty.INTERMEDIATE:
            scores = [70, 75, 72]
        else:
            scores = [85, 88, 90]
        
        for score in scores:
            game_engine._update_player_performance(player_id, score)
        
        recommendations = game_engine.get_recommended_challenges(player_id)
        
        print(f"\n👤 {player_id} ({difficulty.value})")
        print(f"   추천 챌린지 {len(recommendations)}개:")
        
        for i, rec in enumerate(recommendations[:3], 1):  # 상위 3개만 표시
            print(f"   {i}. {rec['type']}")
            print(f"      - 난이도: {rec['difficulty']}")
            print(f"      - 예상 소요시간: {rec['estimated_duration']}초")
            print(f"      - 학습 가치: {rec['learning_value']}")


async def demo_signal_timing_game():
    """신호 타이밍 게임 데모"""
    
    print("\n\n⏰ 신호 타이밍 게임 데모")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 신호 타이밍 챌린지 생성
    timing_challenge = game_engine.create_signal_timing_challenge(
        difficulty=PatternDifficulty.INTERMEDIATE
    )
    
    print(f"✅ 타이밍 챌린지 생성: {timing_challenge.title}")
    print(f"   - 분석할 지표: {len(timing_challenge.indicators)}개")
    print(f"   - 차트 기간: {len(timing_challenge.chart_data)}일")
    
    # 차트 데이터 요약 정보
    data = timing_challenge.chart_data
    print(f"   - 가격 범위: ${data['close'].min():.2f} ~ ${data['close'].max():.2f}")
    print(f"   - 최종 가격: ${data['close'].iloc[-1]:.2f}")
    
    print("\n📈 타이밍 분석 질문:")
    for i, question in enumerate(timing_challenge.questions, 1):
        print(f"   {i}. {question['question']}")
        if question.get('options'):
            print(f"      선택지: {question['options']}")


async def demo_divergence_detection():
    """다이버전스 탐지 게임 데모"""
    
    print("\n\n🔄 다이버전스 탐지 게임 데모")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 다이버전스 탐지 챌린지 생성
    divergence_challenge = game_engine.create_divergence_detection_challenge(
        difficulty=PatternDifficulty.ADVANCED
    )
    
    print(f"✅ 다이버전스 챌린지 생성: {divergence_challenge.title}")
    print(f"   - 분석 기간: {len(divergence_challenge.chart_data)}일")
    print(f"   - 질문 수: {len(divergence_challenge.questions)}")
    
    print("\n🔍 다이버전스 분석 질문:")
    for i, question in enumerate(divergence_challenge.questions, 1):
        print(f"   {i}. {question['question']}")
        print(f"      선택지: {question['options']}")


async def demo_game_statistics():
    """게임 통계 시스템 데모"""
    
    print("\n\n📊 게임 통계 시스템")
    print("=" * 60)
    
    game_engine = PatternGameEngine()
    
    # 여러 챌린지 완료 시뮬레이션
    for i in range(5):
        challenge = game_engine.create_pattern_recognition_challenge(
            pattern_types=[PatternType.HEAD_AND_SHOULDERS],
            difficulty=PatternDifficulty.BEGINNER
        )
        
        # 답안 제출
        answers = challenge.correct_answers  # 모두 정답
        result = game_engine.submit_challenge_answer(
            challenge_id=challenge.id,
            player_id=f"player_{i}",
            answers=answers,
            time_taken=200 + i * 50
        )
    
    # 통계 출력
    stats = game_engine.get_challenge_statistics()
    
    print(f"📈 전체 통계:")
    print(f"   - 총 챌린지 수: {stats['total_challenges']}")
    print(f"   - 평균 점수: {stats['average_score']:.1f}")
    print(f"   - 평균 정확도: {stats['average_accuracy']:.1%}")
    print(f"   - 완료율: {stats['completion_rate']:.1%}")
    
    if stats.get('difficulty_distribution'):
        print(f"\n📊 난이도별 분포:")
        for difficulty, count in stats['difficulty_distribution'].items():
            print(f"   - {difficulty}: {count}개")
    
    if stats.get('popular_game_modes'):
        print(f"\n🎮 인기 게임 모드:")
        for mode, count in stats['popular_game_modes'].items():
            print(f"   - {mode}: {count}회")


async def main():
    """메인 데모 함수"""
    
    print("🎯 Walk Risk 패턴 게임 시스템 종합 데모")
    print("=" * 80)
    
    # 각 데모 실행
    await demo_pattern_recognition_game()
    await demo_indicator_analysis_game()
    await demo_adaptive_difficulty()
    await demo_challenge_recommendations()
    await demo_signal_timing_game()
    await demo_divergence_detection()
    await demo_game_statistics()
    
    print("\n" + "=" * 80)
    print("🎉 패턴 게임 시스템 데모 완료!")
    print("\n💡 주요 구현 완료 사항:")
    print("   ✅ 차트 패턴 인식 게임")
    print("   ✅ 기술적 지표 분석 게임")
    print("   ✅ 신호 타이밍 게임")
    print("   ✅ 다이버전스 탐지 게임")
    print("   ✅ 적응형 난이도 시스템")
    print("   ✅ 개인화된 챌린지 추천")
    print("   ✅ 성과 분석 및 피드백")
    print("   ✅ 보상 및 배지 시스템")
    print("   ✅ 통계 및 분석 시스템")


if __name__ == "__main__":
    asyncio.run(main())