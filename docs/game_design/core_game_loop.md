# 🎮 Walk Risk: 핵심 게임 루프 설계

## 🎯 게임의 핵심 목표
**"실제 투자 위기 상황에서 살아남으면서 성장하는 투자자 되기"**

## 🔄 핵심 게임 루프 (Core Game Loop)

### 현재 문제점
```
❌ 기존: 데이터 보기 → 매수/매도 → 수익 확인 → 끝 (지루함)
```

### 새로운 게임 루프
```
✅ 게임: 미션 받기 → 전략 수립 → 실행 → 위기 대응 → 평가 → 보상 → 성장 → 새 미션
```

## 📋 상세한 게임 플로우

### 1단계: 미션 브리핑 (Mission Briefing)
```yaml
미션 예시:
  title: "2008년 금융위기 생존하기"
  background: "서브프라임 모기지 위기가 시작되었습니다..."
  objectives:
    primary: "12개월 후 손실 50% 이하 유지"
    secondary: 
      - "금융주 비중 20% 이하 유지"
      - "3개 이상 다른 섹터 투자"
      - "현금 비중 20% 이상 유지"
  initial_funds: 10_000_000  # 1천만원
  time_limit: 30  # 실제 시간 30분 = 게임 내 12개월
  difficulty: "Hard"
  mentor: "Warren Buffett"
```

**게임적 요소:**
- 📊 **명확한 목표**: 수치화된 성공 조건
- ⏰ **시간 압박**: 제한 시간 내 결정
- 🎯 **멀티 목표**: 단순 수익률이 아닌 복합 평가
- 🏆 **난이도**: Easy/Normal/Hard/Expert

### 2단계: 전략 수립 (Strategy Planning)
```yaml
전략 수립 도구:
  portfolio_planner:
    - sector_allocation: "섹터별 비중 계획"
    - risk_tolerance: "리스크 허용 수준 설정"  
    - cash_reserve: "현금 보유 비율"
    - stop_loss_rules: "손절매 규칙"
  market_analysis:
    - technical_indicators: "기술적 지표 분석"
    - fundamental_data: "기업 펀더멘털"
    - news_sentiment: "뉴스 심리 분석"
    - mentor_advice: "멘토 조언"
```

**게임적 요소:**
- 🧠 **전략적 사고**: 단순 클릭이 아닌 계획 수립
- 📈 **분석 도구**: 게임 내 차트와 지표
- 🤖 **AI 도움**: 멘토의 맞춤형 조언
- 💡 **학습 요소**: 실제 투자 지식 습득

### 3단계: 실행 (Execution)
```yaml
실행 인터페이스:
  trading_interface:
    - drag_drop_trading: "드래그 앤 드롭으로 간편 거래"
    - order_types: [market, limit, stop_loss, take_profit]
    - position_sizing: "포지션 크기 조절 슬라이더"
    - confirmation_dialog: "거래 확인 대화상자"
  real_time_updates:
    - live_prices: "실시간 주가 업데이트"
    - news_alerts: "중요 뉴스 팝업"
    - portfolio_changes: "포트폴리오 변화 애니메이션"
```

**게임적 요소:**
- 🎮 **직관적 조작**: 게임 같은 인터페이스
- ⚡ **즉각적 피드백**: 거래 시 시각/음향 효과
- 📱 **반응형 UI**: 매끄러운 애니메이션
- 🔊 **사운드 디자인**: 거래 성공/실패 사운드

### 4단계: 위기 대응 (Crisis Management)
```yaml
위기 이벤트:
  market_crash:
    trigger: "주식 시장 10% 이상 급락"
    duration: "3-5분 (게임 시간)"
    player_options:
      - panic_sell: "공포 매도 (손실 확정)"
      - hold_position: "포지션 유지 (리스크 감수)"
      - buy_more: "추가 매수 (기회 포착)"
      - hedge_position: "헤지 포지션 (리스크 중립)"
    mentor_reaction: "실시간 멘토 조언"
    consequences: "선택에 따른 결과"
```

**게임적 요소:**
- 🚨 **긴장감**: 예상치 못한 위기 상황
- ⚡ **빠른 판단**: 제한 시간 내 결정
- 🎭 **선택과 결과**: 플레이어 결정이 결과에 영향
- 🎬 **드라마틱**: 실제 역사적 사건 재현

### 5단계: 평가 (Evaluation)
```yaml
성과 평가 시스템:
  performance_metrics:
    - total_return: "총 수익률"
    - risk_adjusted_return: "샤프 비율"
    - maximum_drawdown: "최대 손실"
    - diversification_score: "분산투자 점수"
    - crisis_response_score: "위기 대응 점수"
  scoring_system:
    S_rank: 90-100점 (전설적 투자자)
    A_rank: 80-89점 (뛰어난 투자자)
    B_rank: 70-79점 (좋은 투자자)
    C_rank: 60-69점 (평범한 투자자)
    D_rank: 0-59점 (개선 필요)
```

