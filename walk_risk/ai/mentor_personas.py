"""Mentor Personas - 멘토 페르소나"""

from typing import Dict, Any, List, Optional
from enum import Enum
import random


class BuffettPersona:
    """워런 버핏 페르소나"""
    
    def __init__(self):
        self.name = "Warren Buffett"
        self.title = "가치투자의 거장"
        self.philosophy = "가격은 당신이 지불하는 것이고, 가치는 당신이 얻는 것입니다"
        
    def get_greeting(self) -> str:
        return f"🏛️ {self.name}: 함께 가치투자의 세계를 탐험해보겠습니다."
        
    def get_advice(self, context: Dict[str, Any]) -> str:
        """상황별 조언 반환"""
        situation = context.get("situation", "general")
        
        advice_map = {
            "market_fear": "다른 사람들이 두려워할 때 탐욕스럽게 행동하세요.",
            "greed": "탐욕이 당신을 지배할 때, 두려움을 기억하세요.",
            "patience": "복리는 세상의 8번째 불가사의입니다. 인내하세요.",
            "general": "항상 장기적인 관점으로 투자하세요."
        }
        
        return f"🏛️ {self.name}: {advice_map.get(situation, advice_map['general'])}"
    
    def give_puzzle_hint(self, 
                        puzzle_data: Dict[str, Any],
                        discovered_clues: List,
                        investigation_progress: float) -> str:
        """퍼즐 해결을 위한 힌트 제공"""
        
        clue_count = len(discovered_clues)
        
        # 진행 상황에 따른 맞춤형 힌트
        if clue_count == 0:
            return f"""
🏛️ {self.name}: "모든 위대한 투자는 정보 수집부터 시작됩니다.

첫 번째 원칙: '무엇을 모르는지 인정하는 것'입니다.
지금 상황에서 가장 중요한 질문을 해보세요:

❓ 이 회사에 무슨 일이 일어났을까요?
❓ 시장은 어떤 반응을 보이고 있을까요?

뉴스부터 확인해보는 것이 좋겠습니다.
기본적인 정보 없이는 현명한 판단을 내릴 수 없습니다."
            """.strip()
            
        elif clue_count == 1:
            return f"""
🏛️ {self.name}: "좋습니다! 첫 번째 단서를 확보했군요.

하지만 제가 항상 말하듯이: '한 가지 정보로는 충분하지 않습니다.'

📊 재무 상태는 어떤가요? 숫자는 거짓말하지 않습니다.
📈 기술적 신호는 어떻게 나타나고 있을까요?

정보는 마치 퍼즐 조각과 같습니다. 
하나만으로는 전체 그림을 볼 수 없어요."
            """.strip()
            
        elif clue_count == 2:
            return f"""
🏛️ {self.name}: "훌륭합니다! 이제 패턴이 보이기 시작하죠?

두 개의 단서가 어떻게 연결되는지 생각해보세요.
• 서로 일치하나요, 아니면 모순되나요?
• 어떤 이야기를 들려주고 있나요?

제가 50년간 배운 것은: '시장은 단기적으로는 투표기계지만, 
장기적으로는 저울'이라는 것입니다.

지금 보고 있는 것이 단기적 노이즈인지, 
아니면 근본적 변화인지 판단해보세요."
            """.strip()
            
        elif clue_count >= 3:
            return f"""
🏛️ {self.name}: "놀랍습니다! 이제 충분한 정보를 모았네요.

정보 수집 단계는 끝났습니다. 이제 가장 중요한 단계입니다:
'종합적 사고'

🤔 모든 단서를 종합해서 큰 그림을 그려보세요:
• 이 상황의 핵심 원인은 무엇인가요?
• 시장의 반응이 합리적인가요?
• 이것이 기회인가요, 아니면 위험인가요?

기억하세요: '복잡한 상황일수록 단순하게 생각하라'
가장 명백하고 논리적인 설명이 대개 정답입니다."
            """.strip()
        
        return f"🏛️ {self.name}: 계속 조사해보세요. 답은 데이터 안에 있습니다."
    
    def validate_hypothesis_thinking(self,
                                   hypothesis: str,
                                   confidence: float,
                                   evidence_strength: float) -> str:
        """플레이어의 가설에 대한 버핏식 검증"""
        
        if confidence > 0.9 and evidence_strength < 0.6:
            return f"""
🏛️ {self.name}: "잠깐, {hypothesis}라고 하셨죠?

주의하세요! 과신은 투자자의 가장 큰 적입니다.
확신도가 {confidence:.0%}나 되는데 증거는 {evidence_strength:.0%}밖에 안 된다고요?

제 경험상, 이런 상황에서는 한 걸음 물러서서 다시 생각해보는 것이 좋습니다.
'나는 무엇을 놓치고 있을까?'라고 자문해보세요.

겸손함이 교만함보다 더 많은 돈을 벌어줍니다."
            """.strip()
            
        elif confidence < 0.4:
            return f"""
🏛️ {self.name}: "'{hypothesis}'... 흥미로운 관점이네요.

하지만 확신이 {confidence:.0%}밖에 안 된다면, 
아직 더 조사가 필요할 수도 있겠네요.

제가 항상 하는 말이 있습니다:
'의심스러우면 투자하지 마라'

더 확신이 설 때까지 기다리는 것도 하나의 전략입니다.
급할 것 없어요."
            """.strip()
            
        elif 0.6 <= confidence <= 0.8 and evidence_strength >= 0.7:
            return f"""
🏛️ {self.name}: "'{hypothesis}' - 균형 잡힌 접근이군요!

확신도 {confidence:.0%}, 증거 {evidence_strength:.0%}... 
이 정도면 합리적인 수준입니다.

완벽한 확신은 없습니다. 중요한 것은:
1. 충분한 정보에 기반했는가?
2. 리스크를 제대로 고려했는가?
3. 감정이 아닌 논리로 판단했는가?

이 세 가지가 만족된다면, 행동할 때입니다."
            """.strip()
            
        else:
            return f"""
🏛️ {self.name}: "'{hypothesis}'에 대해 어떻게 생각하시나요?

가설을 세우는 것 자체가 투자의 절반입니다.
나머지 절반은 그 가설이 틀릴 가능성을 항상 염두에 두는 것이죠.

제가 성공할 수 있었던 이유는 '틀릴 수 있다'는 생각을 
항상 머릿속에 두고 있었기 때문입니다."
            """.strip()
    
    def puzzle_completion_feedback(self,
                                  accuracy: float,
                                  time_taken: int,
                                  clues_used: int) -> str:
        """퍼즐 완료 후 피드백"""
        
        if accuracy >= 0.8:
            feedback = f"""
🏛️ {self.name}: "훌륭합니다! 정확도 {accuracy:.0%}라니, 정말 인상적이에요.

{time_taken}초 만에 {clues_used}개 단서로 이런 결과를 내다니...
당신에게는 투자자의 재능이 있습니다.

🎯 특히 잘한 점:
• 체계적인 정보 수집
• 논리적 사고 과정  
• 감정보다 이성 우선

계속 이런 식으로 접근한다면, 시장에서 성공할 수 있을 겁니다."
            """.strip()
            
        elif accuracy >= 0.6:
            feedback = f"""
🏛️ {self.name}: "좋은 결과입니다! 정확도 {accuracy:.0%}면 충분히 괜찮아요.

투자에서 100% 정확할 필요는 없습니다.
60-70%만 맞춰도 장기적으로는 큰 성공을 거둘 수 있어요.

💡 개선점:
다음번에는 조금 더 신중하게 단서를 검토해보세요.
급하게 결론을 내리지 말고요."
            """.strip()
            
        else:
            feedback = f"""
🏛️ {self.name}: "이번엔 아쉬웠지만, 실패는 최고의 선생님입니다.

제가 젊었을 때 수많은 실수를 했습니다.
버크셔 해서웨이 초기에도 엉뚱한 투자를 많이 했고요.

🎓 중요한 것은 실패에서 배우는 것입니다:
• 어디서 잘못 판단했을까요?
• 어떤 신호를 놓쳤을까요?  
• 다음번에는 어떻게 할 것인가요?

실패를 두려워하지 마세요. 실패에서 배우지 않는 것을 두려워하세요."
            """.strip()
            
        return feedback


