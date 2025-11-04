# Walk Risk 개발 로드맵 - 다음 단계

## 🎯 즉시 시작할 작업 (다음 세션)

### 1. 기존 시스템 통합 (우선순위: 최고)

#### A. 튜토리얼과 퍼즐 시스템 연결
```python
# 구현할 파일: walk_risk/tutorials/puzzle_tutorial.py
# 목표: 튜토리얼에서 첫 번째 퍼즐 체험

class PuzzleTutorial:
    def __init__(self, tutorial_manager, puzzle_engine):
        # 기존 튜토리얼 매니저와 새 퍼즐 엔진 연결
        
    async def first_puzzle_experience(self, player):
        # 1. 간단한 퍼즐 제시 (초급 난이도)
        # 2. 가이드된 단서 수집 (버핏 멘토가 힌트 제공)
        # 3. 가설 수립 도움
        # 4. 검증 과정 설명
```

#### B. 버핏 멘토 업그레이드
```python
# 수정할 파일: walk_risk/ai/mentor_personas.py
# 목표: 퍼즐 힌트 제공 기능 추가

class BuffettMentor:
    def give_puzzle_hint(self, puzzle, discovered_clues):
        # 현재 진행 상황에 맞는 힌트 제공
        # "아직 재무제표를 확인하지 않았군요..."
        
    def validate_hypothesis(self, hypothesis):
        # 플레이어 가설에 대한 버핏식 조언
        # "그 가설은 흥미롭군요. 하지만 한 가지 놓친 게 있습니다..."
```

#### C. 실시간 데이터 연동
```python
# 수정할 파일: walk_risk/data/market_data/yahoo_finance.py  
# 목표: 실제 시장 이벤트 자동 퍼즐화

class MarketEventDetector:
    def detect_puzzle_worthy_events(self):
        # 급락(-5% 이상), 급등(+5% 이상), 변동성(일평균 3배 이상) 감지
        # 자동으로 퍼즐 생성 트리거
        
    def create_real_time_puzzle(self, market_event):
        # 실제 시장 데이터로 퍼즐 생성
        # 뉴스, 재무 데이터, 업종 동향 등 실제 단서 활용
```

### 2. 퍼즐 콘텐츠 확장 (우선순위: 높음)

#### A. 다양한 시나리오 추가
```python
# 추가할 파일: walk_risk/core/risk_puzzle/scenarios/
├── market_crash_scenarios.py      # 폭락 시나리오
├── bubble_scenarios.py            # 버블 시나리오  
├── earnings_scenarios.py          # 실적 발표 시나리오
├── macro_event_scenarios.py       # 거시경제 이벤트
└── sector_rotation_scenarios.py   # 섹터 로테이션

# 각 시나리오별 특화된 단서와 함정 추가
```

#### B. 업종별 특화 퍼즐
```python
# 구현 예시: 반도체 업종 특화 퍼즐
class SemiconductorPuzzle:
    def __init__(self):
        self.specialized_clues = [
            "메모리 반도체 가격 동향",
            "파운드리 수주 현황", 
            "중국 반도체 정책",
            "AI 수요 증감"
        ]
```

### 3. UI/UX 개선 (우선순위: 중간)

#### A. 단서 수집 시각화
```python
# 구현할 기능
- 단서 수집 진행도 바
- 에너지 게이지 애니메이션  
- 단서 연결 네트워크 다이어그램
- 가설 정확도 실시간 피드백
```

#### B. 직관적인 인터페이스
```python
# 개선할 UI 요소
- 드래그&드롭으로 단서 연결
- 시각적 가설 작성 도구
- 진행 상황 대시보드
- 스킬 성장 시각화
```

## 📅 1주차 개발 계획

### Day 1-2: 기존 시스템 통합
- [ ] `tutorial_manager.py`에 퍼즐 단계 추가
- [ ] 버핏 멘토에 퍼즐 힌트 기능 구현
- [ ] 기본 통합 테스트 완료

