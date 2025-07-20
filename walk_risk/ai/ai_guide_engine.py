"""
AI Guide Engine - Main system for providing personalized investment advice
"""
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from .mentor_personas import MentorLibrary, MentorPersona, InvestmentStyle, MentorPersonality
from ..models.player.base import Player
from ..models.risk.base import Risk
from ..models.portfolio.assets import Asset
from ..utils.logger import logger


class GuideContext(Enum):
    """Context for AI guidance"""
    RISK_ANALYSIS = "risk_analysis"
    PORTFOLIO_REVIEW = "portfolio_review"
    MARKET_EVENT = "market_event"
    UNLOCK_CHALLENGE = "unlock_challenge"
    GENERAL_ADVICE = "general_advice"
    EDUCATIONAL = "educational"


class GuidanceType(Enum):
    """Type of guidance provided"""
    ADVICE = "advice"
    WARNING = "warning"
    ENCOURAGEMENT = "encouragement"
    EDUCATION = "education"
    CHALLENGE_HINT = "challenge_hint"


@dataclass
class GuidanceRequest:
    """Request for AI guidance"""
    player_id: str
    context: GuideContext
    guidance_type: GuidanceType
    data: Dict[str, Any] = field(default_factory=dict)
    preferred_mentor: Optional[str] = None
    urgency: float = 0.5  # 0-1 scale
    

@dataclass
class GuidanceResponse:
    """Response from AI guide"""
    mentor_id: str
    mentor_name: str
    message: str
    quote: Optional[str] = None
    confidence: float = 0.8
    follow_up_questions: List[str] = field(default_factory=list)
    educational_links: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mentor_id': self.mentor_id,
            'mentor_name': self.mentor_name,
            'message': self.message,
            'quote': self.quote,
            'confidence': self.confidence,
            'follow_up_questions': self.follow_up_questions,
            'educational_links': self.educational_links,
            'timestamp': self.timestamp.isoformat()
        }


