"""Puzzle Tutorial - 퍼즐 시스템을 튜토리얼에 통합"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
from datetime import datetime

from ..core.risk_puzzle.puzzle_engine import (
    PuzzleEngine, RiskPuzzle, PuzzleDifficulty, PuzzleType
)
from ..core.risk_puzzle.investigation import InvestigationSystem, ClueType
from ..core.risk_puzzle.hypothesis import (
    Hypothesis, HypothesisValidator, HypothesisType, ActionType
)
from ..models.player.base import Player
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class PuzzleTutorialProgress:
    """퍼즐 튜토리얼 진행 상황"""
    has_seen_intro: bool = False
    first_puzzle_completed: bool = False
    investigation_skills_learned: bool = False
    hypothesis_skills_learned: bool = False
    validation_experience_gained: bool = False


class PuzzleTutorial:
    """퍼즐 시스템 튜토리얼 관리자"""
    
    def __init__(self, tutorial_manager, game_manager):
        self.tutorial_manager = tutorial_manager
        self.game_manager = game_manager
        
        # 퍼즐 시스템 초기화
        self.puzzle_engine = PuzzleEngine()
        self.investigation_system = InvestigationSystem(player_level=1)  # 초보자
        self.hypothesis_validator = HypothesisValidator()
        
        # 튜토리얼 상태
        self.current_puzzle = None
        self.discovered_clues = []
        self.tutorial_progress = PuzzleTutorialProgress()
        
    async def introduce_puzzle_concept(self, player: Player) -> Dict[str, Any]:
        """퍼즐 컨셉 소개"""
        logger.info(f"퍼즐 컨셉 소개 시작: {player.name}")
        
        introduction = {
            "stage_name": "🔍 투자 퍼즐 입문",
            "mentor_message": """
🏛️ 워런 버핏: "{player.name}님, 이제 진짜 투자의 세계를 보여드리겠습니다.

투자는 단순히 주식을 사고파는 것이 아닙니다.
그것은 마치 탐정이 사건을 해결하는 것과 같습니다.

🔍 시장에서 일어나는 모든 일에는 이유가 있습니다:
• 주가가 떨어진다면? → 원인이 있습니다
• 거래량이 급증한다면? → 배경이 있습니다  
• 업종이 부진하다면? → 맥락이 있습니다

당신의 임무는 이런 '수수께끼'들을 풀어내는 것입니다.
단서를 모으고, 연결하고, 가설을 세우고, 검증하는 것이죠.

준비되셨나요? 첫 번째 투자 미스터리를 함께 풀어보겠습니다!"
            """.format(player=player).strip(),
            "key_concepts": [
                "🔍 투자 = 미스터리 해결",
                "🧩 단서 수집이 핵심",
                "💡 가설 수립과 검증",
                "📈 패턴 인식 능력 개발"
            ],
            "next_action": "first_puzzle"
        }
        
        self.tutorial_progress.has_seen_intro = True
        return introduction
    
    async def create_tutorial_puzzle(self) -> RiskPuzzle:
        """튜토리얼용 간단한 퍼즐 생성"""
        
        # 초보자용 간단한 시나리오
        tutorial_event = {
            'symbol': 'NAVER',
            'change_percent': -6.2,
            'volume_ratio': 1.8,
            'market_sentiment': 'neutral',
            'time': '장 마감 후',
            'sector_divergence': False
        }
        
        puzzle = self.puzzle_engine.create_puzzle(
            symbol='NAVER',
            market_event=tutorial_event,
            difficulty=PuzzleDifficulty.BEGINNER  # 가장 쉬운 난이도
        )
        
        # 튜토리얼 전용 설정
        puzzle.title = "🔰 첫 번째 미스터리: NAVER -6.2% 하락"
        puzzle.description = f"""
📚 [튜토리얼 퍼즐]

📊 상황: NAVER가 장 마감 후 -6.2% 하락했습니다.
📈 거래량: 평소 대비 1.8배
🌍 시장 전체: 보통
⏰ 시간: 장 마감 후

🎯 미션: 
NAVER 주가 하락의 진짜 원인을 찾아보세요.
단서를 수집하고 올바른 결론을 내리는 것이 목표입니다.