class LynchPersona:
    """피터 린치 페르소나 - One Up On Wall Street 철학"""
    
    def __init__(self):
        self.name = "Peter Lynch"
        self.title = "성장주 투자의 마스터"
        self.philosophy = "당신이 이해할 수 있는 회사에 투자하라"
        
    def get_greeting(self) -> str:
        return f"📈 {self.name}: 일상에서 투자 기회를 찾아보겠습니다!"
        
    def get_advice(self, context: Dict[str, Any]) -> str:
        """상황별 조언 반환"""
        situation = context.get("situation", "general")
        
        advice_map = {
            "market_fear": "공포로 가득한 시장은 좋은 회사를 싸게 살 기회입니다.",
            "greed": "빠른 수익을 쫓지 마세요. 좋은 회사가 시간을 벌어줄 것입니다.",
            "patience": "10배 주식을 찾으려면 10년을 기다릴 각오를 하세요.",
            "general": "당신의 일상에서 투자 아이디어를 찾으세요."
        }
        
        return f"📈 {self.name}: {advice_map.get(situation, advice_map['general'])}"
    
    def give_puzzle_hint(self, 
                        puzzle_data: Dict[str, Any],
                        discovered_clues: List,
                        investigation_progress: float) -> str:
        """퍼즐 해결을 위한 힌트 제공 - Lynch의 소비자 관점"""
        
        clue_count = len(discovered_clues)
        symbol = puzzle_data.get('symbol', '이 회사')
        change_percent = puzzle_data.get('change_percent', 0)
        
        # Lynch는 항상 소비자와 기업 비즈니스 관점으로 접근
        if clue_count == 0:
            return f"""
📈 {self.name}: "훌륭한 투자 기회가 될 수도 있겠네요!
            
제가 펀드를 운용할 때 가장 중요하게 생각했던 질문들입니다:

🏪 소비자 관점:
• 이 회사의 제품이나 서비스를 실제로 사용해봤나요?
• 주변 사람들은 이 회사에 대해 어떻게 말하고 있나요?
• 매장에서 이 회사 제품이 잘 팔리고 있나요?

📊 먼저 뉴스를 확인해서 '무슨 일이 일어났는지' 파악해보세요.
소비자 입장에서 이해할 수 있는 이야기인지 확인하는 것이 중요합니다!"
            """.strip()
            
        elif clue_count == 1:
            return f"""
📈 {self.name}: "좋습니다! 이제 상황을 파악했군요.
            
하지만 저는 항상 '스토리'와 '숫자'를 함께 봅니다.

📖 스토리가 있나요?
• 이 변화가 회사의 장기적 성장에 어떤 영향을 줄까요?
• 경쟁사들은 어떤 상황인가요?
• 이것이 일시적 현상인가요, 아니면 구조적 변화인가요?

💰 재무제표를 확인해보세요:
• 매출이 꾸준히 성장하고 있나요?
• 부채 비율은 건전한가요?
• 현금흐름은 양호한가요?

제가 말레이시아에서 7-Eleven을 보고 투자한 것처럼,
명확한 비즈니스 스토리가 있어야 합니다!"
            """.strip()
            
        elif clue_count == 2:
            return f"""
📈 {self.name}: "훌륭해요! 이제 퍼즐이 맞춰지기 시작하네요.
            
지금까지의 정보를 바탕으로 이 회사를 분류해보세요:

🚀 Fast Growers (급성장주)?
• 매출이 연 20-25% 성장하고 있나요?
• 새로운 시장이나 제품 때문인가요?

🏭 Stalwarts (안정주)?  
• 꾸준하지만 느린 성장 (10-12%)
• 경기 변동에 덜 민감한가요?

📉 Cyclicals (경기순환주)?
• 경기나 업황에 따라 실적이 크게 변하나요?

🔄 Turnarounds (회생주)?
• 어려움을 겪다가 회복 중인가요?

각 유형별로 투자 접근법이 완전히 다릅니다.
차트를 확인해서 기술적 신호도 봐주세요!"
            """.strip()
            
        elif clue_count >= 3:
            # Lynch는 항상 PEG ratio와 성장률을 강조
            return f"""
📈 {self.name}: "완벽합니다! 이제 투자 결정을 내릴 시간이에요.
            
제가 펀드에서 13년간 29배 수익을 낸 비결은 이 체크리스트였습니다:

✅ The Lynch Checklist:
• 이 회사의 비즈니스를 5살 아이에게 설명할 수 있나요?
• 향후 10년간 이 회사가 필요할까요?
• 경쟁 우위(해자)가 있나요?
• 경영진이 주주 친화적인가요?

📊 숫자 체크:
• PEG Ratio = P/E ÷ 성장률 < 1.0 이면 좋습니다
• 부채비율이 너무 높지 않나요?
• 현금 보유량은 충분한가요?

🎯 투자 이유를 한 문장으로 설명할 수 있다면 좋은 투자입니다!
'나는 이 회사에 투자한다 왜냐하면 _______' 를 완성해보세요."
            """.strip()
        
        return f"📈 {self.name}: 소비자 관점에서 한 번 더 생각해보세요!"
    
    def validate_hypothesis_thinking(self,
                                   hypothesis: str,
                                   confidence: float,
                                   evidence_strength: float) -> str:
        """가설 검증 피드백 - Lynch의 실용적 접근"""
        
        # Lynch는 과신보다는 신중함을 강조
        if confidence > 0.9 and evidence_strength < 0.7:
            return f"""
📈 {self.name}: "잠깐, 너무 확신하는 것 같은데요?
            
제가 펀드를 운용하면서 배운 교훈:
'확신할수록 더 신중해져야 한다'

📊 증거: {evidence_strength:.0%} vs 확신: {confidence:.0%}
이 차이가 위험 신호입니다.

🤔 다시 한번 점검해보세요:
• 혹시 놓친 중요한 정보가 있을까요?
• 내가 보고 싶은 것만 보고 있는 건 아닐까요?
• 반대 의견은 어떤 것들이 있을까요?

월가에서 20년간 일하면서 깨달은 것:
'겸손한 투자자가 오래 살아남습니다.'"
            """.strip()
            
        elif confidence < 0.4:
            return f"""
📈 {self.name}: "너무 확신이 없어 보이는데요?
            
좋은 투자 기회를 놓치고 있는 건 아닐까요?

투자에서 100% 확실한 것은 없습니다.
하지만 합리적 확신은 필요해요.

💡 이렇게 생각해보세요:
• 내가 이 회사의 주식을 5년간 보유할 수 있을까?
• 주변 지인들에게 추천할 수 있을까?
• 가격이 30% 떨어져도 더 살 수 있을까?

만약 이 질문들에 '그렇다'고 답할 수 있다면,
더 자신감을 가져도 됩니다!"
            """.strip()
            
        else:
            return f"""
📈 {self.name}: "좋은 균형감각이네요! 
            
확신도 {confidence:.0%}, 증거 강도 {evidence_strength:.0%} - 
이 정도면 합리적인 투자 판단입니다.

제가 Magellan 펀드를 운용할 때도 이런 확신 수준에서
가장 좋은 성과를 냈습니다.

🎯 기억하세요:
투자는 과학이 아니라 예술입니다.
완벽한 정보는 없어도, 합리적 판단은 가능합니다.

'{hypothesis}'
이 가설이 맞을 확률이 60% 이상이라면 충분합니다!"
            """.strip()
    
    def puzzle_completion_feedback(self,
                                  accuracy: float,
                                  time_taken: int,
                                  clues_used: int) -> str:
        """퍼즐 완료 후 피드백 - Lynch의 격려 스타일"""
        
        if accuracy >= 0.8:
            encouragements = [
                "훌륭합니다! 당신에게는 10-Bagger를 찾는 안목이 있어요!",
                "이런 분석력이라면 월가에서도 통할 것 같은데요?",
                "정말 인상적입니다! Magellan 펀드에 와도 될 것 같아요!"
            ]
            
            feedback = f"""
📈 {self.name}: "{random.choice(encouragements)}
            
정확도 {accuracy:.0%}, {time_taken}초, {clues_used}개 단서 활용 - 완벽한 성과입니다!

🏆 특히 인상적인 점:
• 소비자 관점에서의 접근
• 체계적인 정보 수집
• 균형 잡힌 판단력

이런 식으로 계속 접근한다면:
📈 10년 후에는 10배 수익도 가능할 겁니다!
            
다음 번에는 더 복잡한 성장주도 도전해보세요!"
            """.strip()
            
        elif accuracy >= 0.6:
            feedback = f"""
📈 {self.name}: "좋은 성과입니다! 정확도 {accuracy:.0%}면 충분해요.
            
제가 펀드를 운용할 때도 모든 투자가 성공하지는 않았습니다.
중요한 것은 승률이 아니라 '큰 승부에서 이기는 것'이에요.

💡 다음번 개선 포인트:
• 좀 더 인내심을 가지고 조사해보세요
• 반대 의견도 한 번씩 고려해보세요
• 시간 압박에 휘둘리지 마세요

60-70% 정확도로도 충분히 성공적인 투자자가 될 수 있습니다!"
            """.strip()
            
        else:
            feedback = f"""
📈 {self.name}: "이번엔 아쉬웠지만, 실패는 성공의 어머니입니다!
            
제가 월가에서 배운 가장 중요한 교훈:
'실패하지 않는 투자자는 없다. 실패에서 배우지 않는 투자자만 있을 뿐이다.'

🎓 저도 수많은 실수를 했어요:
• 좋은 회사를 너무 일찍 판 적도 있고
• 나쁜 회사를 너무 오래 보유한 적도 있습니다

🔄 다음번에는:
• 더 많은 단서를 수집해보세요
• 소비자 관점을 놓치지 마세요  
• 성급한 결론을 피하세요

실패는 더 좋은 투자자가 되는 과정입니다!"
            """.strip()
            
        return feedback


