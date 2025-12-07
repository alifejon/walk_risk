# 🚀 InvestWalk MVP 개발 계획 (개선된 6주 로드맵)

## 📊 현실적 스코프 재정의

### 핵심 MVP 범위 (Zero Phase 결정사항)
- **플랫폼 우선순위**: 모바일보다 **웹 우선** → PWA로 모바일 경험 제공
- **기존 Rich CLI 유지**: 개발자/테스터용으로 계속 활용
- **점진적 마이그레이션**: 한 번에 전체 재작성하지 않고 레이어별 추가

### MVP 핵심 기능 (기존 시스템 80% 활용)
1. **Risk Puzzle System**: 이미 완전 구현됨 (`walk_risk/core/risk_puzzle/`)
2. **AI Mentor System**: 5명 멘토 with 상황별 피드백 (`walk_risk/ai/mentor_personas.py`)
3. **Tutorial System**: 7단계 학습 경로 (`walk_risk/tutorials/`)
4. **Real-time Trading**: Yahoo Finance API 연동 (`walk_risk/core/trading/`)

## 🗓️ 6주 현실적 개발 로드맵

### Week 1: 아키텍처 & 서비스 레이어 (5일)
**목표**: 기존 로직을 API로 노출 가능한 서비스 레이어 추출

#### Day 1-2: MVP 스코프 확정 & 종속성 매핑
- [x] MVP 핵심 기능 확정
- [x] API 계약서 초안 작성 (`docs/api_contract.md`)
- [ ] 데이터베이스 스키마 설계 (SQLite → PostgreSQL 경로)

#### Day 3-5: 서비스 레이어 구현
- [x] `walk_risk/services/` 모듈 생성 (퍼즐/튜토리얼/플레이어/멘토/포트폴리오)
- [x] `PuzzleService`, `TutorialService`, `PlayerService` 클래스 및 FastAPI 라우터 연결
- [x] 기존 CLI 호환성 유지하면서 FastAPI 엔드포인트 초안 추가 (`walk_risk/api/`)
- [x] FastAPI 의존성 정식 반영 (`pyproject.toml` 업데이트 + `uv sync` 완료)

#### Week 1 회고 (2025-09-30)
- 서비스 레이어와 API 라우터가 Lifespan 부트스트랩과 함께 동작하도록 구성 완료 (`api_server.py`, `walk_risk/api/main.py`).
- `python -m compileall walk_risk`로 런타임 오류가 없음을 확인했고, FastAPI/uvicorn 의존성을 추가한 뒤 `uv sync`, `uv run python api_server.py`까지 확인 완료 (reloader 재시작 경고는 기본 설정).
- 퍼즐/튜토리얼/플레이어 흐름은 모의 데이터 기반으로 API에 노출되었으며, DB 및 인증 레이어가 추가될 때까지 인메모리 스토리지 유지.
- 다음 주 우선순위: 데이터베이스 스키마 설계, 서비스/라우터에 대한 pytest 스캐폴드 작성, 자동화된 헬스 체크 엔드포인트 준비.

### Week 2: 백엔드 인프라 & 데이터 (5일) ✅ 완료
**목표**: 안정적인 데이터 저장 및 인증 시스템

#### Day 1-3: 데이터베이스 & 마이그레이션
- [x] SQLite + SQLAlchemy async 구현 (PostgreSQL 호환)
- [x] 기존 인메모리 데이터를 DB로 마이그레이션
- [x] Alembic 마이그레이션 설정

#### Day 4-5: 인증 & 세션 관리
- [x] JWT 기반 인증 시스템 (access + refresh token)
- [x] 플레이어 세션 관리
- [x] 기본적인 RBAC (역할 기반 접근 제어)

### Week 3: API 완성 & 테스트 (5일) ✅ 완료
**목표**: 안정적인 RESTful API 및 테스트 자동화

#### Day 1-3: FastAPI 엔드포인트 완성
- [x] CRUD 엔드포인트: 플레이어, 퍼즐, 진행도
- [x] 실시간 데이터 연동 (Yahoo Finance API via MarketService)
- [x] JWT 인증 모든 API에 적용

#### Day 4-5: 테스트 자동화
- [x] pytest 테스트 구조 생성 (`tests/`)
- [x] API 테스트 (auth, players, puzzles, portfolio)
- [x] 기존 CLI 데모 스크립트 유지

### Week 4: 웹 클라이언트 MVP (5일) ✅ 완료
**목표**: 반응형 웹 앱으로 핵심 기능 구현

