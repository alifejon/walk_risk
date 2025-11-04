"""API 라우터 모듈"""

from .auth import router as auth_router
from .players import router as players_router
from .puzzles import router as puzzles_router
from .mentors import router as mentors_router
from .tutorials import router as tutorials_router
from .portfolio import router as portfolio_router
from .market import router as market_router

__all__ = [
    "auth_router",
    "players_router",
    "puzzles_router",
    "mentors_router",
    "tutorials_router",
    "portfolio_router",
    "market_router"
]