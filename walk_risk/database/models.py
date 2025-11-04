"""Database models for Walk Risk"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .connection import Base


class User(Base):
    """사용자 모델"""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # 게임 관련 정보
    level: Mapped[int] = mapped_column(Integer, default=1)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    current_class: Mapped[str] = mapped_column(String(50), default="Risk Novice")
    energy: Mapped[int] = mapped_column(Integer, default=100)
    max_energy: Mapped[int] = mapped_column(Integer, default=100)

    # 설정 및 메타데이터
    settings: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    preferred_mentor: Mapped[str] = mapped_column(String(50), default="buffett")
    unlocked_skills: Mapped[List[str]] = mapped_column(JSON, default=list)
    unlocked_features: Mapped[List[str]] = mapped_column(JSON, default=list)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 관계
    portfolios: Mapped[List["Portfolio"]] = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    puzzle_progress: Mapped[List["PuzzleProgress"]] = relationship("PuzzleProgress", back_populates="user")
    tutorial_progress: Mapped[Optional["TutorialProgress"]] = relationship("TutorialProgress", back_populates="user", uselist=False)
    mentor_interactions: Mapped[List["MentorInteraction"]] = relationship("MentorInteraction", back_populates="user")

    __table_args__ = (
        Index('ix_users_username', 'username'),
        Index('ix_users_email', 'email'),
    )


class Portfolio(Base):
    """포트폴리오 모델"""
    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # 포트폴리오 정보
    name: Mapped[str] = mapped_column(String(100), default="기본 포트폴리오")
    initial_cash: Mapped[float] = mapped_column(Float, default=10000000.0)  # 초기 현금 1천만원
    current_cash: Mapped[float] = mapped_column(Float, default=10000000.0)
    total_value: Mapped[float] = mapped_column(Float, default=10000000.0)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="portfolios")
    positions: Mapped[List["Position"]] = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="portfolio")


class Position(Base):
    """포지션 모델"""
    __tablename__ = "positions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id: Mapped[str] = mapped_column(String(36), ForeignKey("portfolios.id"), nullable=False)

    # 포지션 정보
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    average_price: Mapped[float] = mapped_column(Float, nullable=False)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="positions")

    __table_args__ = (
        UniqueConstraint('portfolio_id', 'symbol', name='uq_position_portfolio_symbol'),
        Index('ix_positions_symbol', 'symbol'),
    )


class Order(Base):
    """주문 모델"""
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id: Mapped[str] = mapped_column(String(36), ForeignKey("portfolios.id"), nullable=False)

    # 주문 정보
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    order_type: Mapped[str] = mapped_column(String(20), nullable=False)  # market, limit
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # buy, sell
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float)

    # 실행 정보
    status: Mapped[str] = mapped_column(String(20), default="pending")
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    execution_price: Mapped[Optional[float]] = mapped_column(Float)

    # 메타데이터
    reason: Mapped[Optional[str]] = mapped_column(Text)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 관계
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="orders")

    __table_args__ = (
        Index('ix_orders_symbol', 'symbol'),
        Index('ix_orders_created_at', 'created_at'),
    )


class Puzzle(Base):
    """퍼즐 모델"""
    __tablename__ = "puzzles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # 퍼즐 정보
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # beginner, intermediate, advanced, master
    puzzle_type: Mapped[str] = mapped_column(String(20), nullable=False)  # price_drop, price_surge, etc.
    target_symbol: Mapped[str] = mapped_column(String(20), nullable=False)

    # 퍼즐 데이터
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    hidden_truth: Mapped[str] = mapped_column(Text, nullable=False)
    correct_hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    available_clues: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)

    # 보상 정보
    base_reward_xp: Mapped[int] = mapped_column(Integer, default=100)
    time_bonus_multiplier: Mapped[float] = mapped_column(Float, default=2.0)

    # 상태
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 관계
    progress_records: Mapped[List["PuzzleProgress"]] = relationship("PuzzleProgress", back_populates="puzzle")

    __table_args__ = (
        Index('ix_puzzles_difficulty', 'difficulty'),
        Index('ix_puzzles_type', 'puzzle_type'),
        Index('ix_puzzles_symbol', 'target_symbol'),
    )


class PuzzleProgress(Base):
    """퍼즐 진행도 모델"""
    __tablename__ = "puzzle_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    puzzle_id: Mapped[str] = mapped_column(String(36), ForeignKey("puzzles.id"), nullable=False)

    # 진행 상황
    investigation_count: Mapped[int] = mapped_column(Integer, default=0)
    discovered_clues: Mapped[List[str]] = mapped_column(JSON, default=list)
    clue_discovery_times: Mapped[Dict[str, str]] = mapped_column(JSON, default=dict)

    # 가설 관련
    hypothesis_submitted: Mapped[bool] = mapped_column(Boolean, default=False)
    hypothesis_text: Mapped[Optional[str]] = mapped_column(Text)
    confidence_level: Mapped[Optional[float]] = mapped_column(Float)
    evidence: Mapped[List[str]] = mapped_column(JSON, default=list)

    # 결과
    is_solved: Mapped[bool] = mapped_column(Boolean, default=False)
    accuracy_score: Mapped[Optional[float]] = mapped_column(Float)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)

    # 타임스탬프
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="puzzle_progress")
    puzzle: Mapped["Puzzle"] = relationship("Puzzle", back_populates="progress_records")

    __table_args__ = (
        UniqueConstraint('user_id', 'puzzle_id', name='uq_puzzle_progress_user_puzzle'),
        Index('ix_puzzle_progress_user', 'user_id'),
    )


class TutorialProgress(Base):
    """튜토리얼 진행도 모델"""
    __tablename__ = "tutorial_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, unique=True)

    # 진행 상황
    current_stage: Mapped[str] = mapped_column(String(50), default="welcome")
    completed_stages: Mapped[List[str]] = mapped_column(JSON, default=list)
    completion_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # 스테이지별 데이터
    stage_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    # 퍼즐 튜토리얼 진행도
    puzzle_tutorial_progress: Mapped[Dict[str, bool]] = mapped_column(JSON, default=dict)

    # 타임스탬프
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="tutorial_progress")


class MentorInteraction(Base):
    """멘토 상호작용 모델"""
    __tablename__ = "mentor_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)

    # 상호작용 정보
    mentor_id: Mapped[str] = mapped_column(String(50), nullable=False)  # buffett, lynch, etc.
    context: Mapped[str] = mapped_column(String(50), nullable=False)  # puzzle, general, portfolio
    question: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)

    # 메타데이터
    current_situation: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    helpfulness_rating: Mapped[Optional[int]] = mapped_column(Integer)  # 1-5

    # 타임스탬프
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # 관계
    user: Mapped["User"] = relationship("User", back_populates="mentor_interactions")

    __table_args__ = (
        Index('ix_mentor_interactions_user', 'user_id'),
        Index('ix_mentor_interactions_mentor', 'mentor_id'),
        Index('ix_mentor_interactions_created', 'created_at'),
    )