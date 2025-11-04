"""Risk Puzzle Engine - 리스크를 퍼즐로 변환하는 엔진"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from datetime import datetime


class PuzzleDifficulty(Enum):
    BEGINNER = "beginner"      # 명확한 단서 3개
    INTERMEDIATE = "intermediate"  # 애매한 단서 5개
    ADVANCED = "advanced"      # 모순된 단서 7개
    MASTER = "master"         # 숨겨진 진실 찾기


class PuzzleType(Enum):
    PRICE_DROP = "price_drop"        # "왜 떨어졌을까?"
    PRICE_SURGE = "price_surge"      # "왜 올랐을까?"
    VOLATILITY = "volatility"        # "왜 변동성이 클까?"
    DIVERGENCE = "divergence"        # "왜 섹터와 다르게 움직일까?"
    MYSTERY = "mystery"              # "뭔가 이상한데?"


@dataclass
class RiskPuzzle:
    """플레이어가 풀어야 할 리스크 퍼즐"""
    
    puzzle_id: str
    title: str                      # "삼성전자 -10% 미스터리"
    description: str                 # 상황 설명
    puzzle_type: PuzzleType
    difficulty: PuzzleDifficulty
    
    # 퍼즐 데이터
    target_symbol: str               # 대상 주식
    event_data: Dict                 # 이벤트 정보
    
    # 숨겨진 진실 (플레이어가 찾아야 할 것)
    hidden_truth: str                # "반도체 수요 회복 신호"
    correct_hypothesis: str          # "일시적 과매도"
    
    # 단서들
    available_clues: List['Clue'] = field(default_factory=list)
    discovered_clues: List['Clue'] = field(default_factory=list)
    
    # 보상
    base_reward_xp: int = 100
    time_bonus_multiplier: float = 2.0  # 빨리 풀수록 보너스
    
    # 상태
    is_solved: bool = False
    solve_time: Optional[float] = None
    player_hypothesis: Optional[str] = None
    
    def calculate_reward(self, time_taken: float, accuracy: float) -> Tuple[int, str]:
        """퍼즐 해결 보상 계산"""
        # 기본 보상
        xp = self.base_reward_xp
        
        # 정확도 보너스 (0~100%)
        xp *= (1 + accuracy)
        
        # 시간 보너스 (빠를수록 높음)
        if time_taken < 60:  # 1분 이내
            xp *= self.time_bonus_multiplier
            
        # 난이도 보너스
        difficulty_multipliers = {
            PuzzleDifficulty.BEGINNER: 1.0,
            PuzzleDifficulty.INTERMEDIATE: 1.5,
            PuzzleDifficulty.ADVANCED: 2.0,
            PuzzleDifficulty.MASTER: 3.0
        }
        xp *= difficulty_multipliers[self.difficulty]
        
        # 획득 스킬 결정
        skill_gained = self._determine_skill_reward(accuracy)
        
        return int(xp), skill_gained
    
    def _determine_skill_reward(self, accuracy: float) -> str:
        """정확도에 따른 스킬 보상"""
        if accuracy >= 0.9:
            return f"마스터: {self.puzzle_type.value} 분석"
        elif accuracy >= 0.7:
            return f"숙련: {self.puzzle_type.value} 해석"
        elif accuracy >= 0.5:
            return f"초급: {self.puzzle_type.value} 이해"
        else:
            return f"경험: {self.puzzle_type.value} 실패에서 배움"


class PuzzleEngine:
    """리스크 퍼즐 생성 및 관리 엔진"""
    
    def __init__(self):
        self.active_puzzles: Dict[str, RiskPuzzle] = {}
        self.puzzle_templates = self._load_puzzle_templates()
        
    def _load_puzzle_templates(self) -> Dict:
        """퍼즐 템플릿 로드"""
        return {
            PuzzleType.PRICE_DROP: [
                {
                    "title_format": "{symbol} {change}% 급락의 비밀",
                    "hidden_truths": [
                        "실적 발표 전 불안감",
                        "업종 전체 조정",
                        "대주주 매도 루머",
                        "규제 리스크 부상",
                        "기술적 과매도"
                    ],
                    "correct_hypotheses": [
                        "일시적 과매도 - 매수 기회",
                        "구조적 문제 - 추가 하락 예상",
                        "섹터 로테이션 - 관망 필요"
                    ]
                }
            ],
            PuzzleType.PRICE_SURGE: [
                {
                    "title_format": "{symbol} {change}% 급등의 이유",
                    "hidden_truths": [
                        "M&A 루머",
                        "신제품 출시 임박",
                        "실적 서프라이즈 예상",
                        "기관 매집",
                        "공매도 숏커버링"
                    ],
                    "correct_hypotheses": [
                        "지속 상승 가능 - 추가 매수",
                        "과열 국면 - 차익 실현",
                        "변동성 장세 - 분할 매수"
                    ]
                }
            ]
        }
    
    def create_puzzle(self, 
                     symbol: str,
                     market_event: Dict,
                     difficulty: PuzzleDifficulty) -> RiskPuzzle:
        """시장 이벤트로부터 퍼즐 생성"""
        
        # 이벤트 타입 결정
        puzzle_type = self._determine_puzzle_type(market_event)
        
        # 템플릿 선택
        templates = self.puzzle_templates.get(puzzle_type, [])
        if not templates:
            templates = self.puzzle_templates[PuzzleType.MYSTERY]
        template = random.choice(templates)
        
        # 진실과 가설 선택
        hidden_truth = random.choice(template["hidden_truths"])
        correct_hypothesis = random.choice(template["correct_hypotheses"])
        
        # 퍼즐 생성
        puzzle = RiskPuzzle(
            puzzle_id=f"puzzle_{symbol}_{datetime.now().timestamp()}",
            title=template["title_format"].format(
                symbol=symbol,
                change=market_event.get('change_percent', 0)
            ),
            description=self._generate_description(symbol, market_event),
            puzzle_type=puzzle_type,
            difficulty=difficulty,
            target_symbol=symbol,
            event_data=market_event,
            hidden_truth=hidden_truth,
            correct_hypothesis=correct_hypothesis,
            available_clues=self._generate_clues(
                symbol, hidden_truth, difficulty
            )
        )
        
        self.active_puzzles[puzzle.puzzle_id] = puzzle
        return puzzle
    
    def _determine_puzzle_type(self, market_event: Dict) -> PuzzleType:
        """마켓 이벤트로부터 퍼즐 타입 결정"""
        change = market_event.get('change_percent', 0)
        volatility = market_event.get('volatility', 0)
        
        if change < -5:
            return PuzzleType.PRICE_DROP
        elif change > 5:
            return PuzzleType.PRICE_SURGE
        elif volatility > 30:
            return PuzzleType.VOLATILITY
        elif market_event.get('sector_divergence', False):
            return PuzzleType.DIVERGENCE
        else:
            return PuzzleType.MYSTERY
    
    def _generate_description(self, symbol: str, event: Dict) -> str:
        """퍼즐 설명 생성"""
        return f"""