class GrahamPersona:
    """벤자민 그레이엄 페르소나 - Intelligent Investor 철학"""
    
    def __init__(self):
        self.name = "Benjamin Graham"
        self.title = "가치투자의 아버지"
        self.philosophy = "주식은 기업의 일부분이며, 시장은 단기적으로는 투표기계, 장기적으로는 저울이다"
        
    def get_greeting(self) -> str:
        return f"🎓 {self.name}: 숫자와 논리로 투자의 진실을 찾아보겠습니다."
        
    def get_advice(self, context: Dict[str, Any]) -> str:
        """상황별 조언 반환"""
        situation = context.get("situation", "general")
        
        advice_map = {
            "market_fear": "시장의 공포는 현명한 투자자에게 기회를 선사합니다.",
            "greed": "투기와 투자를 구분하세요. 안전마진을 항상 확보하십시오.",
            "patience": "시장은 장기적으로 가치를 인정합니다. 인내하세요.",
            "general": "항상 객관적 분석과 안전마진을 기반으로 투자하세요."
        }
        
        return f"🎓 {self.name}: {advice_map.get(situation, advice_map['general'])}"
    
    def give_puzzle_hint(self, 
                        puzzle_data: Dict[str, Any],
                        discovered_clues: List,
                        investigation_progress: float) -> str:
        """퍼즐 해결을 위한 힌트 제공 - Graham의 정량적 접근"""
        
        clue_count = len(discovered_clues)
        symbol = puzzle_data.get('symbol', '이 회사')
        change_percent = puzzle_data.get('change_percent', 0)
        
        # Graham은 항상 숫자와 객관적 데이터를 강조
        if clue_count == 0:
            return f"""
🎓 {self.name}: "투자 분석은 과학적이어야 합니다.
            
감정이나 추측이 아닌, 객관적 사실에 기반해야 합니다.

📊 첫 번째 원칙: '사실 수집'
• 무슨 일이 일어났는지 정확히 파악하세요
• 뉴스나 공시를 통해 객관적 정보를 얻으세요
• 추측은 금물, 오직 확인된 사실만

📈 변동률 {change_percent:+.1f}%는 상당한 움직임입니다.
이런 변화에는 반드시 구체적인 원인이 있습니다.

먼저 뉴스를 확인해서 팩트를 파악하세요.
모든 분석은 확실한 정보에서 시작됩니다."
            """.strip()
            
        elif clue_count == 1:
            return f"""
🎓 {self.name}: "좋습니다. 이제 정량적 분석을 시작해야 합니다.
            
제가 '증권분석'에서 강조한 핵심 원칙:
'감정이 아닌 숫자로 말하게 하라'

📊 재무제표 분석이 필수입니다:
• P/E Ratio (주가수익비율)
• P/B Ratio (주가순자산비율) 
• ROE (자기자본이익률)
• 부채비율과 유동비율
• 배당수익률

📈 또한 기술적 지표도 참고하세요:
• 거래량 패턴
• 지지선과 저항선
• 과매수/과매도 신호

숫자는 거짓말하지 않습니다.
재무 데이터를 확인해보세요."
            """.strip()
            
        elif clue_count == 2:
            return f"""
🎓 {self.name}: "훌륭합니다. 이제 종합적 분석 단계입니다.
            
지금까지 수집한 정보를 바탕으로 '내재가치' 분석을 해보세요:

📊 Graham의 내재가치 체크리스트:
• 현재 주가가 장부가치 대비 합리적인가?
• 수익성이 일관되고 안정적인가?
• 부채 수준이 건전한가?
• 경영진이 주주 친화적인가?

🔍 특히 중요한 것은 '안전마진'입니다:
• 내재가치 > 현재 주가 × 1.3 이상이어야 안전합니다
• 위험 대비 수익이 충분한가요?

⚖️ 정량적 분석을 통해:
이 변화가 '일시적 가격 왜곡'인지 
'근본적 가치 변화'인지 판단해보세요.

차트 분석도 추가로 확인해주세요."
            """.strip()
            
        elif clue_count >= 3:
            return f"""
🎓 {self.name}: "완벽합니다. 이제 최종 투자 결정 단계입니다.
            
모든 정보를 종합하여 다음 3가지를 판단하세요:

1️⃣ 내재가치 vs 시장가격
• 현재 주가가 내재가치 대비 할인되어 있나요?
• 안전마진 30% 이상 확보되나요?

2️⃣ 투자 vs 투기 판단
• 객관적 데이터에 기반한 투자인가요?
• 아니면 감정에 휩쓸린 투기인가요?

3️⃣ 리스크-리워드 분석
• 최악의 경우 손실 폭은?
• 예상 수익률이 위험을 감수할 만한가?

📚 제가 '현명한 투자자'에서 강조한 원칙:
'투자의 첫 번째 규칙은 돈을 잃지 않는 것이고,
두 번째 규칙은 첫 번째 규칙을 절대 잊지 않는 것이다.'

모든 분석이 완료되었다면, 이제 논리적 결론을 내리세요."
            """.strip()
        
        return f"🎓 {self.name}: 더 많은 정량적 데이터가 필요합니다."
    
    def validate_hypothesis_thinking(self,
                                   hypothesis: str,
                                   confidence: float,
                                   evidence_strength: float) -> str:
        """가설 검증 피드백 - Graham의 보수적 접근"""
        
        # Graham은 안전마진과 보수적 접근을 강조
        if confidence > 0.8 and evidence_strength < 0.7:
            return f"""
🎓 {self.name}: "주의하세요. 과신은 투자자의 적입니다.
            
확신도 {confidence:.0%} vs 증거 강도 {evidence_strength:.0%}
이런 불균형은 위험한 신호입니다.

제가 평생 강조해온 원칙:
'확실하지 않으면 투자하지 마라'

🛡️ 안전마진 원칙:
• 모든 분석에는 오차가 있습니다
• 예상보다 30% 이상 안전해야 합니다
• 틀릴 가능성을 항상 고려하세요

🔍 재점검하세요:
• 놓친 중요한 데이터가 있을까요?
• 너무 낙관적으로 해석한 건 아닐까요?
• 반대 증거는 충분히 고려했나요?

신중함이 성공적 투자의 기초입니다."
            """.strip()
            
        elif confidence < 0.5:
            return f"""
🎓 {self.name}: "너무 소극적인 것도 기회를 놓칠 수 있습니다.
            
확신도 {confidence:.0%}는 지나치게 낮습니다.
충분한 분석을 했다면 합리적 확신을 가져야 합니다.

💡 객관적으로 평가해보세요:
• 수집한 데이터가 일관된 방향을 가리키나요?
• 정량적 지표들이 명확한 신호를 주나요?
• 안전마진이 충분히 확보되나요?

📊 제가 권하는 확신 수준:
• 60-70%: 합리적 투자 판단
• 70-80%: 좋은 투자 기회
• 80% 이상: 뛰어난 기회 (단, 과신 주의)

데이터가 명확하다면 더 자신감을 가지세요.
하지만 절대 100% 확신하지는 마세요."
            """.strip()
            
        else:
            return f"""
🎓 {self.name}: "훌륭한 균형감입니다!
            
확신도 {confidence:.0%}, 증거 강도 {evidence_strength:.0%}
이는 현명한 투자자의 접근법입니다.

✅ 이런 수준에서 최고의 투자 결정이 나옵니다:
• 충분한 데이터 기반 분석
• 적절한 안전마진 확보
• 과신하지 않는 신중함

'{hypothesis}'
이 가설이 객관적 분석에 기반한다면 좋은 투자 판단입니다.

🎯 기억하세요:
투자는 확률 게임입니다. 
70% 확률로 옳은 결정을 계속 내리면, 
장기적으로는 반드시 성공합니다."
            """.strip()
    
    def puzzle_completion_feedback(self,
                                  accuracy: float,
                                  time_taken: int,
                                  clues_used: int) -> str:
        """퍼즐 완료 후 피드백 - Graham의 학술적 스타일"""
        
        if accuracy >= 0.8:
            feedback = f"""
🎓 {self.name}: "뛰어난 분석력입니다! 정확도 {accuracy:.0%}는 탁월한 성과예요.
            
{time_taken}초 동안 {clues_used}개 단서를 체계적으로 분석한 과정이 인상적입니다.

📊 특히 우수한 점들:
• 객관적 데이터 중심의 접근
• 감정보다 논리를 우선시
• 체계적인 정보 수집 과정
• 안전마진을 고려한 신중함

🏆 이런 분석 역량이라면:
• 안전한 가치투자가 가능합니다
• 장기적 수익 창출이 기대됩니다
• 시장 변동성에 흔들리지 않을 것입니다

제가 컬럼비아 대학에서 가르쳤던 학생들 중에서도
이 정도 수준은 찾기 어려웠습니다!"
            """.strip()
            
        elif accuracy >= 0.6:
            feedback = f"""
🎓 {self.name}: "양호한 성과입니다. 정확도 {accuracy:.0%}는 만족스러운 수준이에요.
            
투자에서 완벽함을 추구할 필요는 없습니다.
일관되게 합리적인 결정을 내리는 것이 더 중요해요.

📈 개선 포인트:
• 더 많은 정량적 데이터 활용
• 반대 의견에 대한 고려
• 안전마진 확보 체크

60-70% 정확도로도 충분히 성공적인 투자가 가능합니다.
꾸준함이 완벽함보다 중요합니다."
            """.strip()
            
        else:
            feedback = f"""
🎓 {self.name}: "실패는 학습의 기회입니다.
            
제가 '증권분석'을 쓸 때도 수많은 시행착오가 있었습니다.
중요한 것은 실패에서 배우는 체계적 접근법입니다.

🔍 분석해보세요:
• 어떤 데이터를 놓쳤을까요?
• 감정적 판단이 개입했을까요?
• 안전마진을 충분히 고려했을까요?

📚 다음번 개선 방법:
• 더 체계적인 정보 수집
• 정량적 지표 우선 활용
• 객관적 사실과 주관적 해석 구분

실패는 더 나은 투자자가 되는 과정입니다.
포기하지 마세요."
            """.strip()
            
        return feedback


