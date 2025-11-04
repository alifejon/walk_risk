"""FastAPI 메인 애플리케이션"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from .routers import (
    auth_router,
    players_router,
    puzzles_router,
    mentors_router,
    tutorials_router,
    portfolio_router,
    market_router
)
from ..services import (
    PlayerService,
    PuzzleService,
    MentorService,
    TutorialService,
    PortfolioService,
    MarketService
)
from ..core.game_state.game_manager import GameManager
from ..database.connection import database
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

# 전역 서비스 인스턴스들
game_manager = None
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    global game_manager, services

    # 시작 시 초기화
    logger.info("Initializing Walk Risk API...")

    try:
        # 데이터베이스 연결
        await database.connect()

        # 게임 매니저 초기화
        game_manager = GameManager()

        # 서비스들 초기화
        services["player"] = PlayerService(game_manager)
        services["puzzle"] = PuzzleService()
        services["mentor"] = MentorService()
        services["tutorial"] = TutorialService(game_manager)
        services["portfolio"] = PortfolioService()
        services["market"] = MarketService()

        # 모든 서비스 초기화
        for service_name, service in services.items():
            await service.initialize()
            logger.info(f"{service_name} service initialized")

        # 앱에 서비스들 등록
        app.state.game_manager = game_manager
        app.state.services = services

        logger.info("Walk Risk API initialized successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise

    finally:
        # 종료 시 정리
        logger.info("Shutting down Walk Risk API...")
        await database.disconnect()


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 생성"""

    app = FastAPI(
        title="InvestWalk API",
        description="Walk Risk 투자 학습 게임 API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발 시에만 * 사용
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(auth_router, prefix="/v1/auth", tags=["Authentication"])
    app.include_router(players_router, prefix="/v1/players", tags=["Players"])
    app.include_router(puzzles_router, prefix="/v1/puzzles", tags=["Puzzles"])
    app.include_router(mentors_router, prefix="/v1/mentors", tags=["Mentors"])
    app.include_router(tutorials_router, prefix="/v1/tutorial", tags=["Tutorial"])
    app.include_router(portfolio_router, prefix="/v1/portfolio", tags=["Portfolio"])
    app.include_router(market_router, prefix="/v1/market", tags=["Market"])

    # 헬스체크 엔드포인트
    @app.get("/health")
    async def health_check():
        """API 헬스체크"""
        return {
            "status": "healthy",
            "timestamp": "2025-09-30T16:00:00Z",
            "version": "1.0.0"
        }

    # 루트 엔드포인트
    @app.get("/")
    async def root():
        """API 루트"""
        return {
            "message": "InvestWalk API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }

    return app


# 애플리케이션 인스턴스 생성
app = create_app()


def run_development_server():
    """개발 서버 실행"""
    uvicorn.run(
        "walk_risk.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    run_development_server()