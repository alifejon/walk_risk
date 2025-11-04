# API 테스트 가이드

## 🚀 API 서버 실행

### 1. 의존성 설치
```bash
# FastAPI 의존성 설치
uv add fastapi uvicorn

# 또는 pip으로 설치
pip install fastapi uvicorn
```

### 2. 서버 실행 방법

#### 방법 1: 직접 실행
```bash
python api_server.py
```

#### 방법 2: uv 스크립트 사용
```bash
uv run walk-risk-api
```

#### 방법 3: uvicorn 직접 실행
```bash
uvicorn walk_risk.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인
서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **헬스체크**: http://localhost:8000/health

## 📡 API 엔드포인트 테스트

### 기본 헬스체크
```bash
curl http://localhost:8000/health
```

### 플레이어 정보 조회
```bash
curl http://localhost:8000/v1/players/me
```

### 퍼즐 목록 조회
```bash
curl http://localhost:8000/v1/puzzles/
```

### 멘토 목록 조회
```bash
curl http://localhost:8000/v1/mentors/
```

### 시장 개요 조회
```bash
curl http://localhost:8000/v1/market/overview
```

## 🧪 고급 테스트

### 1. 퍼즐 조사 API 테스트
```bash
curl -X POST http://localhost:8000/v1/puzzles/{puzzle_id}/investigate \
  -H "Content-Type: application/json" \
  -d '{
    "clue_id": "clue_123",
    "investigation_type": "news"
  }'
```

### 2. 멘토에게 질문하기
```bash
curl -X POST http://localhost:8000/v1/mentors/buffett/ask \
  -H "Content-Type: application/json" \
  -d '{
    "context": "puzzle",
    "question": "이 상황에서 어떻게 판단해야 할까요?",
    "current_situation": {
      "puzzle_id": "puzzle_123",
      "discovered_clues": ["news_analysis"]
    }
  }'
```

### 3. 포트폴리오 주문 실행
```bash
curl -X POST http://localhost:8000/v1/portfolio/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "005930.KS",
    "order_type": "market",
    "side": "buy",
    "quantity": 10,
    "reason": "퍼즐 해결 결과 매수 판단"
  }'
```

## 🔧 개발 환경 설정

### 환경 변수
`.env` 파일을 생성하여 필요한 환경 변수를 설정하세요:

```env
# API 설정
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# 데이터베이스 (추후 구현)
DATABASE_URL=sqlite:///./walk_risk.db

# 외부 API 키 (추후 필요)
YAHOO_FINANCE_API_KEY=your_api_key_here
```

### CORS 설정
개발 환경에서는 모든 도메인에서의 접근을 허용하도록 설정되어 있습니다.
프로덕션에서는 특정 도메인만 허용하도록 수정해야 합니다.

## 🚨 현재 구현 상태

### ✅ 완료된 기능
- FastAPI 기본 구조
- 모든 주요 엔드포인트 스켈레톤
- 서비스 레이어 아키텍처
- API 문서 자동 생성
- 기본 에러 처리

### 🔄 진행 중인 기능
- 실제 비즈니스 로직 연동
- 데이터베이스 연결
- 인증 시스템

### 📋 TODO
- JWT 인증 구현
- 데이터베이스 연동
- 실시간 시장 데이터 연동
- 테스트 코드 작성
- 로깅 시스템 강화

## 🐛 문제 해결

### 포트 충돌 시
다른 포트로 실행:
```bash
uvicorn walk_risk.api.main:app --port 8001
```

### 모듈 import 오류 시
프로젝트 루트에서 실행하고 PYTHONPATH 확인:
```bash
export PYTHONPATH=/Users/alifejon/Documents/GitHub/walk_risk:$PYTHONPATH
python api_server.py
```

### 의존성 오류 시
최신 의존성 설치:
```bash
uv sync --upgrade
```

## 📊 모니터링

### 로그 확인
API 서버는 기본적으로 INFO 레벨 로그를 출력합니다.
상세한 디버깅이 필요한 경우 로그 레벨을 DEBUG로 변경하세요.

### 성능 테스트
```bash
# 간단한 부하 테스트 (Apache Bench 필요)
ab -n 100 -c 10 http://localhost:8000/health
```

이제 Walk Risk의 핵심 기능들이 REST API로 제공됩니다!
기존 CLI 시스템과 새로운 API 시스템이 동일한 비즈니스 로직을 공유하므로
일관된 사용자 경험을 제공할 수 있습니다.