class DalioPersona:
    """레이 달리오 페르소나 - Principles 철학"""
    
    def __init__(self):
        self.name = "Ray Dalio"
        self.title = "거시경제 분석의 대가"
        self.philosophy = "원칙을 갖고, 경제 사이클을 이해하며, 다각화하라"
        
    def get_greeting(self) -> str:
        return f"🌍 {self.name}: 거시경제적 관점에서 위험을 분석해보겠습니다."
        
    def get_advice(self, context: Dict[str, Any]) -> str:
        situation = context.get("situation", "general")
        advice_map = {
            "market_fear": "경제 사이클을 이해하면 공포는 기회가 됩니다.",
            "greed": "과도한 레버리지는 위험합니다. 항상 다각화하세요.",
            "patience": "큰 변화는 시간이 필요합니다. 경제 사이클을 기다리세요.",
            "general": "원칙에 따라 행동하고, 거시경제를 주시하세요."
        }
        return f"🌍 {self.name}: {advice_map.get(situation, advice_map['general'])}"
    
    def give_puzzle_hint(self, puzzle_data: Dict[str, Any], discovered_clues: List, investigation_progress: float) -> str:
        clue_count = len(discovered_clues)
        
        if clue_count == 0:
            return f"""
🌍 {self.name}: "모든 투자는 거시경제적 맥락에서 이해해야 합니다.

🌐 Bridgewater 원칙:
• 경제 사이클 상 어느 지점인가요?
• 중앙은행 정책은 어떻게 변화하고 있나요?
• 글로벌 경제 상황은 어떤가요?

먼저 뉴스를 확인해서 경제 전반의 상황을 파악하세요."
            """.strip()
            
        elif clue_count == 1:
            return f"""
🌍 {self.name}: "이제 거시경제적 분석을 추가해야 합니다.

📊 All Weather 전략의 관점:
• 금리 환경이 이 회사에 미치는 영향
• 인플레이션과의 상관관계
• 환율 변동의 영향

재무 데이터로 기업의 체질을 확인하세요."
            """.strip()
            
        elif clue_count >= 2:
            return f"""
🌍 {self.name}: "이제 시스템적 사고로 연결해보세요.

🔄 Principles 접근법:
• 이 상황이 과거 패턴과 유사한가요?
• 시장 전체에 미칠 파급효과는?
• 포트폴리오 다각화 관점에서 어떤가요?

모든 조사를 완료하고 시스템적으로 분석하세요."
            """.strip()
        
        return f"🌍 {self.name}: 더 넓은 관점에서 바라보세요."
    
    def validate_hypothesis_thinking(self, hypothesis: str, confidence: float, evidence_strength: float) -> str:
        if confidence > 0.9:
            return f"🌍 {self.name}: 과신은 위험합니다. 항상 예상치 못한 변수를 고려하세요."
        elif confidence < 0.4:
            return f"🌍 {self.name}: 데이터가 명확하다면 더 확신을 가져도 됩니다. 원칙에 따라 행동하세요."
        else:
            return f"🌍 {self.name}: 좋은 균형입니다. 리스크 관리를 잊지 마세요."
    
    def puzzle_completion_feedback(self, accuracy: float, time_taken: int, clues_used: int) -> str:
        if accuracy >= 0.8:
            return f"🌍 {self.name}: 탁월한 시스템적 사고입니다. 이런 접근법으로 포트폴리오를 구성하면 All Weather 전략이 가능할 것입니다."
        elif accuracy >= 0.6:
            return f"🌍 {self.name}: 좋은 성과입니다. 다각화와 리스크 관리를 더 고려해보세요."
        else:
            return f"🌍 {self.name}: 실패에서 배우는 것이 원칙입니다. 더 체계적인 접근을 시도해보세요."


