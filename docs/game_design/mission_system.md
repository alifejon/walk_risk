# 🎯 Walk Risk: 미션 시스템 설계

## 🏗️ 미션 구조 (Mission Structure)

### 기본 미션 스키마
```yaml
Mission:
  metadata:
    id: string                    # 고유 식별자
    title: string                 # 미션 제목
    description: string           # 미션 설명
    historical_context: string    # 역사적 배경
    difficulty: enum              # Easy/Normal/Hard/Expert
    estimated_duration: minutes   # 예상 소요시간
    required_level: integer       # 최소 필요 레벨
    category: enum               # Crisis/Growth/Volatility/Bubble
    
  game_settings:
    initial_funds: integer        # 시작 자금
    time_limit: minutes          # 제한 시간 (실제 시간)
    game_speed: float            # 게임 속도 (1.0 = 실시간)
    market_volatility: float     # 시장 변동성 (0.0-2.0)
    news_frequency: integer      # 뉴스 발생 빈도
    
  objectives:
    primary: Objective           # 주요 목표 (필수)
    secondary: [Objective]       # 부차적 목표들 (선택)
    hidden: [Objective]          # 숨겨진 목표들
    
  constraints:
    portfolio: [Constraint]      # 포트폴리오 제약
    trading: [Constraint]        # 거래 제약  
    risk: [Constraint]          # 리스크 제약
    
  rewards:
    completion: Reward           # 완료 보상
    performance: [Reward]        # 성과 보상
    achievements: [Achievement]  # 업적 보상
```

### 목표 시스템 (Objective System)
```yaml
Objective:
  id: string
  type: enum  # [return, drawdown, diversification, timing, sector_weight]
  description: string
  target_value: number
  comparison: enum  # [greater_than, less_than, equals, between]
  weight: float  # 전체 점수에서 차지하는 비중 (0.0-1.0)
  is_mandatory: boolean  # 필수 달성 여부
  measurement_type: enum  # [final, maximum, minimum, average, cumulative]
  time_window: string  # "entire_mission" | "monthly" | "weekly"
  
  # 목표 유형별 세부 설정
  return_objective:
    base_benchmark: string  # "cash" | "kospi" | "kosdaq" | "custom"
    risk_adjusted: boolean  # 리스크 조정 수익률 여부
    
  risk_objective:
    risk_metric: enum  # [max_drawdown, volatility, beta, var]
    lookback_period: days
    
  diversification_objective:
    metric: enum  # [sector_count, position_count, hhi_index]
    min_weight_per_position: float
    max_weight_per_position: float
```

### 제약 조건 시스템 (Constraint System)
```yaml
Constraint:
  id: string
  type: enum  # [portfolio, trading, position, sector, timing]
  description: string
  severity: enum  # [warning, penalty, violation]  # 위반 시 처리 방식
  
  portfolio_constraint:
    max_positions: integer           # 최대 보유 종목 수
    min_cash_ratio: float           # 최소 현금 비중
    max_cash_ratio: float           # 최대 현금 비중
    max_single_position: float      # 단일 종목 최대 비중
    max_sector_weight: float        # 단일 섹터 최대 비중
    
  trading_constraint:
    max_trades_per_day: integer     # 일일 최대 거래 횟수
    min_holding_period: days        # 최소 보유 기간
    max_order_size: float           # 최대 주문 크기
    allowed_order_types: [string]   # 허용된 주문 유형
    trading_hours_only: boolean     # 거래시간 제한
    
  risk_constraint:
    max_leverage: float             # 최대 레버리지
    max_beta: float                 # 최대 베타
    stop_loss_required: boolean     # 손절매 설정 필수
    max_correlation: float          # 종목 간 최대 상관관계
```

### 평가 시스템 (Scoring System)
```yaml
ScoringSystem:
  total_score_range: [0, 1000]     # 총점 범위
  
  score_components:
    objective_completion: 60%       # 목표 달성도
    risk_management: 25%           # 리스크 관리
    trading_efficiency: 10%        # 거래 효율성
    bonus_achievements: 5%         # 보너스 업적
    
  grade_thresholds:
    S: 900-1000  # 전설적 (Legendary)
    A: 800-899   # 뛰어난 (Excellent) 
    B: 700-799   # 좋은 (Good)
    C: 600-699   # 보통 (Average)
    D: 500-599   # 미흡 (Below Average)
    F: 0-499     # 실패 (Failed)
    
  scoring_formulas:
    return_score: |
      if actual_return >= target_return:
        score = min(100, (actual_return / target_return) * 100)
      else:
        score = max(0, 50 + (actual_return / target_return) * 50)
        
    risk_score: |
      max_drawdown_penalty = max(0, (actual_drawdown - target_drawdown) * 10)
      volatility_penalty = max(0, (actual_volatility - target_volatility) * 5)
      score = max(0, 100 - max_drawdown_penalty - volatility_penalty)
      
    efficiency_score: |
      turnover_penalty = max(0, (turnover_ratio - 2.0) * 10)  # 연 2회 초과 시 감점
      commission_penalty = commission_ratio * 100  # 수수료 비율만큼 감점
      score = max(0, 100 - turnover_penalty - commission_penalty)
```