#### Day 1-2: 프론트엔드 프레임워크 선택 & 설정
- [x] React 19 + Vite + TypeScript (빠른 개발)
- [x] Tailwind CSS + Framer Motion (neon 테마)
- [x] Axios + Zustand (API 연동 + 상태 관리)

#### Day 3-5: 핵심 화면 구현
- [x] 로그인/회원가입 (멘토 선택 포함)
- [x] 퍼즐 해결 인터페이스 (API 연동)
- [x] 진행도 대시보드 (통계 표시)
- [x] 포트폴리오 관리 화면

### Week 5: 인프라 & 배포 (5일)
**목표**: 프로덕션 준비 및 모니터링

#### Day 1-2: 컨테이너화 & CI/CD
- [ ] Dockerfile 작성
- [ ] GitHub Actions (자동 테스트 + 배포)
- [ ] 스테이징 환경 구축

#### Day 3-5: 모니터링 & 보안
- [ ] 로그 집계 (Sentry 또는 LogRocket)
- [ ] API 속도 제한
- [ ] 시크릿 관리 (환경 변수 + Vault)

### Week 6: 베타 테스트 & 피드백 (5일)
**목표**: 사용자 피드백 수집 및 개선

#### Day 1-2: 베타 환경 준비
- [ ] PWA 설정 (모바일 친화적)
- [ ] 사용자 분석 도구 (Google Analytics)
- [ ] 피드백 수집 도구

#### Day 3-5: 베타 테스트 실행
- [ ] 50명 클로즈드 베타 (네이버 카페/디스코드)
- [ ] A/B 테스트 (핵심 사용자 플로우)
- [ ] 버그 수정 및 UX 개선

## 🛠️ 기술 스택 최종 선택

### 백엔드
- **API**: FastAPI (기존 Python 코드 재사용)
- **데이터베이스**: PostgreSQL (Supabase)
- **인증**: JWT + bcrypt
- **캐시**: Redis (선택사항)

### 프론트엔드
- **1차**: Next.js (빠른 개발 + SEO)
- **2차**: Flutter (네이티브 앱으로 확장 시)

### 인프라
- **배포**: Vercel (프론트) + Railway/Render (백엔드)
- **모니터링**: Sentry + Plausible Analytics
- **CI/CD**: GitHub Actions

## 💰 예상 비용 (월간)
- **데이터베이스**: $10 (Supabase Pro)
- **배포**: $20 (Railway + Vercel)
- **모니터링**: $10 (Sentry 기본)
- **API**: $20 (Yahoo Finance Pro)
- **총계**: ~$60/월 (베타 기간)

## 🎯 성공 지표 & 위험 관리

### MVP 성공 지표
- **기술**: 99% 업타임, 2초 이하 응답 시간
- **사용자**: 주간 활성 사용자 30명+, 퍼즐 완료율 60%+
- **비즈니스**: NPS 7점 이상, 월 사용 시간 60분+

### 주요 위험 요소
1. **스택 전환 복잡성** → 기존 CLI 병행 유지로 리스크 완화
2. **API 의존성** → Yahoo Finance 장애 대비 캐싱 강화
3. **사용자 확보** → 기존 투자 커뮤니티와 파트너십

## 📋 문서화 & 품질 관리
- **개발 로그**: 매일 `docs/development_log_YYYY_MM_DD.md` 업데이트
- **API 문서**: FastAPI 자동 생성 + OpenAPI 스펙
- **사용자 가이드**: 기존 Korean 컨텐츠 활용
- **코드 리뷰**: 매 PR마다 자동 테스트 + 수동 검증

## 🚀 구현 우선순위

### Phase 1: 서비스 레이어 구현 (Week 1)
- [x] API 계약서 작성
- [x] 서비스 레이어 모듈 생성 (`walk_risk/services/`)
- [x] 기존 로직을 서비스로 추출하고 FastAPI 라우터와 연동
- [x] FastAPI/uvicorn 의존성 명시 및 `uv sync` 실행

### Phase 2: 데이터베이스 연동 (Week 2)
1. PostgreSQL 스키마 설계
2. 데이터 마이그레이션 스크립트
3. 인증 시스템 구현

### Phase 3: 웹 클라이언트 (Week 4)
1. 반응형 웹 앱 프로토타입
2. 핵심 사용자 플로우 구현

---

**이 계획은 기존 코드베이스의 80% 재사용으로 위험을 최소화하면서, 점진적으로 웹 서비스로 확장하는 현실적 접근법입니다.**

## 개발 시작일: 2025-09-30
## 예상 완료일: 2025-11-11 (6주)