class WoodPersona:
    """캐시 우드 페르소나 - 혁신 투자 철학"""
    
    def __init__(self):
        self.name = "Cathie Wood"
        self.title = "혁신 기술 투자의 선구자"
        self.philosophy = "파괴적 혁신에 투자하고, 미래를 앞서가라"
        
    def get_greeting(self) -> str:
        return f"🚀 {self.name}: 혁신 기술의 관점에서 기회를 찾아보겠습니다!"
        
    def get_advice(self, context: Dict[str, Any]) -> str:
        situation = context.get("situation", "general")
        advice_map = {
            "market_fear": "혁신 기업들은 변동성이 높지만 장기적 성장 잠재력이 큽니다.",
            "greed": "기술 발전 속도를 과소평가하지 마세요. 하지만 밸류에이션도 중요해요.",
            "patience": "파괴적 혁신은 시간이 필요합니다. 5-10년의 긴 안목이 필요해요.",
            "general": "전통적 분석을 넘어서 혁신의 잠재력을 보세요."
        }
        return f"🚀 {self.name}: {advice_map.get(situation, advice_map['general'])}"
    
    def give_puzzle_hint(self, puzzle_data: Dict[str, Any], discovered_clues: List, investigation_progress: float) -> str:
        clue_count = len(discovered_clues)
        
        if clue_count == 0:
            return f"""
🚀 {self.name}: "흥미로운 기회일 수 있겠네요!

🔬 ARK Invest 관점:
• 이 회사가 어떤 혁신 기술과 관련이 있나요?
• AI, 로보틱스, 바이오테크, 블록체인 중 어디에 해당하나요?
• 파괴적 혁신의 잠재력이 있나요?

뉴스부터 확인해서 기술적 맥락을 파악하세요."
            """.strip()
            
        elif clue_count == 1:
            return f"""
🚀 {self.name}: "이제 혁신 기업의 특성을 분석해야 합니다.

💡 Innovation Assessment:
• 이 기술이 기존 산업을 파괴할 잠재력이 있나요?
• 시장 크기(TAM)는 얼마나 클까요?
• 경쟁 우위는 지속 가능한가요?

재무 데이터도 확인하되, 전통적 지표만으로는 부족할 수 있어요."
            """.strip()
            
        elif clue_count >= 2:
            return f"""
🚀 {self.name}: "이제 미래 전망을 그려보세요!

🔮 Future Vision:
• 5-10년 후 이 기술/회사는 어떻게 될까요?
• 지수적 성장 가능성이 있나요?
• 변동성을 감수할 만한 잠재력인가요?

모든 정보를 종합해서 혁신의 관점에서 판단하세요."
            """.strip()
        
        return f"🚀 {self.name}: 미래 지향적으로 생각해보세요!"
    
    def validate_hypothesis_thinking(self, hypothesis: str, confidence: float, evidence_strength: float) -> str:
        if confidence > 0.8:
            return f"🚀 {self.name}: 혁신 투자에는 확신이 필요하지만, 변동성도 각오하세요."
        elif confidence < 0.5:
            return f"🚀 {self.name}: 파괴적 혁신을 믿는다면 더 용기를 가지세요. 하지만 리스크는 분산하세요."
        else:
            return f"🚀 {self.name}: 좋은 접근입니다. 혁신에는 인내와 용기가 모두 필요해요."
    
    def puzzle_completion_feedback(self, accuracy: float, time_taken: int, clues_used: int) -> str:
        if accuracy >= 0.8:
            return f"🚀 {self.name}: 놀라운 혁신적 사고입니다! 이런 분석력이라면 차세대 Tesla나 Netflix를 찾을 수 있을 거예요!"
        elif accuracy >= 0.6:
            return f"🚀 {self.name}: 좋은 성과입니다. 혁신 기업 분석은 어려워요. 더 많은 경험을 쌓아보세요."
        else:
            return f"🚀 {self.name}: 혁신 투자는 쉽지 않아요. 실패도 학습의 과정입니다. 포기하지 마세요!"