## 🎮 미션 템플릿들

### 1. 위기 생존형 미션 (Crisis Survival)
```yaml
crisis_survival_template:
  category: "Crisis"
  characteristics:
    - 시장 급락 상황
    - 높은 변동성
    - 단기간 극심한 스트레스
    - 손실 최소화가 목표
    
  common_objectives:
    primary:
      type: "drawdown"
      target_value: -30.0  # 최대 30% 손실 이하
      comparison: "greater_than"
      
    secondary:
      - type: "diversification"
        target_value: 5  # 최소 5개 섹터 분산
      - type: "sector_weight"  
        target_value: 30.0  # 금융주 30% 이하
        
  common_constraints:
    - type: "portfolio"
      max_single_position: 20.0  # 단일 종목 20% 이하
    - type: "portfolio"
      min_cash_ratio: 15.0  # 현금 15% 이상
```

### 2. 성장 포착형 미션 (Growth Capture)
```yaml
growth_capture_template:
  category: "Growth"
  characteristics:
    - 시장 상승 국면
    - 기회 포착이 핵심
    - 공격적 투자 허용
    - 수익률 극대화 목표
    
  common_objectives:
    primary:
      type: "return"
      target_value: 25.0  # 25% 이상 수익
      comparison: "greater_than"
      
    secondary:
      - type: "timing"
        description: "상승장 초기 진입"
      - type: "sector_rotation"
        description: "섹터 로테이션 활용"
        
  common_constraints:
    - type: "risk"
      max_beta: 1.5  # 베타 1.5 이하
    - type: "portfolio"
      max_cash_ratio: 10.0  # 현금 10% 이하
```

### 3. 변동성 대응형 미션 (Volatility Management)  
```yaml
volatility_management_template:
  category: "Volatility"
  characteristics:
    - 높은 시장 변동성
    - 빈번한 방향 전환
    - 타이밍의 중요성
    - 균형잡힌 접근 필요
    
  common_objectives:
    primary:
      type: "risk_adjusted_return"
      target_value: 1.5  # 샤프 비율 1.5 이상
      comparison: "greater_than"
      
    secondary:
      - type: "volatility"
        target_value: 15.0  # 변동성 15% 이하
      - type: "turnover"
        target_value: 2.0  # 연 2회 이하 회전율
```

### 4. 버블 대응형 미션 (Bubble Navigation)
```yaml
bubble_navigation_template:
  category: "Bubble"
  characteristics:
    - 비이성적 시장 과열
    - 밸류에이션 왜곡
    - 타이밍 게임
    - 출구 전략 중요
    
  common_objectives:
    primary:
      type: "market_timing"
      description: "버블 정점 이전 80% 이상 현금화"
      
    secondary:
      - type: "return"
        target_value: 50.0  # 상승기 수익 포착
      - type: "preservation"
        target_value: -10.0  # 하락기 손실 제한
```

## 🎯 구체적 미션 예시: "2008 서브프라임 위기"

