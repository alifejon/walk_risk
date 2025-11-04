"""Auto Puzzle Manager - 실시간 시장 데이터 기반 자동 퍼즐 생성 및 관리"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import time

from ..data.market_data.market_event_detector import (
    MarketEventDetector, MarketEvent, market_event_detector
)
from ..core.risk_puzzle.puzzle_engine import PuzzleEngine, RiskPuzzle, PuzzleDifficulty
from ..core.risk_puzzle.investigation import InvestigationSystem
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class PuzzleStatus(Enum):
    """퍼즐 상태"""
    ACTIVE = "active"           # 활성 (플레이 가능)
    COMPLETED = "completed"     # 완료
    EXPIRED = "expired"         # 만료 (시간 초과)
    ARCHIVED = "archived"       # 보관 (참고용)


@dataclass
class LivePuzzle:
    """실시간 퍼즐 데이터"""
    puzzle: RiskPuzzle
    source_event: MarketEvent
    
    # 메타데이터
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: PuzzleStatus = PuzzleStatus.ACTIVE
    
    # 플레이어 상호작용
    attempts: int = 0
    completions: int = 0
    average_accuracy: float = 0.0
    
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def get_freshness_score(self) -> float:
        """신선도 점수 (0.0~1.0)"""
        if self.is_expired():
            return 0.0
        
        if not self.expires_at:
            return 1.0
        
        total_duration = (self.expires_at - self.created_at).total_seconds()
        remaining_duration = (self.expires_at - datetime.now()).total_seconds()
        
        return max(0.0, remaining_duration / total_duration)


class AutoPuzzleManager:
    """자동 퍼즐 생성 및 관리 시스템"""
    
    def __init__(self):
        self.event_detector = market_event_detector
        self.puzzle_engine = PuzzleEngine()
        
        # 활성 퍼즐들
        self.live_puzzles: Dict[str, LivePuzzle] = {}
        
        # 설정
        self.config = {
            'max_active_puzzles': 10,        # 최대 동시 활성 퍼즐 수
            'detection_interval': 300,       # 이벤트 감지 간격 (5분)
            'puzzle_lifetime': 3600 * 6,     # 퍼즐 수명 (6시간)
            'min_event_worthiness': 0.3,     # 최소 이벤트 적합도
            'auto_cleanup_interval': 1800,   # 자동 정리 간격 (30분)
        }
        
        # 백그라운드 작업
        self._running = False
        self._background_task = None
        
    async def start_auto_detection(self):
        """자동 감지 시작"""
        if self._running:
            logger.warning("자동 감지가 이미 실행 중입니다")
            return
        
        self._running = True
        self._background_task = asyncio.create_task(self._background_loop())
        logger.info("자동 퍼즐 생성 시스템 시작")
    
    async def stop_auto_detection(self):
        """자동 감지 중지"""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        logger.info("자동 퍼즐 생성 시스템 중지")
    
    async def _background_loop(self):
        """백그라운드 루프"""
        last_detection = datetime.min
        last_cleanup = datetime.min
        
        while self._running:
            try:
                current_time = datetime.now()
                
                # 이벤트 감지
                if (current_time - last_detection).total_seconds() >= self.config['detection_interval']:
                    await self._detect_and_create_puzzles()
                    last_detection = current_time
                
                # 자동 정리
                if (current_time - last_cleanup).total_seconds() >= self.config['auto_cleanup_interval']:
                    self._cleanup_expired_puzzles()
                    last_cleanup = current_time
                
                # 30초 대기
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"백그라운드 루프 오류: {e}", exc_info=True)
                await asyncio.sleep(60)  # 오류 시 1분 대기
    
    async def _detect_and_create_puzzles(self):
        """이벤트 감지 및 퍼즐 생성"""
        logger.info("실시간 시장 이벤트 감지 시작...")
        
        try:
            # 이벤트 감지
            events = await self.event_detector.detect_events()
            
            if not events:
                logger.info("감지된 이벤트가 없습니다")
                return
            
            logger.info(f"{len(events)}개 이벤트 감지됨")
            
            # 적합한 이벤트들만 필터링
            worthy_events = [
                event for event in events 
                if event.puzzle_worthiness >= self.config['min_event_worthiness']
            ]
            
            if not worthy_events:
                logger.info("퍼즐 생성에 적합한 이벤트가 없습니다")
                return
            
            logger.info(f"{len(worthy_events)}개 이벤트가 퍼즐 생성에 적합함")
            
            # 퍼즐 생성
            created_count = 0
            for event in worthy_events:
                # 활성 퍼즐 수 제한 체크
                if len(self.live_puzzles) >= self.config['max_active_puzzles']:
                    logger.info("최대 활성 퍼즐 수에 도달했습니다")
                    break
                
                # 중복 체크 (같은 종목의 활성 퍼즐이 있는지)
                if self._has_active_puzzle_for_symbol(event.symbol):
                    logger.info(f"{event.symbol} 종목의 활성 퍼즐이 이미 존재합니다")
                    continue
                
                # 퍼즐 생성
                puzzle = await self.event_detector.create_puzzle_from_event(event)
                if puzzle:
                    await self._add_live_puzzle(puzzle, event)
                    created_count += 1
                    logger.info(f"새 퍼즐 생성: {puzzle.title}")
            
            logger.info(f"총 {created_count}개 퍼즐 생성 완료")
            
        except Exception as e:
            logger.error(f"퍼즐 생성 과정 오류: {e}", exc_info=True)
    
    def _has_active_puzzle_for_symbol(self, symbol: str) -> bool:
        """특정 종목의 활성 퍼즐 존재 여부"""
        for live_puzzle in self.live_puzzles.values():
            if (live_puzzle.status == PuzzleStatus.ACTIVE and 
                live_puzzle.source_event.symbol == symbol):
                return True
        return False
    
    async def _add_live_puzzle(self, puzzle: RiskPuzzle, source_event: MarketEvent):
        """실시간 퍼즐 추가"""
        # 만료 시간 설정
        expires_at = datetime.now() + timedelta(seconds=self.config['puzzle_lifetime'])
        
        live_puzzle = LivePuzzle(
            puzzle=puzzle,
            source_event=source_event,
            expires_at=expires_at
        )
        
        self.live_puzzles[puzzle.puzzle_id] = live_puzzle
        logger.info(f"실시간 퍼즐 추가: {puzzle.puzzle_id} (만료: {expires_at.strftime('%H:%M')})")
    
    def _cleanup_expired_puzzles(self):
        """만료된 퍼즐 정리"""
        expired_ids = []
        
        for puzzle_id, live_puzzle in self.live_puzzles.items():
            if live_puzzle.is_expired():
                live_puzzle.status = PuzzleStatus.EXPIRED
                expired_ids.append(puzzle_id)
        
        # 만료된 퍼즐 제거 (또는 아카이브)
        for puzzle_id in expired_ids:
            live_puzzle = self.live_puzzles.pop(puzzle_id)
            logger.info(f"만료된 퍼즐 제거: {live_puzzle.puzzle.title}")
    
    def get_active_puzzles(self, 
                          sort_by: str = "freshness",  # freshness, difficulty, worthiness
                          limit: int = 5) -> List[LivePuzzle]:
        """활성 퍼즐 목록 반환"""
        active_puzzles = [
            lp for lp in self.live_puzzles.values() 
            if lp.status == PuzzleStatus.ACTIVE and not lp.is_expired()
        ]
        
        # 정렬
        if sort_by == "freshness":
            active_puzzles.sort(key=lambda lp: lp.get_freshness_score(), reverse=True)
        elif sort_by == "difficulty":
            difficulty_order = {
                PuzzleDifficulty.BEGINNER: 1,
                PuzzleDifficulty.INTERMEDIATE: 2,
                PuzzleDifficulty.ADVANCED: 3,
                PuzzleDifficulty.MASTER: 4
            }
            active_puzzles.sort(key=lambda lp: difficulty_order.get(lp.puzzle.difficulty, 0))
        elif sort_by == "worthiness":
            active_puzzles.sort(key=lambda lp: lp.source_event.puzzle_worthiness, reverse=True)
        
        return active_puzzles[:limit]
    
    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[LivePuzzle]:
        """ID로 퍼즐 조회"""
        return self.live_puzzles.get(puzzle_id)
    
    def record_puzzle_attempt(self, puzzle_id: str, accuracy: float = 0.0, completed: bool = False):
        """퍼즐 시도 기록"""
        live_puzzle = self.live_puzzles.get(puzzle_id)
        if not live_puzzle:
            return
        
        live_puzzle.attempts += 1
        
        if completed:
            live_puzzle.completions += 1
            # 평균 정확도 업데이트
            if live_puzzle.completions == 1:
                live_puzzle.average_accuracy = accuracy
            else:
                live_puzzle.average_accuracy = (
                    (live_puzzle.average_accuracy * (live_puzzle.completions - 1) + accuracy) /
                    live_puzzle.completions
                )
            
            # 완료된 퍼즐은 상태 변경
            live_puzzle.status = PuzzleStatus.COMPLETED
    
    def get_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        total_puzzles = len(self.live_puzzles)
        active_count = len([lp for lp in self.live_puzzles.values() if lp.status == PuzzleStatus.ACTIVE])
        completed_count = len([lp for lp in self.live_puzzles.values() if lp.status == PuzzleStatus.COMPLETED])
        expired_count = len([lp for lp in self.live_puzzles.values() if lp.status == PuzzleStatus.EXPIRED])
        
        total_attempts = sum(lp.attempts for lp in self.live_puzzles.values())
        total_completions = sum(lp.completions for lp in self.live_puzzles.values())
        
        avg_accuracy = 0.0
        if completed_count > 0:
            avg_accuracy = sum(
                lp.average_accuracy for lp in self.live_puzzles.values() 
                if lp.status == PuzzleStatus.COMPLETED
            ) / completed_count
        
        return {
            'total_puzzles': total_puzzles,
            'active_puzzles': active_count,
            'completed_puzzles': completed_count,
            'expired_puzzles': expired_count,
            'total_attempts': total_attempts,
            'total_completions': total_completions,
            'completion_rate': total_completions / total_attempts if total_attempts > 0 else 0.0,
            'average_accuracy': avg_accuracy,
            'system_running': self._running
        }
    
    async def force_detection_cycle(self) -> List[LivePuzzle]:
        """강제 감지 사이클 실행 (테스트용)"""
        logger.info("강제 이벤트 감지 실행...")
        await self._detect_and_create_puzzles()
        return self.get_active_puzzles()


# 전역 인스턴스
auto_puzzle_manager = AutoPuzzleManager()