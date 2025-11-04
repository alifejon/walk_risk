"""Investigation System - 단서 수집 및 조사 시스템"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, TYPE_CHECKING
import random
import uuid

if TYPE_CHECKING:
    from .puzzle_engine import RiskPuzzle


class ClueType(Enum):
    NEWS = "news"                    # 뉴스 기사
    FINANCIAL = "financial"          # 재무제표
    CHART = "chart"                  # 차트 패턴
    INSIDER = "insider"              # 내부자 거래
    SOCIAL = "social"                # 소셜 미디어
    ANALYST = "analyst"              # 애널리스트 리포트
    COMPETITOR = "competitor"        # 경쟁사 동향
    MACRO = "macro"                  # 거시경제 지표


@dataclass
class Clue:
    """조사를 통해 얻을 수 있는 단서"""

    clue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    clue_type: ClueType = ClueType.NEWS
    title: str = ""
    description: str = ""
    content: str = ""
    source: str = "system"
    reliability: float = 0.5              # 신뢰도 (0.0 ~ 1.0)
    relevance_score: Optional[float] = None
    cost_time: int = 0                    # 조사 시간 (초)
    cost_energy: int = 0                  # 조사 에너지 (1~5)
    cost: Optional[int] = None            # API 응답 호환용 에너지 비용

    # 단서 상태
    is_discovered: bool = False
    discovery_time: Optional[datetime] = None

    # 단서 연결 (다른 단서와의 관계)
    related_clues: List[str] = field(default_factory=list)
    contradicts: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.relevance_score is None:
            self.relevance_score = self.reliability
        if self.cost is None:
            self.cost = self.cost_energy or 0
        if not self.title and self.source:
            self.title = f"{self.source.title()} 단서"
        if not self.description and self.content:
            self.description = self.content[:120]


class InvestigationSystem:
    """플레이어의 조사 활동을 관리하는 시스템"""
    
    def __init__(self, player_level: int = 1):
        self.player_level = player_level
        self.energy = self._calculate_max_energy()
        self.investigation_speed = 1.0 + (player_level * 0.1)  # 레벨당 10% 빨라짐
        
        # 조사 도구 해금 상태
        self.unlocked_tools = self._get_unlocked_tools()
        
        # 조사 기록
        self.investigation_history: List[Dict] = []
        
    def _calculate_max_energy(self) -> int:
        """레벨에 따른 최대 에너지"""
        return 10 + (self.player_level // 5) * 2
    
    def _get_unlocked_tools(self) -> Set[ClueType]:
        """레벨에 따라 해금된 조사 도구"""
        tools = {ClueType.NEWS}  # 기본
        
        if self.player_level >= 3:
            tools.add(ClueType.FINANCIAL)
        if self.player_level >= 5:
            tools.add(ClueType.CHART)
        if self.player_level >= 10:
            tools.add(ClueType.ANALYST)
        if self.player_level >= 15:
            tools.add(ClueType.INSIDER)
        if self.player_level >= 20:
            tools.add(ClueType.COMPETITOR)
        if self.player_level >= 25:
            tools.add(ClueType.MACRO)
        if self.player_level >= 30:
            tools.add(ClueType.SOCIAL)
            
        return tools
    
    def investigate(self, 
                   clue: Clue,
                   use_boost: bool = False) -> Tuple[bool, str, Dict]:
        """단서 조사 시도"""
        
        # 도구 확인
        if clue.clue_type not in self.unlocked_tools:
            return False, f"{clue.clue_type.value} 조사 도구가 잠겨있습니다", {}
        
        # 에너지 확인
        energy_cost = clue.cost_energy
        if use_boost:
            energy_cost *= 2  # 부스트 사용시 2배 에너지
            
        if self.energy < energy_cost:
            return False, f"에너지 부족 (필요: {energy_cost}, 현재: {self.energy})", {}
        
        # 조사 시간 계산
        investigation_time = clue.cost_time / self.investigation_speed
        if use_boost:
            investigation_time /= 2  # 부스트시 시간 절반
        
        # 조사 수행
        self.energy -= energy_cost
        clue.is_discovered = True
        clue.discovery_time = datetime.now()
        
        # 조사 결과 생성
        result = self._generate_investigation_result(clue, use_boost)
        
        # 기록 저장
        self.investigation_history.append({
            'timestamp': datetime.now(),
            'clue_type': clue.clue_type.value,
            'success': True,
            'energy_spent': energy_cost,
            'time_spent': investigation_time,
            'reliability': clue.reliability
        })
        
        return True, "조사 성공", result
    
    def _generate_investigation_result(self, 
                                      clue: Clue,
                                      use_boost: bool) -> Dict:
        """조사 결과 생성"""
        result = {
            'clue_content': clue.content,
            'reliability': clue.reliability,
            'insights': []
        }
        
        # 신뢰도에 따른 통찰력 제공
        if clue.reliability > 0.8:
            result['insights'].append("매우 신뢰할 만한 정보입니다")
        elif clue.reliability > 0.6:
            result['insights'].append("어느 정도 신뢰할 수 있는 정보입니다")
        elif clue.reliability > 0.4:
            result['insights'].append("추가 확인이 필요한 정보입니다")
        else:
            result['insights'].append("신중하게 받아들여야 할 정보입니다")
        
        # 부스트 사용시 추가 정보
        if use_boost:
            result['bonus_insight'] = self._get_bonus_insight(clue)
        
        # 관련 단서 힌트
        if clue.related_clues:
            result['hint'] = f"이 단서는 {len(clue.related_clues)}개의 다른 단서와 연결되어 있습니다"
        
        # 모순 경고
        if clue.contradicts:
            result['warning'] = "다른 단서와 모순되는 정보가 있습니다"
        
        return result
    
    def _get_bonus_insight(self, clue: Clue) -> str:
        """부스트 사용시 추가 통찰력"""
        insights = {
            ClueType.NEWS: "기사 작성 시점과 현재 시장 상황을 비교해보세요",
            ClueType.FINANCIAL: "전년 동기 대비 변화율에 주목하세요",
            ClueType.CHART: "비슷한 패턴이 과거에 어떻게 전개되었는지 확인하세요",
            ClueType.INSIDER: "내부자 거래 시점과 주가 움직임을 대조해보세요",
            ClueType.SOCIAL: "감정적 반응과 실제 펀더멘털을 구분하세요",
            ClueType.ANALYST: "목표가 변경 이력을 추적해보세요",
            ClueType.COMPETITOR: "업종 전체 트렌드와 개별 기업을 구분하세요",
            ClueType.MACRO: "거시 지표가 해당 기업에 미치는 구체적 영향을 파악하세요"
        }
        return insights.get(clue.clue_type, "깊이 있는 분석이 필요합니다")
    
    def connect_clues(self, clue1: Clue, clue2: Clue) -> Optional[str]:
        """두 단서를 연결하여 새로운 통찰 얻기"""
        if not (clue1.is_discovered and clue2.is_discovered):
            return None
        
        # 같은 타입의 단서
        if clue1.clue_type == clue2.clue_type:
            return self._connect_same_type(clue1, clue2)
        
        # 보완적인 단서들
        complementary = {
            (ClueType.NEWS, ClueType.FINANCIAL): "뉴스와 재무 데이터를 대조하니 실제 영향이 보입니다",
            (ClueType.CHART, ClueType.INSIDER): "차트 패턴과 내부자 거래가 일치합니다",
            (ClueType.MACRO, ClueType.COMPETITOR): "거시 환경이 업종 전체에 미치는 영향이 명확해집니다",
            (ClueType.ANALYST, ClueType.SOCIAL): "전문가 의견과 대중 심리의 괴리가 보입니다"
        }
        
        key = (clue1.clue_type, clue2.clue_type)
        if key in complementary:
            return complementary[key]
        
        key_reversed = (clue2.clue_type, clue1.clue_type)
        if key_reversed in complementary:
            return complementary[key_reversed]
        
        # 모순 발견
        if clue1.reliability > 0.7 and clue2.reliability < 0.4:
            return "신뢰도 차이가 큰 정보들입니다. 더 신뢰할 만한 쪽에 무게를 두세요"
        
        return "두 단서 사이의 연관성을 찾기 어렵습니다"
    
    def _connect_same_type(self, clue1: Clue, clue2: Clue) -> str:
        """같은 타입의 단서 연결"""
        connections = {
            ClueType.NEWS: "여러 뉴스를 종합하니 전체 그림이 보입니다",
            ClueType.FINANCIAL: "재무 데이터의 추세가 명확해집니다",
            ClueType.CHART: "패턴의 확인이 강화됩니다",
            ClueType.ANALYST: "여러 애널리스트의 공통 의견을 찾았습니다"
        }
        return connections.get(clue1.clue_type, "같은 종류의 정보가 일관성을 보입니다")
    
    def synthesize_clues(self, discovered_clues: List[Clue]) -> Dict:
        """발견한 모든 단서를 종합하여 큰 그림 제시"""
        if not discovered_clues:
            return {"summary": "아직 충분한 단서가 없습니다", "confidence": 0.0}
        
        # 신뢰도 가중 평균
        total_reliability = sum(c.reliability for c in discovered_clues)
        avg_reliability = total_reliability / len(discovered_clues)
        
        # 단서 타입별 분류
        by_type = {}
        for clue in discovered_clues:
            if clue.clue_type not in by_type:
                by_type[clue.clue_type] = []
            by_type[clue.clue_type].append(clue)
        
        # 종합 분석
        summary_parts = []
        
        if ClueType.NEWS in by_type:
            summary_parts.append("뉴스 동향이 시장 심리를 보여줍니다")
        if ClueType.FINANCIAL in by_type:
            summary_parts.append("재무 데이터가 펀더멘털을 뒷받침합니다")
        if ClueType.CHART in by_type:
            summary_parts.append("기술적 신호가 나타나고 있습니다")
        
        # 모순 확인
        has_contradiction = any(
            c1.contradicts and any(c2 for c2 in discovered_clues if id(c2) in c1.contradicts)
            for c1 in discovered_clues
        )
        
        if has_contradiction:
            summary_parts.append("⚠️ 상충하는 정보가 있어 주의가 필요합니다")
        
        return {
            "summary": ". ".join(summary_parts) if summary_parts else "패턴을 찾는 중입니다",
            "confidence": avg_reliability,
            "clue_count": len(discovered_clues),
            "coverage": len(by_type) / len(ClueType),  # 조사 범위
            "recommendation": self._get_investigation_recommendation(by_type, avg_reliability)
        }
    
    def _get_investigation_recommendation(self, 
                                         by_type: Dict,
                                         avg_reliability: float) -> str:
        """추가 조사 추천"""
        missing_types = set(ClueType) - set(by_type.keys())
        
        if avg_reliability < 0.5:
            return "더 신뢰할 만한 정보원을 찾아보세요"
        elif len(missing_types) > 4:
            return f"아직 조사하지 않은 영역이 많습니다. {list(missing_types)[0].value} 조사를 추천합니다"
        elif ClueType.FINANCIAL not in by_type:
            return "재무 데이터를 확인하여 펀더멘털을 검증하세요"
        elif len(by_type) >= 5:
            return "충분한 조사를 했습니다. 이제 가설을 세워보세요"
        else:
            return "몇 가지 단서를 더 수집하면 확신을 가질 수 있을 것입니다"


class InvestigationEngine:
    """서비스 레이어용 조사 엔진 래퍼"""

    def __init__(self, player_level: int = 1):
        self.player_level = player_level

    async def investigate(
        self,
        puzzle: "RiskPuzzle",
        clue: Clue,
        investigation_type: str = "standard"
    ) -> Dict[str, Any]:
        """퍼즐 단서 조사 수행"""
        system = InvestigationSystem(player_level=self.player_level)
        use_boost = investigation_type.lower() == "boost"
        success, message, result = system.investigate(clue, use_boost=use_boost)

        response: Dict[str, Any] = {
            "success": success,
            "message": message,
            "insights": result.get("insights", []),
        }

        if "bonus_insight" in result:
            response["bonus_insight"] = result["bonus_insight"]
        if "hint" in result:
            response["hint"] = result["hint"]
        if "warning" in result:
            response["warning"] = result["warning"]

        return response
