# Walk Risk 배포 가이드

## 빠른 배포 (권장)

### Option A: Railway + Vercel (무료 티어 가능)

#### 1. 백엔드 배포 (Railway)

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 새 프로젝트 생성
railway init

# 환경 변수 설정
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set DEBUG=false
railway variables set LOG_LEVEL=INFO
railway variables set CORS_ORIGINS=https://your-app.vercel.app

# 배포
railway up
```

**Railway 대시보드에서 설정:**
1. https://railway.app 접속
2. 프로젝트 선택 → Settings → Domains
3. 커스텀 도메인 또는 Railway 제공 도메인 확인
4. 환경 변수 확인 (Variables 탭)

#### 2. 프론트엔드 배포 (Vercel)

```bash
# Vercel CLI 설치
npm install -g vercel

# web-ui 디렉토리로 이동
cd web-ui

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

**Vercel 대시보드에서 설정:**
1. https://vercel.com 접속
2. 프로젝트 선택 → Settings → Environment Variables
3. `VITE_API_URL` 추가: Railway 백엔드 URL (예: `https://walkrisk-api.up.railway.app`)

---

### Option B: Render (올인원)

Render는 백엔드 + 프론트엔드 + DB를 한 곳에서 관리할 수 있습니다.

```bash
# render.yaml이 이미 설정되어 있음
# Render 대시보드에서 Blueprint 배포:
```

1. https://render.com 접속
2. Dashboard → Blueprints → New Blueprint Instance
3. GitHub 저장소 연결
4. `render.yaml` 자동 감지됨
5. Deploy 클릭

---

## 수동 배포

### Docker Compose (자체 서버)

```bash
# 프로덕션 빌드 및 실행
docker-compose -f docker-compose.yml up -d --build

# 로그 확인
docker-compose logs -f

# PostgreSQL 포함 (프로덕션)
docker-compose --profile production up -d --build
```

### 개별 Docker 배포

```bash
# 백엔드 이미지 빌드
docker build -t walkrisk-backend .

# 프론트엔드 이미지 빌드
docker build -t walkrisk-frontend ./web-ui \
  --build-arg VITE_API_URL=https://api.walkrisk.com

# 백엔드 실행
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://... \
  walkrisk-backend

# 프론트엔드 실행
docker run -d -p 80:80 walkrisk-frontend
```

---

## 환경 변수 체크리스트

### 백엔드 (필수)

| 변수 | 설명 | 예시 |
|------|------|------|
| `SECRET_KEY` | JWT 서명 키 (32자 이상) | `openssl rand -hex 32` |
| `DATABASE_URL` | DB 연결 문자열 | `postgresql+asyncpg://user:pass@host:5432/db` |
| `CORS_ORIGINS` | 허용 도메인 (쉼표 구분) | `https://walkrisk.com` |

### 백엔드 (선택)

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `DEBUG` | 디버그 모드 | `false` |
| `LOG_LEVEL` | 로그 레벨 | `INFO` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 액세스 토큰 만료 | `30` |

### 프론트엔드 (필수)

| 변수 | 설명 | 예시 |
|------|------|------|
| `VITE_API_URL` | 백엔드 API URL | `https://api.walkrisk.com` |

---

## 배포 후 확인

### 1. Health Check

```bash
# 백엔드 상태 확인
curl https://your-api-url.com/health

# 예상 응답
{"status":"healthy","timestamp":"...","version":"1.0.0"}

# Readiness 확인
curl https://your-api-url.com/health/ready
```

### 2. API 문서 접근

- Swagger UI: `https://your-api-url.com/docs`
- ReDoc: `https://your-api-url.com/redoc`

### 3. 프론트엔드 확인

- 로그인 페이지 접근
- PWA 설치 프롬프트 확인 (모바일)
- Service Worker 등록 확인 (DevTools → Application)

---

## 문제 해결

### CORS 오류

```bash
# 백엔드 환경 변수 확인
railway variables get CORS_ORIGINS

# 프론트엔드 도메인이 포함되어 있는지 확인
# 쉼표로 여러 도메인 추가 가능:
# https://walkrisk.com,https://www.walkrisk.com
```

### 데이터베이스 연결 실패

```bash
# Railway에서 PostgreSQL 추가
railway add --name postgres

# 연결 문자열 확인
railway variables get DATABASE_URL
```

### 빌드 실패

```bash
# 로컬에서 빌드 테스트
docker build -t test-backend .
docker build -t test-frontend ./web-ui

# 로그 확인
docker logs <container-id>
```

---

## 비용 예상 (월간)

| 서비스 | Free Tier | Pro |
|--------|-----------|-----|
| Railway (Backend) | $5 크레딧 | ~$10 |
| Vercel (Frontend) | 무료 | 무료 |
| Render (All-in-one) | 무료 | ~$15 |
| Supabase (DB) | 무료 | $25 |

**권장**: Railway + Vercel 조합으로 시작 → 트래픽 증가 시 업그레이드

---

## CI/CD 파이프라인

GitHub Actions가 이미 설정되어 있습니다:

- **PR/Push**: 자동 테스트 + 빌드 검증
- **main 브랜치**: 스테이징 자동 배포
- **태그 (v*)**: 프로덕션 배포

```bash
# 프로덕션 릴리스
git tag v1.0.0
git push origin v1.0.0
```

---

*최종 업데이트: 2025-12-07*