**게임적 요소:**
- 🏆 **등급 시스템**: S/A/B/C/D 랭크
- 📊 **상세 분석**: 어디서 잘했고 못했는지
- 📈 **진전 추적**: 이전 게임과 비교
- 🎖️ **업적 해제**: 특별한 성과 달성 시

### 6단계: 보상 (Rewards)
```yaml
보상 시스템:
  experience_points:
    base_exp: "기본 경험치 (완주 시)"
    performance_bonus: "성과 보너스"
    perfect_bonus: "완벽한 플레이 보너스"
    discovery_bonus: "새로운 전략 발견"
  unlockables:
    new_mentors: "새로운 멘토 해제"
    advanced_tools: "고급 분석 도구"
    new_scenarios: "새로운 시나리오"
    special_achievements: "특별 업적"
  virtual_rewards:
    certificates: "투자 인증서"
    portfolio_showcase: "포트폴리오 전시"
    leaderboard_entry: "리더보드 등록"
```

**게임적 요소:**
- 🎁 **즉각적 보상**: 게임 완료 시 바로 보상
- 🔓 **언락 시스템**: 새로운 콘텐츠 해제
- 🏅 **수집 요소**: 업적, 인증서 수집
- 🌟 **희귀성**: 특별한 보상의 가치

### 7단계: 성장 (Character Growth)
```yaml
캐릭터 성장 시스템:
  investor_level:
    level_1_10: "초보 투자자 (Novice Investor)"
    level_11_20: "경험있는 투자자 (Experienced)"
    level_21_30: "숙련된 투자자 (Skilled)"
    level_31_40: "전문 투자자 (Professional)"
    level_41_50: "마스터 투자자 (Master)"
  skill_trees:
    value_investing: "가치투자 스킬 (버핏 스타일)"
    growth_investing: "성장투자 스킬 (린치 스타일)"
    risk_management: "리스크관리 스킬 (달리오 스타일)"
    technical_analysis: "기술적분석 스킬 (차트 분석)"
  passive_abilities:
    - "거래 수수료 할인"
    - "고급 지표 해제"
    - "멘토 조언 빈도 증가"
    - "위기 상황 조기 감지"
```

**게임적 요소:**
- ⬆️ **레벨업**: 명확한 진행감
- 🌳 **스킬 트리**: 플레이어 선택의 자유
- 💪 **능력 향상**: 게임 플레이가 실제로 향상
- 📚 **지식 습득**: 실제 투자 지식도 함께 성장

### 8단계: 새로운 미션 (Next Mission)
```yaml
미션 진행 시스템:
  difficulty_scaling:
    - 플레이어 레벨에 따른 난이도 조정
    - 이전 성과에 따른 도전 과제
    - 새로운 시장 상황과 시나리오
  story_progression:
    - 연대기 순서로 역사적 사건 경험
    - 각 멘토별 특별 스토리라인
    - 플레이어 선택에 따른 분기점
  endless_mode:
    - 랜덤 생성되는 시장 상황
    - 무한정 플레이 가능
    - 리더보드 경쟁
```

**게임적 요소:**
- 🔄 **반복성**: 계속 하고 싶게 만드는 루프
- 📈 **점진적 도전**: 조금씩 어려워지는 난이도
- 📖 **스토리 진행**: 연결된 이야기
- 🏃‍♂️ **끝없는 도전**: 엔드게임 콘텐츠

## 🎮 게임 루프의 핵심 원칙

### 1. 즉각적 피드백 (Immediate Feedback)
- 모든 행동에 즉각적인 시각/음향 피드백
- 실시간으로 변하는 수치와 그래프

### 2. 점진적 도전 (Progressive Challenge)  
- 처음에는 쉽게, 점차 복잡하게
- 플레이어 실력에 맞는 적절한 난이도

### 3. 의미있는 선택 (Meaningful Choices)
- 단순한 클릭이 아닌 전략적 판단
- 선택에 따른 명확한 결과

### 4. 성장의 실감 (Tangible Progress)
- 숫자로 보이는 성장
- 새로운 능력과 도구 해제

### 5. 사회적 요소 (Social Elements)
- 다른 플레이어와의 비교
- 공유하고 싶은 성과

## 🚀 다음 단계

이 게임 루프를 바탕으로:
1. **미션 시스템** 상세 설계
2. **평가 시스템** 알고리즘 구현  
3. **보상 시스템** 벨런스 조정
4. **첫 번째 시나리오** 구체적 제작

이제 진짜 **게임다운 게임**을 만들 수 있는 기반이 준비되었습니다!