💡 힌트: 
이것은 연습이니까 천천히 해보세요. 
실패해도 괜찮습니다!
        """.strip()
        
        self.current_puzzle = puzzle
        logger.info(f"튜토리얼 퍼즐 생성: {puzzle.title}")
        
        return puzzle
    
    async def guided_investigation(self, player: Player) -> List[Dict]:
        """가이드된 단서 조사 과정"""
        investigation_steps = []
        
        # 1단계: 뉴스 조사 (기본)
        news_step = await self._guide_clue_investigation(
            ClueType.NEWS,
            "📰 첫 번째로 뉴스를 확인해보겠습니다.",
            "뉴스는 가장 기본적인 정보원입니다. 항상 여기서 시작하세요."
        )
        investigation_steps.append(news_step)
        
        # 2단계: 재무 데이터 조사 (레벨 3 필요하지만 튜토리얼이므로 허용)
        if len(self.discovered_clues) >= 1:
            financial_step = await self._guide_clue_investigation(
                ClueType.FINANCIAL,
                "📊 이제 재무 데이터를 살펴보겠습니다.",
                "숫자는 거짓말하지 않습니다. 실제 실적을 확인해보세요."
            )
            investigation_steps.append(financial_step)
        
        # 3단계: 차트 분석 (레벨 5 필요하지만 튜토리얼이므로 허용)
        if len(self.discovered_clues) >= 2:
            chart_step = await self._guide_clue_investigation(
                ClueType.CHART,
                "📈 마지막으로 차트 패턴을 분석해보겠습니다.",
                "차트는 시장의 심리를 보여줍니다."
            )
            investigation_steps.append(chart_step)
        
        self.tutorial_progress.investigation_skills_learned = True
        return investigation_steps
    
    async def _guide_clue_investigation(self, 
                                       clue_type: ClueType,
                                       intro_message: str,
                                       explanation: str) -> Dict:
        """개별 단서 조사 가이드"""
        
        # 해당 타입의 단서 찾기
        available_clue = None
        for clue in self.current_puzzle.available_clues:
            if clue.clue_type == clue_type and not clue.is_discovered:
                available_clue = clue
                break
        
        if not available_clue:
            return {
                "success": False,
                "message": f"{clue_type.value} 단서를 찾을 수 없습니다"
            }
        
        # 튜토리얼에서는 에너지 제한 무시
        success, message, result = self.investigation_system.investigate(
            available_clue, use_boost=True  # 튜토리얼 부스트
        )
        
        if success:
            self.discovered_clues.append(available_clue)
            
            return {
                "success": True,
                "intro_message": intro_message,
                "explanation": explanation,
                "clue_type": clue_type.value,
                "clue_content": result['clue_content'],
                "reliability": result['reliability'],
                "insights": result['insights'],
                "bonus_insight": result.get('bonus_insight', ''),
                "energy_spent": 0  # 튜토리얼에서는 에너지 무료
            }
        else:
            return {
                "success": False,
                "message": message
            }
    
    async def guide_hypothesis_creation(self, player: Player) -> Dict:
        """가설 수립 가이드"""
        
        # 현재까지 수집한 단서 요약
        synthesis = self.investigation_system.synthesize_clues(self.discovered_clues)
        
        guidance = {
            "stage_name": "💡 가설 수립 훈련",
            "mentor_message": f"""
🏛️ 버핏: "좋습니다, {player.name}님! 이제 수집한 정보를 바탕으로 가설을 세워봅시다.

📊 지금까지 발견한 것들:
• 수집한 단서: {len(self.discovered_clues)}개
• 전체 신뢰도: {synthesis['confidence']:.0%}
• 조사 범위: {synthesis['coverage']:.0%}

💭 가설이란 '이런 이유로 이런 일이 일어났을 것이다'라는 추론입니다.

예를 들어:
1. 'NAVER가 하락한 이유는 광고 시장 부진 때문이다'
2. 'NAVER가 하락한 이유는 일시적 차익실현 때문이다'
3. 'NAVER가 하락한 이유는 경쟁사 대비 실적 부진 때문이다'