# 멘토 팩토리 클래스
class MentorFactory:
    """멘토 생성 및 관리 클래스"""
    
    @staticmethod
    def get_all_mentors():
        """모든 멘토 인스턴스 반환"""
        return {
            "buffett": BuffettPersona(),
            "lynch": LynchPersona(),
            "graham": GrahamPersona(),
            "dalio": DalioPersona(),
            "wood": WoodPersona()
        }
    
    @staticmethod
    def get_mentor(mentor_name: str):
        """특정 멘토 인스턴스 반환"""
        mentors = MentorFactory.get_all_mentors()
        return mentors.get(mentor_name.lower())
    
    @staticmethod
    def get_mentor_names():
        """사용 가능한 멘토 이름 리스트 반환"""
        return list(MentorFactory.get_all_mentors().keys())
    
    @staticmethod
    def get_random_mentor():
        """랜덤 멘토 반환"""
        mentors = list(MentorFactory.get_all_mentors().values())
        return random.choice(mentors)
    
    @staticmethod
    def create_mentor_debate(puzzle_data: Dict[str, Any], mentor1_name: str, mentor2_name: str):
        """멘토 간 토론 생성"""
        mentor1 = MentorFactory.get_mentor(mentor1_name)
        mentor2 = MentorFactory.get_mentor(mentor2_name)
        
        if not mentor1 or not mentor2:
            return None
            
        return MentorDebate(mentor1, mentor2, puzzle_data)


class MentorDebate:
    """멘토 간 토론 시스템"""
    
    def __init__(self, mentor1, mentor2, puzzle_data: Dict[str, Any]):
        self.mentor1 = mentor1
        self.mentor2 = mentor2
        self.puzzle_data = puzzle_data
        self.debate_rounds = []
        
    def generate_debate_scenario(self) -> str:
        """토론 시나리오 생성"""
        scenarios = {
            ("buffett", "lynch"): {
                "topic": "장기 가치 vs 성장 잠재력",
                "context": "같은 기업을 두고 서로 다른 투자 접근법을 제시합니다"
            },
            ("buffett", "wood"): {
                "topic": "안정성 vs 혁신 투자",
                "context": "전통적 가치투자와 혁신 기술 투자의 대립"
            },
            ("graham", "dalio"): {
                "topic": "개별 기업 분석 vs 거시경제 관점",
                "context": "미시적 분석과 거시적 분석의 충돌"
            },
            ("lynch", "wood"): {
                "topic": "검증된 성장 vs 파괴적 혁신",
                "context": "기존 성장주와 혁신 기술주의 선택"
            }
        }
        
        key1 = (self.mentor1.name.lower().split()[1], self.mentor2.name.lower().split()[1])
        key2 = (self.mentor2.name.lower().split()[1], self.mentor1.name.lower().split()[1])
        
        scenario = scenarios.get(key1) or scenarios.get(key2)
        if scenario:
            return f"🥊 {scenario['topic']}\n💭 {scenario['context']}"
        else:
            return "🥊 투자 철학 대결\n💭 서로 다른 관점에서 같은 상황을 분석합니다"
    
    def get_opening_statements(self) -> tuple:
        """각 멘토의 개막 발언"""
        symbol = self.puzzle_data.get('symbol', '이 회사')
        change_percent = self.puzzle_data.get('change_percent', 0)
        
        # 멘토별 특화된 개막 발언 생성
        statement1 = self._generate_opening_statement(self.mentor1, change_percent)
        statement2 = self._generate_opening_statement(self.mentor2, change_percent)
        
        return statement1, statement2
    
    def _generate_opening_statement(self, mentor, change_percent: float) -> str:
        """개별 멘토의 개막 발언 생성"""
        if "Buffett" in mentor.name:
            if change_percent < -5:
                return f"""
🏛️ {mentor.name}: "이런 급락은 오히려 기회일 수 있습니다.
가격이 떨어졌다고 해서 가치까지 사라진 건 아니거든요.
중요한 것은 이 회사의 본질적 가치를 파악하는 것입니다.
단기적 변동에 휘둘리지 말고, 10년 후를 내다보세요."
                """.strip()
            else:
                return f"🏛️ {mentor.name}: 장기적 관점에서 이 회사의 경쟁 우위와 경영진의 능력을 봐야 합니다."
                
        elif "Lynch" in mentor.name:
            if change_percent < -5:
                return f"""
📈 {mentor.name}: "급락했다고? 이건 정말 흥미로운데요!
소비자로서 이 회사 제품을 생각해보세요. 
스마트폰, 반도체, 가전제품... 여전히 우리 생활에 필수적이잖아요?
주가가 떨어진 이유를 파악하되, 비즈니스 펀더멘털은 별개로 봐야 합니다.
때로는 시장이 과도하게 반응하거든요."
                """.strip()
            else:
                return f"📈 {mentor.name}: 소비자 관점에서 이 회사의 실제 비즈니스를 평가해봅시다."
                
        elif "Graham" in mentor.name:
            return f"""
🎓 {mentor.name}: "감정을 배제하고 객관적 데이터만 봅시다.
{change_percent:+.1f}% 변동의 근본 원인을 숫자로 분석해야 합니다.
P/E, P/B, ROE, 부채비율... 이런 지표들이 진실을 말해줄 것입니다.
안전마진이 확보된다면 좋은 기회가 될 수 있어요."
            """.strip()
            
        elif "Dalio" in mentor.name:
            return f"""
🌍 {mentor.name}: "개별 기업만 보면 안 됩니다.
경제 사이클 전체를 봐야 해요. 중앙은행 정책, 글로벌 공급망, 
지정학적 리스크... 이 모든 것이 연결되어 있습니다.
이 회사가 현재 경제 환경에서 어떤 위치에 있는지 파악해야 합니다."
            """.strip()
            
        elif "Wood" in mentor.name:
            return f"""
🚀 {mentor.name}: "전통적 분석으로는 한계가 있어요!
이 회사가 AI, 5G, IoT 같은 혁신 기술과 어떻게 연결되는지 봐야 합니다.
변동성은 혁신의 대가예요. 5-10년 후 이 기술이 세상을 어떻게 바꿀지
상상해보세요. 그게 진짜 투자 기회입니다."
            """.strip()
            
        return f"{mentor.name}: 제 관점에서 이 상황을 분석해보겠습니다."
    
    def generate_rebuttal(self, mentor, opponent_statement: str) -> str:
        """상대방 발언에 대한 반박"""
        if "Buffett" in mentor.name:
            if "혁신" in opponent_statement or "기술" in opponent_statement:
                return f"""
🏛️ {mentor.name}: "혁신이 중요하다는 건 동의합니다. 하지만 혁신이 반드시 수익으로 이어지는 건 아니에요.
닷컴 버블 때를 기억하세요. 모두가 '혁신'을 외쳤지만 결국 대부분이 사라졌습니다.
진정한 투자는 이해할 수 있는 비즈니스, 지속 가능한 경쟁 우위, 합리적 가격에 기반해야 합니다."
                """.strip()
            elif "소비자" in opponent_statement:
                return f"🏛️ {mentor.name}: 소비자 관점도 중요하지만, 수익성과 자본 효율성을 놓치면 안 됩니다."
            else:
                return f"🏛️ {mentor.name}: 하지만 근본적 가치 없는 투자는 도박과 다를 바 없습니다."
                
        elif "Lynch" in mentor.name:
            if "장기" in opponent_statement or "10년" in opponent_statement:
                return f"""
📈 {mentor.name}: "10년도 좋지만, 그 사이에 얼마나 많은 기회를 놓칠까요?
제가 Magellan 펀드에서 29배 수익을 낸 건 너무 완벽한 기업만 기다리지 않았기 때문입니다.
소비자로서 직접 체험할 수 있는 좋은 회사, 이해하기 쉬운 비즈니스 모델이면 충분해요."
                """.strip()
            elif "데이터" in opponent_statement or "객관적" in opponent_statement:
                return f"📈 {mentor.name}: 숫자도 중요하지만, 숫자 뒤에 숨은 스토리를 놓치면 안 됩니다."
            else:
                return f"📈 {mentor.name}: 너무 복잡하게 생각하지 마세요. 좋은 회사는 보통 명확합니다."
                
        elif "Graham" in mentor.name:
            if "소비자" in opponent_statement or "스토리" in opponent_statement:
                return f"""
🎓 {mentor.name}: "스토리는 매력적이지만 위험할 수 있습니다.
감정에 휩쓸려 객관적 판단을 잃기 쉽거든요. 
수치화할 수 없는 건 투자 근거가 될 수 없습니다. 
P/E가 30배인 주식을 '스토리'만으로 살 수는 없어요."
                """.strip()
            elif "혁신" in opponent_statement:
                return f"🎓 {mentor.name}: 혁신의 가치를 어떻게 정량화할 건가요? 추측에 의존한 투자는 투기입니다."
            else:
                return f"🎓 {mentor.name}: 감정을 배제하고 팩트에 집중해야 합니다."
                
        return f"{mentor.name}: 제 관점에서는 다르게 봅니다."
    
    def conduct_debate_round(self, round_num: int) -> Dict[str, str]:
        """토론 라운드 진행"""
        if round_num == 1:
            # 1라운드: 개막 발언
            statement1, statement2 = self.get_opening_statements()
            
        elif round_num == 2:
            # 2라운드: 상호 반박
            prev_round = self.debate_rounds[-1]
            statement1 = self.generate_rebuttal(self.mentor1, prev_round['mentor2_statement'])
            statement2 = self.generate_rebuttal(self.mentor2, prev_round['mentor1_statement'])
            
        else:
            # 3라운드 이후: 추가 논점
            statement1 = self._generate_additional_point(self.mentor1, round_num)
            statement2 = self._generate_additional_point(self.mentor2, round_num)
        
        round_result = {
            'round': round_num,
            'mentor1_statement': statement1,
            'mentor2_statement': statement2
        }
        
        self.debate_rounds.append(round_result)
        return round_result
    
    def _generate_additional_point(self, mentor, round_num: int) -> str:
        """추가 논점 생성"""
        points = {
            "Buffett": [
                "리스크 관리 측면에서 봤을 때...",
                "역사적 사례를 보면...",
                "경영진의 신뢰성을 고려해야..."
            ],
            "Lynch": [
                "실제 매장에서 확인해보면...",
                "경쟁사 대비 이 회사는...",
                "성장 동력을 살펴보면..."
            ],
            "Graham": [
                "재무제표 분석 결과...",
                "내재가치 계산을 해보면...",
                "안전마진을 고려할 때..."
            ],
            "Dalio": [
                "거시경제 지표를 보면...",
                "포트폴리오 다각화 차원에서...",
                "경제 사이클상 현재 위치는..."
            ],
            "Wood": [
                "기술 발전 트렌드를 보면...",
                "파괴적 혁신의 관점에서...",
                "미래 시장 전망을 고려하면..."
            ]
        }
        
        mentor_key = mentor.name.split()[1]  # Buffett, Lynch, etc.
        mentor_points = points.get(mentor_key, ["추가적으로 고려할 점은..."])
        
        if round_num - 3 < len(mentor_points):
            return f"{mentor.name}: {mentor_points[round_num - 3]}"
        else:
            return f"{mentor.name}: 마지막으로 강조하고 싶은 것은..."