📊 상황: {symbol}이(가) {event.get('change_percent', 0):+.1f}% 변동했습니다.
📈 거래량: 평소 대비 {event.get('volume_ratio', 1.0):.1f}배
🌍 시장: {event.get('market_sentiment', '중립')}
⏰ 시간: {event.get('time', '장중')}

무엇이 이 움직임을 만들었을까요?
단서를 수집하고 가설을 세워보세요.
        """.strip()
    
    def _generate_clues(self, 
                       symbol: str,
                       hidden_truth: str,
                       difficulty: PuzzleDifficulty) -> List:
        """난이도에 따른 단서 생성"""
        from .investigation import Clue, ClueType
        
        clue_counts = {
            PuzzleDifficulty.BEGINNER: 3,
            PuzzleDifficulty.INTERMEDIATE: 5,
            PuzzleDifficulty.ADVANCED: 7,
            PuzzleDifficulty.MASTER: 10
        }
        
        num_clues = clue_counts[difficulty]
        clues = []
        
        # 진실 단서 (1~2개)
        clues.append(Clue(
            clue_type=ClueType.NEWS,
            content=self._create_truth_clue(hidden_truth),
            reliability=0.9 if difficulty == PuzzleDifficulty.BEGINNER else 0.7,
            cost_time=10,
            cost_energy=1
        ))
        
        # 노이즈 단서들
        for _ in range(num_clues - 1):
            clues.append(self._create_noise_clue(difficulty))
        
        random.shuffle(clues)
        return clues
    
    def _create_truth_clue(self, hidden_truth: str) -> str:
        """진실을 암시하는 단서 생성"""
        hints = {
            "실적 발표 전 불안감": "다음 주 실적 발표 예정, 시장 예상치 하회 우려",
            "업종 전체 조정": "동종 업계 주식들도 동반 하락 중",
            "대주주 매도 루머": "최대주주 지분 변동 공시는 없으나 시장에 루머 확산",
            "기술적 과매도": "RSI 30 이하, 볼린저 밴드 하단 이탈"
        }
        return hints.get(hidden_truth, "특별한 뉴스는 없음")
    
    def _create_noise_clue(self, difficulty: PuzzleDifficulty) -> 'Clue':
        """노이즈 단서 생성"""
        from .investigation import Clue, ClueType
        
        noise_contents = [
            "애널리스트 목표가 하향 조정",
            "외국인 순매도 지속",
            "기관 순매수 전환",
            "공매도 잔고 증가",
            "프로그램 매도 호가 대기"
        ]
        
        return Clue(
            clue_type=random.choice(list(ClueType)),
            content=random.choice(noise_contents),
            reliability=random.uniform(0.3, 0.6),
            cost_time=random.randint(5, 15),
            cost_energy=random.randint(1, 3)
        )
    
    def submit_hypothesis(self, 
                         puzzle_id: str,
                         hypothesis: str,
                         evidence: List[str]) -> Tuple[float, str]:
        """플레이어의 가설 제출 및 평가"""
        puzzle = self.active_puzzles.get(puzzle_id)
        if not puzzle:
            return 0.0, "퍼즐을 찾을 수 없습니다"
        
        # 정확도 계산
        accuracy = self._calculate_accuracy(
            hypothesis,
            puzzle.correct_hypothesis,
            evidence,
            puzzle.discovered_clues
        )
        
        # 피드백 생성
        feedback = self._generate_feedback(
            accuracy,
            puzzle.hidden_truth,
            hypothesis
        )
        
        # 퍼즐 완료 처리
        puzzle.is_solved = True
        puzzle.player_hypothesis = hypothesis
        
        return accuracy, feedback
    
    def _calculate_accuracy(self,
                           player_hypothesis: str,
                           correct_hypothesis: str,
                           evidence: List[str],
                           discovered_clues: List) -> float:
        """가설의 정확도 계산"""
        score = 0.0
        
        # 가설 유사도 (간단한 키워드 매칭)
        hypothesis_keywords = set(player_hypothesis.lower().split())
        correct_keywords = set(correct_hypothesis.lower().split())
        
        if hypothesis_keywords & correct_keywords:
            score += 0.5
        
        # 증거 품질
        if len(evidence) > 0:
            score += min(0.3, len(evidence) * 0.1)
        
        # 발견한 단서의 품질
        truth_clues = [c for c in discovered_clues if c.reliability > 0.7]
        if truth_clues:
            score += 0.2
        
        return min(1.0, score)
    
    def _generate_feedback(self, 
                          accuracy: float,
                          hidden_truth: str,
                          hypothesis: str) -> str:
        """플레이어에게 줄 피드백 생성"""
        if accuracy >= 0.8:
            return f"""
🎯 훌륭합니다! 정확한 분석이었습니다.
진실: {hidden_truth}
당신의 통찰력이 시장을 이겼습니다.
            """.strip()
        elif accuracy >= 0.5:
            return f"""
👍 괜찮은 분석이었습니다.
진실: {hidden_truth}
방향은 맞았지만 더 깊은 조사가 필요했습니다.
            """.strip()
        else:
            return f"""
💡 이번엔 빗나갔지만 좋은 경험이었습니다.
진실: {hidden_truth}
실패도 소중한 학습입니다. 다음엔 더 많은 단서를 수집해보세요.
            """.strip()