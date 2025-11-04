# InvestWalk API 계약서 v1.0

## 📋 API 개요

Walk Risk 시스템을 웹 서비스로 제공하기 위한 RESTful API 명세서입니다.
기존 CLI 시스템의 모든 기능을 HTTP 엔드포인트로 노출합니다.

**Base URL**: `https://api.investwalk.app/v1`
**인증 방식**: JWT Bearer Token
**응답 형식**: JSON

## 🔐 인증 엔드포인트

### POST /auth/register
사용자 등록

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "preferred_mentor": "buffett" // "buffett", "lynch", "graham", "dalio", "wood"
}
```

**Response (201):**
```json
{
  "user_id": "uuid",
  "username": "string",
  "email": "string",
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "expires_in": 3600
}
```

### POST /auth/login
사용자 로그인

**Request Body:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "user_id": "uuid",
  "access_token": "jwt_token",
  "refresh_token": "jwt_token",
  "expires_in": 3600
}
```

## 👤 플레이어 관리

### GET /players/me
현재 사용자 정보 조회

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "level": 5,
  "experience": 1250,
  "current_class": "Risk Walker",
  "unlocked_skills": ["market_analysis", "risk_assessment"],
  "tutorial_progress": {
    "current_stage": "graduation",
    "completion_rate": 85.5,
    "completed_stages": ["welcome", "mentor_selection"]
  },
  "created_at": "2025-09-30T10:00:00Z",
  "last_active": "2025-09-30T15:30:00Z"
}
```

### PUT /players/me
사용자 정보 업데이트

**Request Body:**
```json
{
  "preferred_mentor": "lynch",
  "settings": {
    "notifications": true,
    "difficulty": "intermediate"
  }
}
```

## 🧩 퍼즐 시스템

### GET /puzzles
사용 가능한 퍼즐 목록 조회

**Query Parameters:**
- `difficulty`: string (optional) - "beginner", "intermediate", "advanced", "master"
- `type`: string (optional) - "price_drop", "price_surge", "volatility", "divergence", "mystery"
- `limit`: int (optional) - 기본값 10
- `offset`: int (optional) - 기본값 0

**Response (200):**
```json
{
  "puzzles": [
    {
      "puzzle_id": "uuid",
      "title": "삼성전자 -6.2% 미스터리",
      "description": "삼성전자가 갑자기 6.2% 하락했습니다. 무엇이 원인일까요?",
      "difficulty": "beginner",
      "type": "price_drop",
      "target_symbol": "005930.KS",
      "estimated_time": 15,
      "reward_xp": 150,
      "is_solved": false,
      "created_at": "2025-09-30T09:00:00Z"
    }
  ],
  "total": 25,
  "has_more": true
}
```

### GET /puzzles/{puzzle_id}
특정 퍼즐 상세 조회

**Response (200):**
```json
{
  "puzzle_id": "uuid",
  "title": "삼성전자 -6.2% 미스터리",
  "description": "삼성전자가 갑자기 6.2% 하락했습니다...",
  "difficulty": "beginner",
  "type": "price_drop",
  "target_symbol": "005930.KS",
  "event_data": {
    "price_change": -6.2,
    "volume": 15000000,
    "date": "2025-09-30",
    "market_context": "코스피 -1.2%"
  },
  "available_clues": [
    {
      "clue_id": "uuid",
      "source": "news",
      "title": "뉴스 조사",
      "cost": 0,
      "is_discovered": false
    },
    {
      "clue_id": "uuid",
      "source": "financials",
      "title": "재무 분석",
      "cost": 10,
      "is_discovered": false
    }
  ],
  "discovered_clues": [],
  "player_progress": {
    "investigation_count": 0,
    "hypothesis_submitted": false,
    "start_time": null
  }
}
```

### POST /puzzles/{puzzle_id}/investigate
단서 조사 실행

**Request Body:**
```json
{
  "clue_id": "uuid",
  "investigation_type": "news" // "news", "financials", "technical", "social"
}
```

**Response (200):**
```json
{
  "clue": {
    "clue_id": "uuid",
    "source": "news",
    "content": "삼성전자가 새로운 반도체 투자 계획을 발표했습니다...",
    "relevance_score": 0.85,
    "discovery_time": "2025-09-30T15:45:00Z"
  },
  "investigation_result": {
    "new_insights": ["반도체 투자", "장기 성장"],
    "energy_consumed": 10,
    "remaining_energy": 90
  }
}
```

### POST /puzzles/{puzzle_id}/hypothesis
가설 제출

**Request Body:**
```json
{
  "hypothesis": "일시적 과매도 상황으로 판단됩니다",
  "confidence": 75,
  "evidence": [
    "반도체 투자 발표는 긍정적 신호",
    "시장 전체 하락 대비 과도한 반응"
  ],
  "predicted_outcome": "short_term_recovery"
}
```

**Response (200):**
```json
{
  "hypothesis_id": "uuid",
  "validation_result": {
    "accuracy_score": 82,
    "correct_aspects": ["투자 발표 해석", "시장 상황 분석"],
    "missed_aspects": ["기술적 지표 미고려"],
    "mentor_feedback": "좋은 관찰이었습니다. 하지만 기술적 지표도...",
    "is_correct": true
  },
  "rewards": {
    "xp_gained": 150,
    "skills_unlocked": ["market_analysis_basic"],
    "achievements": ["first_puzzle_solved"]
  }
}
```

## 🎓 튜토리얼 시스템

### GET /tutorial/progress
튜토리얼 진행 상황 조회

**Response (200):**
```json
{
  "current_stage": "first_risk",
  "completion_rate": 40.5,
  "completed_stages": ["welcome", "mentor_selection"],
  "available_stages": ["portfolio_basics"],
  "stage_data": {
    "mentor": "buffett",
    "puzzles_completed": 2,
    "skills_learned": ["basic_investigation"]
  }
}
```

### POST /tutorial/{stage}/complete
튜토리얼 단계 완료

**Request Body:**
```json
{
  "stage_results": {
    "time_spent": 300,
    "actions_taken": 15,
    "success_rate": 0.8
  }
}
```

**Response (200):**
```json
{
  "stage_completed": "first_risk",
  "next_stage": "portfolio_basics",
  "rewards": {
    "xp_gained": 100,
    "features_unlocked": ["advanced_investigation"]
  },
  "mentor_message": "축하합니다! 첫 번째 리스크를 성공적으로..."
}
```

## 🤖 AI 멘토 시스템

### GET /mentors
사용 가능한 멘토 목록

**Response (200):**
```json
{
  "mentors": [
    {
      "id": "buffett",
      "name": "Warren Buffett",
      "specialty": "Value Investing",
      "description": "장기 가치 투자의 대가",
      "personality_traits": ["patient", "analytical", "conservative"],
      "is_available": true
    },
    {
      "id": "lynch",
      "name": "Peter Lynch",
      "specialty": "Growth Investing",
      "description": "성장주 투자의 전설",
      "personality_traits": ["energetic", "curious", "practical"],
      "is_available": true
    }
  ]
}
```

### POST /mentors/{mentor_id}/ask
멘토에게 조언 요청

**Request Body:**
```json
{
  "context": "puzzle", // "puzzle", "general", "portfolio"
  "question": "이 상황에서 어떻게 판단해야 할까요?",
  "current_situation": {
    "puzzle_id": "uuid",
    "discovered_clues": ["news_analysis", "financial_data"],
    "player_state": "investigating"
  }
}
```

**Response (200):**
```json
{
  "mentor_response": {
    "message": "이런 상황에서는 먼저...",
    "advice_type": "hint", // "hint", "encouragement", "warning", "explanation"
    "personality_note": "차분하고 신중한 어조",
    "suggested_actions": [
      "추가 재무 데이터 확인",
      "경쟁사 상황 비교"
    ]
  },
  "context_updates": {
    "interaction_count": 3,
    "mentor_relationship": "developing"
  }
}
```

## 📊 포트폴리오 & 거래

### GET /portfolio
현재 포트폴리오 조회

**Response (200):**
```json
{
  "portfolio_id": "uuid",
  "total_value": 10150000,
  "cash_balance": 2500000,
  "total_return": 1.5,
  "holdings": [
    {
      "symbol": "005930.KS",
      "name": "삼성전자",
      "quantity": 100,
      "avg_price": 75000,
      "current_price": 76500,
      "market_value": 7650000,
      "unrealized_pnl": 150000,
      "weight": 75.3
    }
  ],
  "recent_trades": [
    {
      "trade_id": "uuid",
      "symbol": "005930.KS",
      "type": "buy",
      "quantity": 50,
      "price": 74000,
      "timestamp": "2025-09-30T14:30:00Z"
    }
  ]
}
```

### POST /portfolio/orders
주문 실행

**Request Body:**
```json
{
  "symbol": "005930.KS",
  "order_type": "market", // "market", "limit"
  "side": "buy", // "buy", "sell"
  "quantity": 10,
  "price": 76000, // limit 주문인 경우
  "reason": "퍼즐 해결 결과 매수 판단"
}
```

**Response (201):**
```json
{
  "order_id": "uuid",
  "status": "filled", // "pending", "filled", "cancelled"
  "execution_price": 76200,
  "execution_time": "2025-09-30T15:35:00Z",
  "portfolio_update": {
    "new_cash_balance": 2238000,
    "new_position": {
      "symbol": "005930.KS",
      "quantity": 110
    }
  }
}
```

## 📈 마켓 데이터

### GET /market/symbols
검색 가능한 종목 목록

**Query Parameters:**
- `search`: string (optional) - 종목명 또는 심볼 검색
- `market`: string (optional) - "KRX", "NASDAQ", "NYSE"

**Response (200):**
```json
{
  "symbols": [
    {
      "symbol": "005930.KS",
      "name": "삼성전자",
      "market": "KRX",
      "sector": "Technology",
      "is_tradable": true
    }
  ]
}
```

### GET /market/quote/{symbol}
실시간 시세 조회

**Response (200):**
```json
{
  "symbol": "005930.KS",
  "name": "삼성전자",
  "current_price": 76500,
  "change": -4800,
  "change_percent": -5.9,
  "volume": 12500000,
  "market_cap": 456789000000,
  "last_updated": "2025-09-30T15:40:00Z",
  "trading_session": "market_hours"
}
```

## 🏆 게임화 요소

### GET /achievements
달성 가능한 업적 목록

**Response (200):**
```json
{
  "achievements": [
    {
      "id": "first_puzzle",
      "name": "첫 번째 퍼즐 마스터",
      "description": "첫 번째 퍼즐을 성공적으로 해결하세요",
      "icon": "🧩",
      "reward_xp": 100,
      "is_unlocked": true,
      "unlocked_at": "2025-09-30T14:00:00Z"
    }
  ]
}
```

### GET /leaderboard
리더보드 조회

**Query Parameters:**
- `period`: string - "daily", "weekly", "monthly", "all_time"
- `metric`: string - "xp", "puzzles_solved", "accuracy"

**Response (200):**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "uuid",
      "username": "투자마스터",
      "score": 2500,
      "metric": "total_xp"
    }
  ],
  "my_rank": {
    "rank": 15,
    "score": 1250
  }
}
```

