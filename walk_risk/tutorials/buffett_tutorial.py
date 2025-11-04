"""Buffett Tutorial - 워런 버핏과 함께하는 투자 여정"""

from typing import Dict, Any, List, Optional
import asyncio
import random
from datetime import datetime, timedelta

from ..models.player.base import Player
from ..models.risk.base import RiskType, RiskLevel
from ..models.portfolio.assets import Asset, AssetType
from ..ai.mentor_personas import BuffettPersona
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BuffettTutorial:
    """버핏 멘토와 함께하는 튜토리얼"""
    
    def __init__(self, tutorial_manager, player: Player):
        self.tutorial_manager = tutorial_manager
        self.game_manager = tutorial_manager.game_manager
        self.player = player
        self.buffett = BuffettPersona()
        self.tutorial_portfolio = None
        self.emotional_state = {
            "confidence": 3,  # 1-10
            "fear": 7,  # 1-10
            "greed": 5,  # 1-10
            "patience": 2  # 1-10
        }
        
    async def welcome_stage(self) -> Dict[str, Any]:
        """환영 스테이지"""
        welcome_message = f"""
🏛️ 워런 버핏: "{self.player.name}님, 투자의 세계에 오신 것을 환영합니다!

저는 워런 버핏입니다. 오늘부터 당신의 투자 멘토가 되겠습니다.

함께 배울 것들:
1. 📊 가치투자의 기본 원칙
2. 🎯 리스크를 기회로 바꾸는 방법
3. 🔓 시장 공포를 극복하는 비법
4. 💰 복리의 마법을 활용하는 방법

준비가 되셨나요?"
        """
        
        # 초기 설정
        initial_capital = 1_000_000  # 100만원
        
        # 튜토리얼용 가상 포트폴리오 생성
        self.tutorial_portfolio = {
            "cash": initial_capital,
            "assets": [],
            "total_value": initial_capital,
            "start_value": initial_capital
        }
        
        return {
            "message": welcome_message,
            "initial_capital": initial_capital,
            "emotional_state": self.emotional_state,
            "actions": [
                {"id": "start", "label": "네, 시작하겠습니다!"},
                {"id": "nervous", "label": "조금 긴장되네요..."}
            ]
        }
        
    async def mentor_selection_stage(self) -> Dict[str, Any]:
        """멘토 선택 스테이지 (버핏 튜토리얼에서는 버핏 소개만)"""
        buffett_intro = f"""
🏛️ 워런 버핏의 투자 철학:

📖 핵심 원칙:
1. "가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것입니다"
2. "다른 사람들이 탐욕스러울 때 두려워하고, 두려워할 때 탐욕스러워하세요"
3. "장기적으로 보유할 주식을 사세요"

🎯 나의 목표:
당신이 평생 사용할 수 있는 투자 철학을 전수하겠습니다.
빠른 수익보다 확실한 성장을 추구하겠습니다.

하지만 기억하세요:
"당신이 10년, 20년 보유할 수 없다면, 10분도 보유하지 마세요."
        """
        
        # 감정 상태 업데이트 (버핏 선택으로 자신감 상승)
        self.emotional_state["confidence"] += 1
        self.emotional_state["patience"] += 1
        
        return {
            "mentor_info": buffett_intro,
            "selected_mentor": "warren_buffett",
            "emotional_state": self.emotional_state,
            "next_step": "이제 첫 번째 리스크에 도전해볼까요?",
            "actions": [
                {"id": "ready", "label": "네, 준비됐습니다!"}
            ]
        }
        
    async def first_risk_stage(self) -> Dict[str, Any]:
        """첫 번째 리스크 도전 - 시장 공포"""
        # 리스크 소개
        risk_intro = """
🔒 첫 번째 리스크: "시장 공포 (Market Fear)"

📊 상황 설명:
주식시장이 급락하면 많은 투자자들이 공포에 빠집니다.
하지만 이때가 바로 기회일 수 있습니다.

🔑 필요한 열쇠:
1. 지식 열쇠: 시장의 역사 이해
2. 경험 열쇠: 시장 변동성 체험
3. 지혜 열쇠: 감정 조절 능력
        """
        
        # 시장 역사 학습 콘텐츠
        market_history = [
            {
                "year": "1929년 대공황",
                "drop": "-89%",
                "recovery": "25년",
                "lesson": "시장은 결국 회복됩니다"
            },
            {
                "year": "2008년 금융위기",
                "drop": "-57%",
                "recovery": "6년",
                "lesson": "위기는 기회의 시작입니다"
            },
            {
                "year": "2020년 코로나",
                "drop": "-34%",
                "recovery": "6개월",
                "lesson": "빠른 회복도 가능합니다"
            }
        ]
        
        # 시뮬레이션 준비
        simulation_scenario = {
            "company": "삼성전자",
            "buy_price": 70000,
            "current_price": 59500,  # -15% 하락
            "investment": 500000,
            "shares": 7,
            "current_value": 416500,
            "loss": -83500,
            "loss_percent": -16.7
        }
        
        return {
            "risk_intro": risk_intro,
            "market_history": market_history,
            "simulation_ready": True,
            "simulation_scenario": simulation_scenario,
            "buffett_advice": "🏛️ 버핏: \"역사를 보세요. 시장은 항상 회복했습니다. 지금이 바로 학습할 시간입니다.\"",
            "actions": [
                {"id": "learn_history", "label": "시장 역사 학습하기"},
                {"id": "start_simulation", "label": "시뮬레이션 시작하기"}
            ]
        }
        
    async def portfolio_basics_stage(self) -> Dict[str, Any]:
        """포트폴리오 기초"""
        portfolio_lesson = f"""
💼 포트폴리오 구성의 기본

🏛️ 버핏: "계란을 한 바구니에 담지 마세요"

📈 분산투자의 원칙:
1. 업종 분산 (IT, 금융, 제조업 등)
2. 지역 분산 (국내, 해외)
3. 자산 유형 분산 (주식, 채권, 현금)

현재 포트폴리오:
💵 현금: {self.tutorial_portfolio['cash']:,}원
📊 주식: {len(self.tutorial_portfolio['assets'])}개 종목
💰 총 자산: {self.tutorial_portfolio['total_value']:,}원
        """
        
        # 추천 포트폴리오 구성
        recommended_portfolio = [
            {"name": "삼성전자", "sector": "IT", "allocation": "30%", "reason": "안정적인 대형주"},
            {"name": "KB금융", "sector": "금융", "allocation": "20%", "reason": "배당 수익률 우수"},
            {"name": "현대차", "sector": "제조", "allocation": "20%", "reason": "저평가 우량주"},
            {"name": "KODEX 200 ETF", "sector": "ETF", "allocation": "20%", "reason": "시장 평균 추종"},
            {"name": "현금", "sector": "현금", "allocation": "10%", "reason": "비상금"}
        ]
        
        # 감정 상태 변화
        self.emotional_state["confidence"] += 1
        self.emotional_state["patience"] += 1
        
        return {
            "lesson": portfolio_lesson,
            "recommended_portfolio": recommended_portfolio,
            "current_portfolio": self.tutorial_portfolio,
            "emotional_state": self.emotional_state,
            "buffett_tip": "🏛️ 버핏: \"처음에는 3-4개 종목으로 시작하세요. 너무 많으면 관리가 어렵습니다.\"",
            "actions": [
                {"id": "build_portfolio", "label": "포트폴리오 구성하기"},
                {"id": "practice_more", "label": "더 연습하기"}
            ]
        }
        
    async def market_simulation_stage(self) -> Dict[str, Any]:
        """시장 시뮬레이션"""
        # 시뮬레이션 시나리오
        simulation_events = [
            {
                "day": 1,
                "event": "평온한 시장",
                "market_change": "+0.5%",
                "portfolio_change": "+0.3%",
                "emotion_trigger": "calm"
            },
            {
                "day": 5,
                "event": "미국 금리 인상 우려",
                "market_change": "-3.2%",
                "portfolio_change": "-2.8%",
                "emotion_trigger": "fear"
            },
            {
                "day": 10,
                "event": "기업 실적 호조",
                "market_change": "+2.1%",
                "portfolio_change": "+2.5%",
                "emotion_trigger": "greed"
            },
            {
                "day": 15,
                "event": "지정학적 리스크",
                "market_change": "-5.5%",
                "portfolio_change": "-4.9%",
                "emotion_trigger": "panic"
            },
            {
                "day": 20,
                "event": "시장 회복",
                "market_change": "+4.2%",
                "portfolio_change": "+5.1%",
                "emotion_trigger": "relief"
            }
        ]
        
        # 현재 시뮬레이션 진행 상황
        current_event = simulation_events[2]  # 10일차 예시
        
        # 포트폴리오 현황
        portfolio_status = {
            "initial_value": 1000000,
            "current_value": 1025000,
            "total_return": 25000,
            "return_percent": 2.5,
            "best_performer": {"name": "삼성전자", "return": "+5.2%"},
            "worst_performer": {"name": "KB금융", "return": "-1.3%"}
        }
        
        # 버핏의 시장 상황별 조언
        market_advice = {
            "fear": "🏛️ \"두려워할 때 탐욕스럽게 행동하세요. 좋은 기업이 세일할 때입니다.\"",
            "greed": "🏛️ \"탐욕스러울 때 두려워하세요. 과열된 시장은 위험합니다.\"",
            "panic": "🏛️ \"패닉은 좋은 투자자의 적입니다. 침착하게 기회를 찾으세요.\"",
            "relief": "🏛️ \"안도감에 방심하지 마세요. 원칙을 유지하세요.\""
        }
        
        return {
            "simulation_events": simulation_events,
            "current_event": current_event,
            "portfolio_status": portfolio_status,
            "emotional_state": self.emotional_state,
            "buffett_advice": market_advice.get(current_event["emotion_trigger"], market_advice["fear"]),
            "choices": [
                {"id": "hold", "label": "현재 포트폴리오 유지"},
                {"id": "buy_more", "label": "추가 매수"},
                {"id": "sell_some", "label": "일부 매도"},
                {"id": "rebalance", "label": "포트폴리오 재조정"}
            ],
            "simulation_progress": "10/20 days"
        }
        
    async def graduation_stage(self) -> Dict[str, Any]:
        """졸업 스테이지"""
        # 최종 성과 정리
        final_results = {
            "initial_capital": 1000000,
            "final_value": 1052000,
            "total_return": 52000,
            "return_percent": 5.2,
            "experience_gained": 1000,
            "risks_unlocked": ["시장 공포", "분산 투자", "감정 조절"],
            "skills_learned": [
                "기본적 재무제표 분석",
                "포트폴리오 구성",
                "리스크 관리 기초",
                "장기 투자 사고"
            ]
        }
        
        # 버핏의 졸업 메시지
        graduation_message = f"""
🏛️ 워런 버핏: "{self.player.name}님, 축하합니다!

튜토리얼을 성공적으로 완료하셨습니다.

🏆 달성한 성과:
• 투자 수익률: +{final_results['return_percent']}%
• 해제한 리스크: {len(final_results['risks_unlocked'])}개
• 획득한 경험치: {final_results['experience_gained']} XP

💎 당신이 배운 가장 중요한 교훈:
1. 투자는 단순하지만 쉽지 않습니다
2. 감정을 조절하는 것이 성공의 열쇠입니다
3. 장기적 관점이 부를 만듭니다

🚀 다음 단계:
이제 실전 투자를 시작할 준비가 되었습니다.
항상 원칙을 기억하고, 꾸준히 학습하세요.

행운을 빕니다!"
        """
        
        # 졸업 보상
        rewards = {
            "title": "투자 입문자",
            "badge": "버핏의 제자",
            "unlock_features": [
                "real_portfolio",  # 실전 포트폴리오
                "advanced_risks",  # 고급 리스크
                "market_analysis",  # 시장 분석 도구
                "community_access"  # 커뮤니티 접근
            ],
            "special_item": "버핏의 투자 원칙 25가지"
        }
        
        return {
            "graduation_message": graduation_message,
            "final_results": final_results,
            "rewards": rewards,
            "emotional_state": {
                "confidence": 8,
                "fear": 3,
                "greed": 4,
                "patience": 7
            },
            "next_steps": [
                {"id": "start_real", "label": "실전 투자 시작하기"},
                {"id": "explore_more", "label": "더 학습하기"},
                {"id": "join_community", "label": "커뮤니티 가입하기"}
            ]
        }
        
    async def handle_choice(self, choice_id: str, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """플레이어 선택 처리"""
        # 선택에 따른 감정 상태 변화
        emotion_changes = {
            "buy_more": {"greed": +1, "fear": -1},
            "sell_some": {"fear": +1, "greed": -1},
            "hold": {"patience": +1},
            "rebalance": {"confidence": +1, "patience": +1}
        }
        
        if choice_id in emotion_changes:
            for emotion, change in emotion_changes[choice_id].items():
                self.emotional_state[emotion] = max(1, min(10, 
                    self.emotional_state[emotion] + change))
                    
        # 선택에 따른 버핏의 피드백
        feedback = {
            "buy_more": "🏛️ \"두려울 때 매수하는 것, 좋은 판단입니다!\"",
            "sell_some": "🏛️ \"자신의 감정을 돌아보세요. 두려움 때문인가요?\"",
            "hold": "🏛️ \"인내심이 보상을 가져다 줍니다. 좋아요!\"",
            "rebalance": "🏛️ \"주기적인 재조정은 현명한 전략입니다.\""
        }
        
        return {
            "choice_made": choice_id,
            "buffett_feedback": feedback.get(choice_id, "🏛️ \"항상 원칙에 따라 행동하세요.\""),
            "emotional_state": self.emotional_state,
            "continue": True
        }