### Day 3-4: 실시간 데이터 연동
- [ ] 시장 이벤트 감지 시스템 구현
- [ ] Yahoo Finance 데이터로 실제 퍼즐 생성
- [ ] 실시간 퍼즐 자동 생성 테스트

### Day 5-7: 콘텐츠 확장 및 밸런싱
- [ ] 5가지 기본 시나리오 구현
- [ ] 난이도별 퍼즐 밸런싱
- [ ] 통합 테스트 및 버그 수정

## 🗓️ 1개월 로드맵

### Week 1: 핵심 통합 (위 내용)
### Week 2: 멀티 멘토 시스템
- Peter Lynch (성장주 전문)
- Benjamin Graham (가치투자)  
- Ray Dalio (거시경제)
- Cathie Wood (혁신 기술)

### Week 3: 고급 퍼즐 메커니즘
- 연속 퍼즐 (여러 이벤트 연결)
- 시간 제한 퍼즐
- 선택의 결과가 다음 퍼즐에 영향

### Week 4: 폴리싱 및 최적화
- 성능 최적화
- UI/UX 개선
- 버그 수정 및 안정화

## 🎮 핵심 개발 원칙

### 1. 항상 "왜 재미있는가?" 질문하기
- 모든 기능이 플레이어의 호기심을 자극하는가?
- 성취감을 느낄 수 있는가?
- 더 하고 싶게 만드는가?

### 2. 교육 효과 우선
- 실제 투자에 도움이 되는가?
- 잘못된 투자 습관을 조장하지 않는가?
- 리스크 관리 중요성을 강조하는가?

### 3. 확장성 고려
- 새로운 퍼즐 타입 추가가 쉬운가?
- 다양한 시장(해외, 암호화폐 등) 지원 가능한가?
- 멀티플레이어 확장 가능한가?

## 🚨 주의사항 및 함정

### 1. 과도한 복잡성 경계
- 퍼즐이 너무 복잡해져서 초보자가 포기하지 않도록
- 단계적 학습 곡선 유지
- 실패해도 재미있어야 함

### 2. 실제 투자와의 괴리 방지
- 게임의 단순화가 현실 왜곡으로 이어지지 않도록
- 시뮬레이션의 한계 명확히 표시
- 실제 투자 전 추가 학습 필요성 강조

### 3. 중독성 vs 건전성
- 도박적 요소 완전 배제
- 장기적 사고 방식 강화
- 감정적 의사결정 경계 교육

## 💾 중요한 백업 파일들

### 필수 백업 대상
```
walk_risk/core/risk_puzzle/          # 오늘 구현한 핵심 시스템
docs/development_log_2025_08_03.md  # 오늘의 작업 기록
risk_puzzle_auto_demo.py             # 작동하는 데모
```

### 다음 작업 시 우선 확인
1. 기존 데모들이 여전히 작동하는지 확인
2. 새로운 퍼즐 시스템과 기존 시스템 충돌 여부 확인  
3. 실시간 데이터 연동 시 API 제한 확인

## 📝 다음 세션 시작 가이드

### 1. 환경 확인
```bash
cd /Users/alifejon/Documents/GitHub/walk_risk
uv sync
uv run python risk_puzzle_auto_demo.py  # 작동 확인
```

### 2. 우선순위 작업 시작
```bash
# 1. 튜토리얼 통합부터 시작
cp walk_risk/tutorials/tutorial_manager.py walk_risk/tutorials/tutorial_manager_backup.py
# 안전하게 백업 후 수정 시작
```

### 3. 개발 방향 확인
- 이 문서의 "즉시 시작할 작업" 섹션 참조
- 각 기능이 왜 필요한지 다시 한 번 검토
- 플레이어 관점에서 재미있는지 계속 확인

---

*이 로드맵은 Walk Risk가 진정한 "투자 학습 게임"으로 완성되기 위한 명확한 경로를 제시합니다. 각 단계마다 "왜 재미있는가?"와 "실제로 도움이 되는가?"를 끊임없이 질문하며 개발하세요.*