## 🚨 에러 응답 형식

모든 에러는 다음 형식으로 응답됩니다:

```json
{
  "error": {
    "code": "PUZZLE_NOT_FOUND",
    "message": "요청한 퍼즐을 찾을 수 없습니다",
    "details": {
      "puzzle_id": "invalid_uuid"
    }
  },
  "timestamp": "2025-09-30T15:45:00Z",
  "request_id": "req_uuid"
}
```

### 주요 에러 코드
- `UNAUTHORIZED`: 인증 실패
- `FORBIDDEN`: 권한 없음
- `PUZZLE_NOT_FOUND`: 퍼즐 없음
- `INSUFFICIENT_ENERGY`: 에너지 부족
- `INVALID_HYPOTHESIS`: 잘못된 가설
- `MARKET_CLOSED`: 장 마감
- `RATE_LIMIT_EXCEEDED`: 요청 한도 초과

## 📝 데이터 모델

### Player
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "level": "integer",
  "experience": "integer",
  "current_class": "string",
  "energy": "integer",
  "max_energy": "integer",
  "settings": "object",
  "created_at": "datetime",
  "last_active": "datetime"
}
```

### Puzzle
```json
{
  "puzzle_id": "uuid",
  "title": "string",
  "description": "string",
  "difficulty": "enum",
  "type": "enum",
  "target_symbol": "string",
  "event_data": "object",
  "hidden_truth": "string",
  "correct_hypothesis": "string",
  "base_reward_xp": "integer",
  "time_limit": "integer",
  "created_at": "datetime"
}
```

이 API 계약서는 기존 Walk Risk 시스템의 모든 기능을 HTTP 엔드포인트로 매핑하여, CLI와 웹 클라이언트 모두에서 동일한 비즈니스 로직을 사용할 수 있도록 설계되었습니다.