🎯 당신이 수집한 단서들을 바탕으로 가장 그럴듯한 가설을 세워보세요!"
            """.strip(),
            "clue_summary": synthesis,
            "suggested_hypotheses": [
                {
                    "type": HypothesisType.BEARISH,
                    "statement": "NAVER는 구조적 문제로 추가 하락 예상",
                    "reasoning": "광고 시장 경쟁 심화"
                },
                {
                    "type": HypothesisType.BULLISH,
                    "statement": "NAVER는 일시적 조정으로 반등 예상",
                    "reasoning": "펀더멘털 양호한 상태"
                },
                {
                    "type": HypothesisType.NEUTRAL,
                    "statement": "NAVER는 당분간 횡보 예상",
                    "reasoning": "명확한 방향성 부족"
                }
            ]
        }
        
        self.tutorial_progress.hypothesis_skills_learned = True
        return guidance
    
    async def validate_tutorial_hypothesis(self,
                                          hypothesis_choice: int,
                                          player: Player) -> Dict:
        """튜토리얼 가설 검증"""
        
        # 선택한 가설 생성
        hypothesis_templates = [
            {
                "statement": "NAVER는 구조적 문제로 추가 하락 예상",
                "type": HypothesisType.BEARISH,
                "action": ActionType.SELL
            },
            {
                "statement": "NAVER는 일시적 조정으로 반등 예상", 
                "type": HypothesisType.BULLISH,
                "action": ActionType.BUY
            },
            {
                "statement": "NAVER는 당분간 횡보 예상",
                "type": HypothesisType.NEUTRAL,
                "action": ActionType.HOLD
            }
        ]
        
        selected_template = hypothesis_templates[hypothesis_choice]
        
        hypothesis = Hypothesis(
            hypothesis_id=f"tutorial_{datetime.now().timestamp()}",
            puzzle_id=self.current_puzzle.puzzle_id,
            statement=selected_template["statement"],
            reasoning="튜토리얼 가설",
            hypothesis_type=selected_template["type"],
            supporting_clues=[str(id(c)) for c in self.discovered_clues],
            contradicting_clues=[],
            confidence_level=0.6,  # 초보자 수준
            predicted_outcome="튜토리얼 예측",
            time_horizon=7,
            recommended_action=selected_template["action"],
            position_size=5.0,  # 작은 포지션
            stop_loss=-3.0,
            take_profit=6.0
        )
        
        # 검증 (튜토리얼 버전 - 항상 부분적 성공)
        market_data = {
            'sentiment': 'neutral',
            'trend': 'sideways'
        }
        
        success, accuracy, feedback = self.hypothesis_validator.validate_hypothesis(
            hypothesis,
            market_data,
            self.discovered_clues
        )
        
        # 튜토리얼에서는 실패하더라도 긍정적 피드백
        if accuracy < 0.5:
            accuracy = 0.65  # 최소 점수 보장
            feedback = f"""
🎯 좋은 시도였습니다! (정확도: {accuracy:.0%})

📈 시장 결과: 예상대로 움직였습니다
💭 당신의 가설: {hypothesis.statement}

✅ 잘한 점:
• 단서를 체계적으로 수집했습니다
• 논리적인 가설을 세웠습니다
• 리스크 관리를 고려했습니다

💡 교훈:
투자는 정답을 맞히는 게임이 아닙니다.
정보를 수집하고, 분석하고, 합리적으로 판단하는 과정이 중요합니다.
이 과정을 반복하면서 점점 더 나은 투자자가 됩니다!
            """.strip()
        
        # 퍼즐 완료 처리
        self.current_puzzle.is_solved = True
        self.current_puzzle.player_hypothesis = hypothesis.statement
        self.tutorial_progress.first_puzzle_completed = True
        self.tutorial_progress.validation_experience_gained = True
        
        # 보상 계산 (튜토리얼 보너스)
        xp_earned = 200  # 튜토리얼 보너스
        skill_gained = "🔰 퍼즐 해결 입문자"
        
        return {
            "success": True,
            "accuracy": accuracy,
            "feedback": feedback,
            "xp_earned": xp_earned,
            "skill_gained": skill_gained,
            "puzzle_completed": True,
            "next_stage": "portfolio_integration"
        }
    
    async def complete_puzzle_tutorial(self, player: Player) -> Dict:
        """퍼즐 튜토리얼 완료"""
        
        completion_message = {
            "stage_name": "🎓 퍼즐 마스터 입문 완료",
            "mentor_message": f"""
🏛️ 버핏: "축하합니다, {player.name}님! 

첫 번째 투자 미스터리를 성공적으로 해결하셨습니다!

🏆 당신이 배운 것들:
✅ 투자는 정보 수집부터 시작한다
✅ 단서들을 연결하여 큰 그림을 본다  
✅ 가설을 세우고 검증하는 습관
✅ 실패해도 배움이 있다는 마음가짐

🚀 이제부터 실전입니다:
앞으로 실제 시장에서 일어나는 다양한 사건들을 
퍼즐로 만나게 될 것입니다.

각각의 퍼즐을 해결할 때마다 당신은 
더 현명한 투자자가 될 것입니다.

준비되셨나요? 진짜 투자의 세계로 함께 떠나봅시다!"
            """.strip(),
            "skills_learned": [
                "🔍 단서 수집 능력",
                "🔗 정보 연결 능력", 
                "💡 가설 수립 능력",
                "🎯 검증 경험"
            ],
            "unlocked_features": [
                "실시간 시장 퍼즐",
                "고급 조사 도구 (레벨업 시)",
                "다양한 멘토 (향후 업데이트)",
                "퍼즐 성과 추적"
            ],
            "progress_summary": {
                "intro_completed": self.tutorial_progress.has_seen_intro,
                "puzzle_completed": self.tutorial_progress.first_puzzle_completed,
                "investigation_learned": self.tutorial_progress.investigation_skills_learned,
                "hypothesis_learned": self.tutorial_progress.hypothesis_skills_learned,
                "validation_experienced": self.tutorial_progress.validation_experience_gained
            }
        }
        
        logger.info(f"퍼즐 튜토리얼 완료: {player.name}")
        return completion_message