class StepByStepAnalysis:
    """단계별 심화 분석 시스템"""
    
    def __init__(self, mentor, puzzle_data: Dict[str, Any]):
        self.mentor = mentor
        self.puzzle_data = puzzle_data
        self.analysis_steps = []
        
    def get_step_guidance(self, step: int, discovered_clues: List) -> str:
        """단계별 가이드 제공"""
        if step == 1:
            return self._step1_initial_assessment(discovered_clues)
        elif step == 2:
            return self._step2_data_analysis(discovered_clues)
        elif step == 3:
            return self._step3_comparative_analysis(discovered_clues)
        elif step == 4:
            return self._step4_risk_assessment(discovered_clues)
        elif step == 5:
            return self._step5_final_conclusion(discovered_clues)
        else:
            return self._step_beyond(step, discovered_clues)
    
    def _step1_initial_assessment(self, discovered_clues: List) -> str:
        """1단계: 초기 상황 평가"""
        if "Buffett" in self.mentor.name:
            return f"""
🏛️ {self.mentor.name} - 1단계 분석:

📋 **상황 파악 체크리스트**
• 회사의 기본 비즈니스 모델을 이해하고 있나요?
• 경쟁 우위(Economic Moat)가 명확한가요?
• 경영진을 신뢰할 수 있나요?

🎯 **이 단계의 목표**
변동성에 휘둘리지 말고, 회사의 본질을 파악하는 것입니다.
지금 수집한 정보만으로도 이 회사가 '좋은 회사'인지 판단해보세요.

💡 **버핏의 조언**
"좋은 회사를 적정 가격에 사는 것이 적정한 회사를 싼 가격에 사는 것보다 낫습니다."
            """.strip()
            
        elif "Lynch" in self.mentor.name:
            return f"""
📈 {self.mentor.name} - 1단계 분석:

🏪 **소비자 체크리스트**
• 이 회사 제품을 직접 사용해본 적이 있나요?
• 주변 사람들의 반응은 어떤가요?
• 매장이나 온라인에서 인기가 있나요?

📊 **회사 카테고리 분류**
□ Fast Growers (급성장주)
□ Stalwarts (안정주)
□ Cyclicals (경기순환주)
□ Turnarounds (회생주)

💡 **린치의 조언**
"투자하기 전에 회사를 5살 아이에게 설명할 수 있어야 합니다."
            """.strip()
            
        elif "Graham" in self.mentor.name:
            return f"""
🎓 {self.mentor.name} - 1단계 분석:

📊 **객관적 사실 정리**
• 주가 변동률: {self.puzzle_data.get('change_percent', 0):+.1f}%
• 거래량 비율: {self.puzzle_data.get('volume_ratio', 0):.1f}배
• 시장 심리: {self.puzzle_data.get('market_sentiment', 'unknown')}

🔍 **필수 확인 사항**
• 구체적 변동 원인이 무엇인가요?
• 이것이 일시적인지 구조적인지 구분할 수 있나요?
• 객관적 증거가 충분한가요?

💡 **그레이엄의 조언**
"투자의 첫 번째 원칙은 원금을 잃지 않는 것입니다."
            """.strip()
            
        elif "Dalio" in self.mentor.name:
            return f"""
🌍 {self.mentor.name} - 1단계 분석:

🌐 **거시경제 체크리스트**
• 현재 경제 사이클 위치는?
• 중앙은행 정책 방향은?
• 글로벌 공급망 상황은?

📈 **시스템적 연결고리**
• 이 변화가 다른 자산에 미치는 영향
• 업종 전체 vs 개별 기업 요인 구분
• 지정학적 리스크 고려

💡 **달리오의 조언**
"개별 나무만 보지 말고 숲 전체를 보세요."
            """.strip()
            
        elif "Wood" in self.mentor.name:
            return f"""
🚀 {self.mentor.name} - 1단계 분석:

🔬 **혁신 기술 체크리스트**
• AI/머신러닝과의 연관성은?
• 5G/IoT 생태계에서의 위치는?
• 자율주행/로보틱스 연결점은?

📊 **파괴적 혁신 지표**
• 기존 산업을 바꿀 잠재력
• 시장 크기(TAM) 확장 가능성
• 기술적 진입장벽

💡 **우드의 조언**
"전통적 밸류에이션으로는 혁신의 가치를 측정할 수 없습니다."
            """.strip()
        
        return f"{self.mentor.name}: 1단계 분석을 시작하겠습니다."
    
    def _step2_data_analysis(self, discovered_clues: List) -> str:
        """2단계: 데이터 분석"""
        if "Buffett" in self.mentor.name:
            return f"""
🏛️ {self.mentor.name} - 2단계 심화분석:

💰 **재무 건전성 평가**
• ROE (자기자본수익률) - 15% 이상이면 우수
• 부채비율 - 업종 평균 대비 적정한가?
• 영업현금흐름 - 일관되게 양수인가?

⚖️ **가치 vs 가격 비교**
• 내재가치 대비 현재 주가는?
• 과거 PER 밴드 대비 현재 위치는?
• 배당수익률이 매력적인가?

🔍 **집중 조사 포인트**
수집한 {len(discovered_clues)}개 단서를 바탕으로
이 회사가 '훌륭한 기업'의 기준에 부합하는지 판단하세요.
            """.strip()
            
        elif "Lynch" in self.mentor.name:
            return f"""
📈 {self.mentor.name} - 2단계 심화분석:

📊 **성장률 분석**
• 매출 성장률 - 최근 3년 추이는?
• 이익 성장률 - 지속 가능한가?
• PEG Ratio - 1.0 이하면 매력적

🏢 **비즈니스 스토리 검증**
• 경쟁사 대비 우위점은 명확한가?
• 시장 점유율 변화 추이는?
• 신제품/서비스 파이프라인은?

🎯 **린치 스타일 판단**
지금까지 {len(discovered_clues)}개 단서로
이 회사가 '10-Bagger' 잠재력이 있는지 평가해보세요.
            """.strip()
            
        elif "Graham" in self.mentor.name:
            return f"""
🎓 {self.mentor.name} - 2단계 심화분석:

📋 **정량적 지표 분석**
• P/E Ratio - 업종 평균 대비
• P/B Ratio - 1.5배 이하 선호
• 유동비율 - 최소 2:1 이상

🛡️ **안전마진 계산**
• 청산가치 대비 현재 시가총액
• 최악 시나리오 손실 가능성
• 하방 리스크 vs 상승 잠재력

📊 **객관적 결론 도출**
{len(discovered_clues)}개 데이터 포인트를 종합하여
수치적으로 투자 가치를 평가하세요.
            """.strip()
            
        elif "Dalio" in self.mentor.name:
            return f"""
🌍 {self.mentor.name} - 2단계 심화분석:

📈 **거시경제 연관성**
• 금리 변화가 이 기업에 미치는 영향
• 환율 변동 노출도는?
• 인플레이션 수혜/피해 정도는?

⚖️ **포트폴리오 관점**
• 기존 보유 자산과의 상관관계
• 다각화 효과는 있는가?
• 리스크 조정 수익률은?

🔄 **All Weather 관점**
{len(discovered_clues)}개 정보를 바탕으로
다양한 경제 환경에서 이 투자가 어떻게 작동할지 예측하세요.
            """.strip()
            
        elif "Wood" in self.mentor.name:
            return f"""
🚀 {self.mentor.name} - 2단계 심화분석:

🔬 **기술 트렌드 분석**
• 기술 발전 S-Curve 상의 위치
• 특허 포트폴리오 강도
• R&D 투자 비중 및 효율성

💡 **혁신 생태계 포지션**
• 플랫폼 기업인가, 부품 공급사인가?
• 네트워크 효과가 있는가?
• 디지털 전환 수혜 정도는?

🚀 **미래 가치 평가**
{len(discovered_clues)}개 단서로
5-10년 후 이 기술/기업의 potential을 계산해보세요.
            """.strip()
        
        return f"{self.mentor.name}: 2단계 데이터 분석을 진행하겠습니다."
    
    def _step3_comparative_analysis(self, discovered_clues: List) -> str:
        """3단계: 비교 분석"""
        return f"""
{self.mentor.name} - 3단계 비교분석:

🔍 지금까지 수집한 {len(discovered_clues)}개 단서를 바탕으로
경쟁사 및 대안 투자와 비교분석을 실시합니다.
        """.strip()
        
    def _step4_risk_assessment(self, discovered_clues: List) -> str:
        """4단계: 리스크 평가"""
        return f"""
{self.mentor.name} - 4단계 리스크 평가:

⚠️ 종합적인 리스크 요인을 분석하고
최악의 시나리오까지 고려한 투자 전략을 수립합니다.
        """.strip()
        
    def _step5_final_conclusion(self, discovered_clues: List) -> str:
        """5단계: 최종 결론"""
        return f"""
{self.mentor.name} - 5단계 최종 결론:

🎯 모든 분석을 종합하여 최종 투자 의사결정을 내립니다.
구체적인 매수/매도/보유 결정과 그 이유를 제시합니다.
        """.strip()
        
    def _step_beyond(self, step: int, discovered_clues: List) -> str:
        """5단계 이후 추가 분석"""
        return f"""
{self.mentor.name} - {step}단계 고급분석:

🔬 더욱 세밀한 분석과 시나리오 플래닝을 진행합니다.
        """.strip()