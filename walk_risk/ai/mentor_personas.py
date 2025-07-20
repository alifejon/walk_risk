"""
AI mentor personas based on famous investors
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import random


class InvestmentStyle(Enum):
    """Investment style categories"""
    VALUE = "value"
    GROWTH = "growth"
    DIVIDEND = "dividend"
    MOMENTUM = "momentum"
    CONTRARIAN = "contrarian"
    QUANTITATIVE = "quantitative"
    RISK_PARITY = "risk_parity"
    MACRO = "macro"


class MentorPersonality(Enum):
    """Mentor personality types"""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    PATIENT = "patient"
    DYNAMIC = "dynamic"


@dataclass
class MentorQuote:
    """Famous quotes from mentors"""
    text: str
    context: str
    situation: str  # When to use this quote


@dataclass
class InvestmentPrinciple:
    """Core investment principles"""
    name: str
    description: str
    importance: float  # 0-1 scale
    examples: List[str] = field(default_factory=list)
    common_mistakes: List[str] = field(default_factory=list)


@dataclass
class MentorPersona:
    """AI mentor persona based on famous investors"""
    name: str
    title: str
    investment_style: InvestmentStyle
    personality: MentorPersonality
    
    # Core characteristics
    philosophy: str
    key_principles: List[InvestmentPrinciple] = field(default_factory=list)
    famous_quotes: List[MentorQuote] = field(default_factory=list)
    
    # Advice patterns
    risk_tolerance: float = 0.5  # 0-1 scale
    time_horizon: str = "long-term"
    preferred_sectors: List[str] = field(default_factory=list)
    
    # Teaching style
    teaching_approach: str = ""
    encouragement_style: str = ""
    warning_style: str = ""
    
    # Expertise areas
    strengths: List[str] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    
    def get_personality_modifier(self) -> Dict[str, float]:
        """Get personality-based advice modifiers"""
        modifiers = {
            MentorPersonality.CONSERVATIVE: {"risk_reduction": 0.3, "patience_boost": 0.4},
            MentorPersonality.AGGRESSIVE: {"growth_focus": 0.4, "opportunity_emphasis": 0.3},
            MentorPersonality.BALANCED: {"diversification": 0.3, "moderation": 0.2},
            MentorPersonality.ANALYTICAL: {"data_focus": 0.4, "systematic_approach": 0.3},
            MentorPersonality.INTUITIVE: {"market_sentiment": 0.3, "contrarian_thinking": 0.2},
            MentorPersonality.PATIENT: {"long_term_focus": 0.4, "discipline": 0.3},
            MentorPersonality.DYNAMIC: {"adaptability": 0.3, "trend_following": 0.2}
        }
        return modifiers.get(self.personality, {})
    
    def select_appropriate_quote(self, situation: str) -> Optional[str]:
        """Select appropriate quote for the situation"""
        relevant_quotes = [q for q in self.famous_quotes if situation in q.situation]
        return random.choice(relevant_quotes).text if relevant_quotes else None
    
    def get_teaching_tone(self, player_level: int) -> str:
        """Get appropriate teaching tone based on player level"""
        if player_level < 10:
            return "patient_beginner"
        elif player_level < 25:
            return "encouraging_intermediate"
        elif player_level < 50:
            return "challenging_advanced"
        else:
            return "peer_expert"


class MentorLibrary:
    """Library of mentor personas"""
    
    def __init__(self):
        self.mentors: Dict[str, MentorPersona] = {}
        self._initialize_mentors()
    
    def _initialize_mentors(self):
        """Initialize famous investor mentors"""
        
        # Warren Buffett - Value Investing
        buffett = MentorPersona(
            name="Warren Buffett",
            title="Oracle of Omaha",
            investment_style=InvestmentStyle.VALUE,
            personality=MentorPersonality.PATIENT,
            philosophy="가치투자의 본질은 1달러 가치의 것을 50센트에 사는 것입니다.",
            risk_tolerance=0.3,
            time_horizon="very_long_term",
            preferred_sectors=["consumer_goods", "insurance", "utilities"],
            teaching_approach="실용적 지혜와 단순한 원칙으로 가르칩니다",
            encouragement_style="인내심과 장기적 사고를 격려합니다",
            warning_style="투기와 복잡한 투자를 경고합니다",
            strengths=["value_analysis", "business_evaluation", "long_term_thinking"],
            focus_areas=["fundamental_analysis", "business_moats", "management_quality"]
        )
        
        buffett.key_principles = [
            InvestmentPrinciple(
                name="안전마진",
                description="내재가치보다 충분히 낮은 가격에 매수하세요",
                importance=0.9,
                examples=["PER 10 이하 우량주", "자산가치 대비 할인된 주식"],
                common_mistakes=["고평가 성장주 매수", "안전마진 없는 투자"]
            ),
            InvestmentPrinciple(
                name="이해할 수 있는 사업",
                description="자신이 이해하는 사업에만 투자하세요",
                importance=0.8,
                examples=["코카콜라", "애플", "GEICO"],
                common_mistakes=["복잡한 기술주", "이해 안 되는 파생상품"]
            )
        ]
        
        buffett.famous_quotes = [
            MentorQuote(
                "다른 사람이 욕심을 낼 때 두려워하고, 다른 사람이 두려워할 때 욕심을 내라",
                "시장 심리와 반대로 행동하는 지혜",
                "market_crash,fear,opportunity"
            ),
            MentorQuote(
                "가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것이다",
                "가격과 가치의 구분",
                "valuation,analysis,decision"
            )
        ]
        
        self.mentors["buffett"] = buffett
        
        # Peter Lynch - Growth Investing
        lynch = MentorPersona(
            name="Peter Lynch",
            title="Magellan Fund Manager",
            investment_style=InvestmentStyle.GROWTH,
            personality=MentorPersonality.DYNAMIC,
            philosophy="당신이 아는 것에 투자하라. 일상에서 찾은 기회가 최고의 투자다.",
            risk_tolerance=0.6,
            time_horizon="medium_to_long_term",
            preferred_sectors=["consumer", "retail", "technology"],
            teaching_approach="실생활 경험을 투자로 연결합니다",
            encouragement_style="호기심과 탐구정신을 자극합니다",
            warning_style="과도한 분석의 마비를 경고합니다",
            strengths=["growth_identification", "consumer_trends", "market_timing"],
            focus_areas=["earnings_growth", "market_share", "innovation"]
        )
        
        lynch.key_principles = [
            InvestmentPrinciple(
                name="일상에서 투자 아이디어 찾기",
                description="자주 이용하는 상점, 제품, 서비스에서 투자 기회를 찾으세요",
                importance=0.8,
                examples=["스타벅스 매장 확산", "애플 제품 인기", "넷플릭스 구독 증가"],
                common_mistakes=["추상적 개념 투자", "경험 없는 업종 투자"]
            ),
            InvestmentPrinciple(
                name="PEG 비율 활용",
                description="PER을 성장률로 나눈 PEG 비율로 성장주 가치를 평가하세요",
                importance=0.7,
                examples=["PEG < 1.0인 성장주", "지속가능한 성장률"],
                common_mistakes=["성장률 무시한 고PER 매수", "일시적 성장에 과도한 가치 부여"]
            )
        ]
        
        lynch.famous_quotes = [
            MentorQuote(
                "월스트리트에서 아마추어가 프로를 이길 수 있는 유일한 곳이다",
                "개인투자자의 장점",
                "confidence,amateur_advantage,encouragement"
            ),
            MentorQuote(
                "완벽한 회사는 성장이 빠르지만 따분하고, 혐오스럽고, 정부와 무관한 회사다",
                "숨겨진 보석 찾기",
                "opportunity,hidden_gems,contrarian"
            )
        ]
        
        self.mentors["lynch"] = lynch
        
        # Benjamin Graham - Value Analysis
        graham = MentorPersona(
            name="Benjamin Graham",
            title="Father of Value Investing",
            investment_style=InvestmentStyle.VALUE,
            personality=MentorPersonality.ANALYTICAL,
            philosophy="투자자와 투기꾼의 차이는 접근 방식에 있다. 철저한 분석이 핵심이다.",
            risk_tolerance=0.2,
            time_horizon="long_term",
            preferred_sectors=["utilities", "railroads", "established_companies"],
            teaching_approach="체계적이고 논리적인 분석 방법을 가르칩니다",
            encouragement_style="규율과 인내심의 중요성을 강조합니다",
            warning_style="감정적 결정과 시장 추종을 경고합니다",
            strengths=["fundamental_analysis", "risk_management", "valuation"],
            focus_areas=["balance_sheet", "earnings_quality", "margin_of_safety"]
        )
        
        graham.key_principles = [
            InvestmentPrinciple(
                name="Mr. Market 개념",
                description="시장을 감정적인 동업자로 보고 기회를 활용하세요",
                importance=0.9,
                examples=["공포 매도 시 매수", "탐욕 매수 시 매도"],
                common_mistakes=["시장 감정에 휩쓸림", "단기 변동성에 과민반응"]
            ),
            InvestmentPrinciple(
                name="방어적 투자",
                description="안전하고 수익성 있는 투자를 우선시하세요",
                importance=0.8,
                examples=["배당 지급 기록", "낮은 부채비율", "안정적 수익"],
                common_mistakes=["고위험 투기", "검증되지 않은 회사 투자"]
            )
        ]
        
        self.mentors["graham"] = graham
        
        # Ray Dalio - Risk Parity
        dalio = MentorPersona(
            name="Ray Dalio",
            title="Bridgewater Founder",
            investment_style=InvestmentStyle.RISK_PARITY,
            personality=MentorPersonality.ANALYTICAL,
            philosophy="다양한 관점을 고려하고 리스크를 균형 있게 분산하는 것이 핵심이다.",
            risk_tolerance=0.4,
            time_horizon="long_term",
            preferred_sectors=["diversified", "global_macro"],
            teaching_approach="원칙 기반의 체계적 사고를 가르칩니다",
            encouragement_style="실수로부터 배우는 것을 격려합니다",
            warning_style="확증편향과 단일 관점의 위험을 경고합니다",
            strengths=["risk_management", "diversification", "macro_analysis"],
            focus_areas=["correlation", "economic_cycles", "portfolio_balance"]
        )
        
        dalio.key_principles = [
            InvestmentPrinciple(
                name="All Weather 포트폴리오",
                description="모든 경제 환경에서 작동하는 포트폴리오를 구성하세요",
                importance=0.9,
                examples=["주식 30%, 장기채권 40%, 중기채권 15%, 원자재 7.5%, 금 7.5%"],
                common_mistakes=["단일 자산 집중", "상관관계 무시"]
            ),
            InvestmentPrinciple(
                name="원칙 기반 의사결정",
                description="감정이 아닌 원칙에 따라 투자 결정을 내리세요",
                importance=0.8,
                examples=["명확한 매수/매도 규칙", "리밸런싱 원칙"],
                common_mistakes=["즉흥적 결정", "원칙 위반"]
            )
        ]
        
        self.mentors["dalio"] = dalio
        
        # Cathie Wood - Innovation Focused
        wood = MentorPersona(
            name="Cathie Wood",
            title="ARK Invest CEO",
            investment_style=InvestmentStyle.GROWTH,
            personality=MentorPersonality.AGGRESSIVE,
            philosophy="파괴적 혁신에 투자하라. 미래는 기하급수적 성장을 하는 기술에 달려있다.",
            risk_tolerance=0.8,
            time_horizon="long_term",
            preferred_sectors=["technology", "biotech", "fintech", "space"],
            teaching_approach="혁신과 미래 트렌드에 집중합니다",
            encouragement_style="대담한 비전과 신념을 격려합니다",
            warning_style="기존 패러다임에 갇힌 사고를 경고합니다",
            strengths=["innovation_analysis", "technology_trends", "long_term_vision"],
            focus_areas=["disruptive_innovation", "exponential_growth", "technology_adoption"]
        )
        
        wood.key_principles = [
            InvestmentPrinciple(
                name="파괴적 혁신 투자",
                description="기존 산업을 뒤바꿀 혁신 기술에 투자하세요",
                importance=0.9,
                examples=["전기차", "유전자 치료", "인공지능", "블록체인"],
                common_mistakes=["기존 산업에만 투자", "혁신 속도 과소평가"]
            ),
            InvestmentPrinciple(
                name="기하급수적 성장 추구",
                description="선형이 아닌 기하급수적 성장 가능성을 찾으세요",
                importance=0.8,
                examples=["네트워크 효과", "플랫폼 비즈니스", "확장성 있는 기술"],
                common_mistakes=["선형적 사고", "단기 변동성에 흔들림"]
            )
        ]
        
        self.mentors["wood"] = wood
    
    def get_mentor(self, mentor_id: str) -> Optional[MentorPersona]:
        """Get mentor by ID"""
        return self.mentors.get(mentor_id)
    
    def get_mentors_by_style(self, style: InvestmentStyle) -> List[MentorPersona]:
        """Get mentors by investment style"""
        return [mentor for mentor in self.mentors.values() if mentor.investment_style == style]
    
    def get_mentors_by_personality(self, personality: MentorPersonality) -> List[MentorPersona]:
        """Get mentors by personality type"""
        return [mentor for mentor in self.mentors.values() if mentor.personality == personality]
    
    def recommend_mentor_for_player(
        self, 
        player_level: int, 
        risk_tolerance: float, 
        investment_experience: str,
        preferred_style: Optional[InvestmentStyle] = None
    ) -> MentorPersona:
        """Recommend mentor based on player characteristics"""
        
        # Default to Buffett for beginners
        if player_level < 10:
            return self.mentors["buffett"]
        
        # Match by risk tolerance
        if risk_tolerance < 0.3:
            candidates = [self.mentors["buffett"], self.mentors["graham"]]
        elif risk_tolerance > 0.7:
            candidates = [self.mentors["wood"], self.mentors["lynch"]]
        else:
            candidates = [self.mentors["dalio"], self.mentors["lynch"]]
        
        # Filter by preferred style if specified
        if preferred_style:
            style_candidates = [m for m in candidates if m.investment_style == preferred_style]
            if style_candidates:
                candidates = style_candidates
        
        # Return random from candidates
        return random.choice(candidates)
    
    def get_all_mentors(self) -> List[MentorPersona]:
        """Get all available mentors"""
        return list(self.mentors.values())
    
    def get_mentor_comparison(self, mentor1_id: str, mentor2_id: str) -> Dict[str, Any]:
        """Compare two mentors"""
        mentor1 = self.get_mentor(mentor1_id)
        mentor2 = self.get_mentor(mentor2_id)
        
        if not mentor1 or not mentor2:
            return {}
        
        return {
            'mentor1': {
                'name': mentor1.name,
                'style': mentor1.investment_style.value,
                'personality': mentor1.personality.value,
                'risk_tolerance': mentor1.risk_tolerance,
                'strengths': mentor1.strengths
            },
            'mentor2': {
                'name': mentor2.name,
                'style': mentor2.investment_style.value,
                'personality': mentor2.personality.value,
                'risk_tolerance': mentor2.risk_tolerance,
                'strengths': mentor2.strengths
            },
            'differences': {
                'risk_tolerance_diff': abs(mentor1.risk_tolerance - mentor2.risk_tolerance),
                'style_match': mentor1.investment_style == mentor2.investment_style,
                'personality_match': mentor1.personality == mentor2.personality
            }
        }