class AIGuideEngine:
    """Main AI guide engine for personalized investment advice"""
    
    def __init__(self):
        self.mentor_library = MentorLibrary()
        self.player_mentor_preferences: Dict[str, List[str]] = {}
        self.guidance_history: Dict[str, List[GuidanceResponse]] = {}
        self.mentor_usage_stats: Dict[str, int] = {}
        
        # Initialize mentor usage tracking
        for mentor_id in self.mentor_library.mentors.keys():
            self.mentor_usage_stats[mentor_id] = 0
    
    async def provide_guidance(self, request: GuidanceRequest) -> GuidanceResponse:
        """Provide personalized guidance based on request"""
        try:
            # Select appropriate mentor
            mentor = self._select_mentor_for_request(request)
            
            # Generate guidance message
            message = await self._generate_guidance_message(mentor, request)
            
            # Get appropriate quote
            quote = self._get_contextual_quote(mentor, request)
            
            # Create response
            response = GuidanceResponse(
                mentor_id=mentor.name.lower().replace(' ', '_'),
                mentor_name=mentor.name,
                message=message,
                quote=quote,
                confidence=self._calculate_confidence(mentor, request),
                follow_up_questions=self._generate_follow_up_questions(mentor, request),
                educational_links=self._get_educational_links(request.context)
            )
            
            # Track usage and store response
            self._track_guidance_usage(request.player_id, mentor, response)
            
            return response
            
        except Exception as e:
            logger.error(f"AI 가이드 생성 실패: {e}")
            return self._create_fallback_response(request)
    
    def _select_mentor_for_request(self, request: GuidanceRequest) -> MentorPersona:
        """Select most appropriate mentor for the request"""
        
        # Use preferred mentor if specified and available
        if request.preferred_mentor and request.preferred_mentor in self.mentor_library.mentors:
            return self.mentor_library.mentors[request.preferred_mentor]
        
        # Get player preferences
        player_preferences = self.player_mentor_preferences.get(request.player_id, [])
        
        # Filter mentors based on context
        suitable_mentors = self._filter_mentors_by_context(request.context, request.data)
        
        # Apply player preferences
        if player_preferences:
            preferred_mentors = [m for m in suitable_mentors if m.name.lower().replace(' ', '_') in player_preferences]
            if preferred_mentors:
                suitable_mentors = preferred_mentors
        
        # Select mentor (balance between suitability and variety)
        if suitable_mentors:
            # Weight by inverse usage to promote variety
            weights = []
            for mentor in suitable_mentors:
                mentor_id = mentor.name.lower().replace(' ', '_')
                usage_count = self.mentor_usage_stats.get(mentor_id, 0)
                weight = 1.0 / (usage_count + 1)  # Inverse usage weighting
                weights.append(weight)
            
            # Weighted random selection
            selected_mentor = random.choices(suitable_mentors, weights=weights)[0]
        else:
            # Fallback to Buffett for conservative advice
            selected_mentor = self.mentor_library.mentors['buffett']
        
        return selected_mentor
    
    def _filter_mentors_by_context(self, context: GuideContext, data: Dict[str, Any]) -> List[MentorPersona]:
        """Filter mentors based on context and data"""
        all_mentors = list(self.mentor_library.mentors.values())
        
        if context == GuideContext.RISK_ANALYSIS:
            # Risk analysis: prefer analytical mentors
            return [m for m in all_mentors if m.personality in [MentorPersonality.ANALYTICAL, MentorPersonality.CONSERVATIVE]]
        
        elif context == GuideContext.PORTFOLIO_REVIEW:
            # Portfolio review: prefer balanced mentors
            return [m for m in all_mentors if m.personality in [MentorPersonality.BALANCED, MentorPersonality.PATIENT]]
        
        elif context == GuideContext.MARKET_EVENT:
            # Market events: prefer dynamic or contrarian mentors
            volatility = data.get('volatility', 0.5)
            if volatility > 0.7:
                return [m for m in all_mentors if m.personality in [MentorPersonality.CONSERVATIVE, MentorPersonality.PATIENT]]
            else:
                return [m for m in all_mentors if m.personality in [MentorPersonality.DYNAMIC, MentorPersonality.AGGRESSIVE]]
        
        elif context == GuideContext.UNLOCK_CHALLENGE:
            # Challenges: prefer encouraging mentors
            return [m for m in all_mentors if m.personality in [MentorPersonality.DYNAMIC, MentorPersonality.BALANCED]]
        
        elif context == GuideContext.EDUCATIONAL:
            # Education: prefer patient, analytical mentors
            return [m for m in all_mentors if m.personality in [MentorPersonality.PATIENT, MentorPersonality.ANALYTICAL]]
        
        else:
            # General advice: all mentors suitable
            return all_mentors
    
    async def _generate_guidance_message(self, mentor: MentorPersona, request: GuidanceRequest) -> str:
        """Generate personalized guidance message"""
        
        # Get base message template based on context
        base_message = self._get_base_message_template(mentor, request)
        
        # Personalize with mentor's style
        personalized_message = self._apply_mentor_style(mentor, base_message, request)
        
        return personalized_message
    
    def _get_base_message_template(self, mentor: MentorPersona, request: GuidanceRequest) -> str:
        """Get base message template for the context"""
        
        if request.context == GuideContext.RISK_ANALYSIS:
            risk_level = request.data.get('risk_level', 'medium')
            if risk_level == 'high':
                return "높은 리스크를 감지했습니다. 신중한 분석과 대응이 필요합니다."
            elif risk_level == 'low':
                return "현재 리스크 수준이 낮습니다. 좋은 기회를 모색해볼 시점입니다."
            else:
                return "적정한 리스크 수준입니다. 균형잡힌 접근이 필요합니다."
        
        elif request.context == GuideContext.PORTFOLIO_REVIEW:
            portfolio_health = request.data.get('health_score', 0.7)
            if portfolio_health < 0.5:
                return "포트폴리오 개선이 필요합니다. 리밸런싱을 고려해보세요."
            elif portfolio_health > 0.8:
                return "포트폴리오가 잘 구성되어 있습니다. 현재 전략을 유지하세요."
            else:
                return "포트폴리오가 적절합니다. 몇 가지 개선점을 고려해보세요."
        
        elif request.context == GuideContext.MARKET_EVENT:
            event_type = request.data.get('event_type', 'normal')
            if event_type == 'crash':
                return "시장 급락 상황입니다. 냉정함을 유지하고 장기적 관점을 갖세요."
            elif event_type == 'rally':
                return "시장이 급등하고 있습니다. 과도한 탐욕을 경계하세요."
            else:
                return "시장 상황을 지켜보며 기회를 모색하세요."
        
        elif request.context == GuideContext.UNLOCK_CHALLENGE:
            difficulty = request.data.get('difficulty', 0.5)
            if difficulty > 0.7:
                return "도전적인 문제입니다. 차근차근 접근하고 기본 원칙을 기억하세요."
            else:
                return "좋은 학습 기회입니다. 경험을 쌓아가며 실력을 향상시키세요."
        
        elif request.context == GuideContext.EDUCATIONAL:
            return "투자의 기본 원칙을 이해하는 것이 중요합니다. 꾸준한 학습이 성공의 열쇠입니다."
        
        else:
            return "투자에서 가장 중요한 것은 인내심과 규율입니다."
    
    def _apply_mentor_style(self, mentor: MentorPersona, base_message: str, request: GuidanceRequest) -> str:
        """Apply mentor's personal style to the message"""
        
        # Add mentor's philosophy context
        styled_message = f"{base_message}\n\n"
        
        # Add mentor-specific advice style
        if mentor.personality == MentorPersonality.CONSERVATIVE:
            styled_message += "안전을 최우선으로 고려하세요. "
        elif mentor.personality == MentorPersonality.AGGRESSIVE:
            styled_message += "대담하게 기회를 잡되, 계산된 리스크를 취하세요. "
        elif mentor.personality == MentorPersonality.ANALYTICAL:
            styled_message += "데이터와 분석을 바탕으로 의사결정하세요. "
        elif mentor.personality == MentorPersonality.PATIENT:
            styled_message += "서두르지 말고 장기적 관점을 유지하세요. "
        elif mentor.personality == MentorPersonality.DYNAMIC:
            styled_message += "변화하는 시장에 유연하게 대응하세요. "
        
        # Add specific advice based on mentor's investment style
        if mentor.investment_style == InvestmentStyle.VALUE:
            styled_message += "내재가치를 중심으로 판단하고, 안전마진을 확보하세요."
        elif mentor.investment_style == InvestmentStyle.GROWTH:
            styled_message += "성장 가능성을 면밀히 분석하고, 트렌드를 파악하세요."
        elif mentor.investment_style == InvestmentStyle.RISK_PARITY:
            styled_message += "리스크를 균형있게 분산하고, 상관관계를 고려하세요."
        
        return styled_message
    
    def _get_contextual_quote(self, mentor: MentorPersona, request: GuidanceRequest) -> Optional[str]:
        """Get appropriate quote for the context"""
        
        # Map context to situation keywords
        situation_keywords = {
            GuideContext.RISK_ANALYSIS: "analysis,decision",
            GuideContext.PORTFOLIO_REVIEW: "portfolio,strategy",
            GuideContext.MARKET_EVENT: "market_crash,fear,opportunity",
            GuideContext.UNLOCK_CHALLENGE: "confidence,encouragement",
            GuideContext.EDUCATIONAL: "learning,wisdom",
            GuideContext.GENERAL_ADVICE: "general,wisdom"
        }
        
        keywords = situation_keywords.get(request.context, "general")
        return mentor.select_appropriate_quote(keywords)
    
    def _calculate_confidence(self, mentor: MentorPersona, request: GuidanceRequest) -> float:
        """Calculate confidence level for the guidance"""
        
        base_confidence = 0.8
        
        # Adjust based on mentor's expertise areas
        if request.context == GuideContext.RISK_ANALYSIS and "risk_management" in mentor.strengths:
            base_confidence += 0.1
        elif request.context == GuideContext.PORTFOLIO_REVIEW and "diversification" in mentor.strengths:
            base_confidence += 0.1
        elif request.context == GuideContext.MARKET_EVENT and "market_timing" in mentor.strengths:
            base_confidence += 0.1
        
        # Adjust based on data quality
        data_quality = request.data.get('data_quality', 0.8)
        confidence = base_confidence * data_quality
        
        return min(1.0, max(0.5, confidence))
    
    def _generate_follow_up_questions(self, mentor: MentorPersona, request: GuidanceRequest) -> List[str]:
        """Generate follow-up questions to encourage learning"""
        
        questions = []
        
        if request.context == GuideContext.RISK_ANALYSIS:
            questions = [
                "어떤 추가 정보가 필요하다고 생각하시나요?",
                "이 리스크에 대한 헤징 전략을 고려해보셨나요?",
                "유사한 상황에서 어떻게 대응했었나요?"
            ]
        
        elif request.context == GuideContext.PORTFOLIO_REVIEW:
            questions = [
                "포트폴리오의 목표 수익률과 리스크 수준은 어떻게 되나요?",
                "리밸런싱 주기를 어떻게 설정하고 계신가요?",
                "현재 자산 배분에 만족하시나요?"
            ]
        
        elif request.context == GuideContext.MARKET_EVENT:
            questions = [
                "이 시장 상황이 언제까지 지속될 것 같나요?",
                "포트폴리오에 어떤 영향을 미칠 것 같나요?",
                "기회 요소는 무엇이라고 생각하시나요?"
            ]
        
        # Return 1-2 random questions
        return random.sample(questions, min(2, len(questions))) if questions else []
    
    def _get_educational_links(self, context: GuideContext) -> List[str]:
        """Get educational resource links for the context"""
        
        # In a real implementation, these would be actual educational resources
        links = {
            GuideContext.RISK_ANALYSIS: [
                "리스크 관리 기초",
                "VaR 계산 방법",
                "포트폴리오 리스크 측정"
            ],
            GuideContext.PORTFOLIO_REVIEW: [
                "자산 배분 전략",
                "리밸런싱 가이드",
                "포트폴리오 최적화"
            ],
            GuideContext.MARKET_EVENT: [
                "시장 사이클 이해",
                "변동성 대응 전략",
                "시장 타이밍 vs 장기 투자"
            ],
            GuideContext.EDUCATIONAL: [
                "투자 기초 강의",
                "재무제표 읽기",
                "투자 심리학"
            ]
        }
        
        return links.get(context, [])
    
    def _track_guidance_usage(self, player_id: str, mentor: MentorPersona, response: GuidanceResponse) -> None:
        """Track guidance usage for analytics and personalization"""
        
        # Update mentor usage stats
        mentor_id = mentor.name.lower().replace(' ', '_')
        self.mentor_usage_stats[mentor_id] += 1
        
        # Store guidance history
        if player_id not in self.guidance_history:
            self.guidance_history[player_id] = []
        
        self.guidance_history[player_id].append(response)
        
        # Limit history size
        if len(self.guidance_history[player_id]) > 100:
            self.guidance_history[player_id] = self.guidance_history[player_id][-100:]
        
        # Update player mentor preferences based on usage
        if player_id not in self.player_mentor_preferences:
            self.player_mentor_preferences[player_id] = []
        
        # Add mentor to preferences if not already there
        if mentor_id not in self.player_mentor_preferences[player_id]:
            self.player_mentor_preferences[player_id].append(mentor_id)
    
    def _create_fallback_response(self, request: GuidanceRequest) -> GuidanceResponse:
        """Create fallback response when main generation fails"""
        
        return GuidanceResponse(
            mentor_id="system",
            mentor_name="AI 가이드",
            message="죄송합니다. 일시적인 문제로 개인화된 조언을 제공할 수 없습니다. 기본적인 투자 원칙을 기억하세요: 분산투자, 장기적 관점, 그리고 자신만의 투자 원칙을 지키는 것이 중요합니다.",
            confidence=0.3,
            follow_up_questions=["어떤 구체적인 도움이 필요하신가요?"]
        )
    
    # Public API methods
    
    def get_mentor_recommendations(self, player_id: str, context: GuideContext = GuideContext.GENERAL_ADVICE) -> List[Dict[str, Any]]:
        """Get mentor recommendations for player"""
        
        # Get player's preferred mentors
        player_preferences = self.player_mentor_preferences.get(player_id, [])
        
        # Get suitable mentors for context
        suitable_mentors = self._filter_mentors_by_context(context, {})
        
        recommendations = []
        for mentor in suitable_mentors:
            mentor_id = mentor.name.lower().replace(' ', '_')
            
            # Calculate recommendation score
            score = 0.5  # Base score
            
            # Boost score for preferred mentors
            if mentor_id in player_preferences:
                score += 0.3
            
            # Boost score for less used mentors (variety)
            usage_count = self.mentor_usage_stats.get(mentor_id, 0)
            if usage_count == 0:
                score += 0.2
            elif usage_count < 5:
                score += 0.1
            
            recommendations.append({
                'mentor_id': mentor_id,
                'name': mentor.name,
                'title': mentor.title,
                'investment_style': mentor.investment_style.value,
                'personality': mentor.personality.value,
                'philosophy': mentor.philosophy,
                'recommendation_score': score
            })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations
    
    def get_guidance_history(self, player_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get player's guidance history"""
        
        history = self.guidance_history.get(player_id, [])
        recent_history = history[-limit:] if len(history) > limit else history
        
        return [response.to_dict() for response in recent_history]
    
    def update_mentor_preference(self, player_id: str, mentor_id: str, preference: str) -> bool:
        """Update player's mentor preference (like/dislike)"""
        
        if player_id not in self.player_mentor_preferences:
            self.player_mentor_preferences[player_id] = []
        
        preferences = self.player_mentor_preferences[player_id]
        
        if preference == "like":
            if mentor_id not in preferences:
                preferences.append(mentor_id)
        elif preference == "dislike":
            if mentor_id in preferences:
                preferences.remove(mentor_id)
        
        return True
    
    def get_mentor_stats(self) -> Dict[str, Any]:
        """Get mentor usage statistics"""
        
        total_usage = sum(self.mentor_usage_stats.values())
        
        stats = {
            'total_guidance_provided': total_usage,
            'mentor_usage': self.mentor_usage_stats.copy(),
            'most_popular_mentor': max(self.mentor_usage_stats.items(), key=lambda x: x[1])[0] if self.mentor_usage_stats else None,
            'least_used_mentor': min(self.mentor_usage_stats.items(), key=lambda x: x[1])[0] if self.mentor_usage_stats else None
        }
        
        return stats