```yaml
mission_2008_subprime:
  metadata:
    id: "crisis_2008_subprime"
    title: "2008년 서브프라임 위기 생존하기"
    description: |
      2007년 8월부터 시작된 서브프라임 모기지 위기가 2008년 전면적인 
      금융위기로 확산되고 있습니다. 리먼 브라더스 파산부터 AIG 구제금융까지, 
      역사상 최악의 금융위기 상황에서 포트폴리오를 보호하세요.
    historical_context: |
      • 2007.8: 서브프라임 모기지 위기 시작
      • 2008.3: 베어스턴스 구제금융  
      • 2008.9: 리먼 브라더스 파산
      • 2008.10: KOSPI 1,000선 붕괴
      • 2009.3: 시장 바닥 (KOSPI 1,124)
    difficulty: "Hard"
    estimated_duration: 45  # 45분
    required_level: 10
    category: "Crisis"
    
  game_settings:
    initial_funds: 100_000_000  # 1억원
    time_limit: 45  # 45분 실제 시간
    game_speed: 2.0  # 2배속 (18개월을 45분에)
    market_volatility: 2.5  # 극도로 높은 변동성
    news_frequency: 180  # 3분마다 뉴스
    
  objectives:
    primary:
      id: "survive_crisis"
      type: "drawdown"
      description: "최대 손실 40% 이하로 유지"
      target_value: -40.0
      comparison: "greater_than" 
      weight: 0.6
      is_mandatory: true
      measurement_type: "maximum"
      
    secondary:
      - id: "diversify_sectors"
        type: "diversification"
        description: "5개 이상 서로 다른 섹터에 투자"
        target_value: 5
        comparison: "greater_than"
        weight: 0.15
        
      - id: "limit_financials"
        type: "sector_weight"
        description: "금융주 비중 15% 이하 유지"
        target_value: 15.0
        comparison: "less_than"
        weight: 0.15
        
      - id: "maintain_liquidity"  
        type: "cash_ratio"
        description: "현금 비중 20% 이상 유지"
        target_value: 20.0
        comparison: "greater_than"
        weight: 0.1
        
    hidden:
      - id: "buffett_opportunity"
        type: "timing"
        description: "시장 바닥에서 우량주 매수"
        trigger_condition: "kospi < 1200 AND buy_blue_chips"
        bonus_points: 100
        
  constraints:
    portfolio:
      - id: "position_limit"
        type: "portfolio"
        max_single_position: 25.0
        severity: "penalty"
        description: "단일 종목 25% 이하"
        
      - id: "leverage_limit"
        type: "risk"
        max_leverage: 1.0
        severity: "violation"
        description: "레버리지 금지"
        
    trading:
      - id: "day_trading_limit"
        type: "trading"  
        max_trades_per_day: 10
        severity: "warning"
        description: "일일 거래 10회 제한"
        
  rewards:
    completion:
      base_exp: 1000
      grade_multiplier:
        S: 2.0
        A: 1.5  
        B: 1.2
        C: 1.0
        D: 0.8
        F: 0.5
        
    performance:
      - condition: "grade >= A"
        reward_type: "unlock"
        item: "mentor_ray_dalio"
        
      - condition: "hidden_objective_completed"
        reward_type: "achievement"
        item: "crisis_opportunist"
        
      - condition: "perfect_score"
        reward_type: "title"
        item: "Crisis Master"
        
    achievements:
      - id: "diamond_hands"
        description: "위기 상황에서 우량주 계속 보유"
        condition: "hold_blue_chip_during_crash"
        points: 50
        
      - id: "market_timer"
        description: "시장 바닥 근처에서 매수"  
        condition: "buy_at_market_bottom"
        points: 100
        
      - id: "risk_manager"
        description: "손실을 20% 이하로 제한"
        condition: "max_drawdown <= 20.0"
        points: 150
```

## 🎮 미션 진행 시스템

### 미션 상태 관리
```yaml
MissionState:
  status: enum  # [not_started, in_progress, paused, completed, failed]
  start_time: datetime
  current_time: datetime  # 게임 내 시간
  real_elapsed_time: seconds
  
  progress:
    objectives_completed: [string]  # 완료된 목표 ID들
    constraints_violated: [string]  # 위반된 제약 ID들
    current_score: number
    current_grade: string
    
  events:
    triggered_events: [GameEvent]  # 발생한 이벤트들
    pending_events: [GameEvent]    # 예정된 이벤트들
    news_history: [NewsItem]       # 뉴스 히스토리
```

### 동적 이벤트 시스템
```yaml
GameEvent:
  id: string
  trigger_time: datetime  # 게임 내 시간
  trigger_condition: string  # 추가 발생 조건
  type: enum  # [news, market_shock, opportunity, mentor_advice]
  
  market_impact:
    affected_sectors: [string]
    price_change_range: [float, float]  # 가격 변동 범위
    volume_multiplier: float
    duration: minutes
    
  player_options:
    - id: string
      description: string
      consequences: MarketImpact
      mentor_reaction: string
      
  news_content:
    headline: string
    content: string
    sentiment: enum  # [very_negative, negative, neutral, positive, very_positive]
    reliability: float  # 0.0-1.0, 정보의 신뢰도
```

이제 **완전한 미션 시스템 구조**가 완성되었습니다! 

다음 단계로 이 구조를 바탕으로 **실제 구현 가능한 코드**를 만들어볼까요?