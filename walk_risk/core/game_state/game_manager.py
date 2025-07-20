"""
Central game state management system
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from ...models.player.base import Player, PlayerClass, PlayerStats, SkillPath
from ...models.risk.base import Risk, RiskLevel, RiskKey
from ...core.risk_engine.risk_factory import RiskFactory
from ...data.sources.data_manager import DataManager, DataSourceConfig, DataSourcePriority
from ...models.portfolio.portfolio_manager import PortfolioManager
from ...core.unlock_system.unlock_manager import UnlockManager
from ...ai.ai_guide_manager import AIGuideManager, AIGuideConfig
from ...utils.logger import logger


class GameState(Enum):
    """Game states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    SHUTDOWN = "shutdown"


class GameMode(Enum):
    """Game modes"""
    TUTORIAL = "tutorial"
    PRACTICE = "practice"
    REAL_TIME = "real_time"
    SIMULATION = "simulation"
    CHALLENGE = "challenge"


@dataclass
class GameSession:
    """Individual game session data"""
    id: str
    player_id: str
    mode: GameMode
    start_time: datetime
    end_time: Optional[datetime] = None
    risks_encountered: List[str] = field(default_factory=list)
    risks_unlocked: List[str] = field(default_factory=list)
    experience_gained: int = 0
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> timedelta:
        """Get session duration"""
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'player_id': self.player_id,
            'mode': self.mode.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'risks_encountered': self.risks_encountered,
            'risks_unlocked': self.risks_unlocked,
            'experience_gained': self.experience_gained,
            'duration_seconds': self.duration().total_seconds(),
            'session_data': self.session_data
        }


@dataclass
class GameConfig:
    """Game configuration"""
    auto_save_interval: int = 300  # seconds
    max_concurrent_risks: int = 5
    experience_multiplier: float = 1.0
    difficulty_scaling: float = 1.2
    tutorial_enabled: bool = True
    real_time_mode: bool = False
    data_sources: List[str] = field(default_factory=lambda: ["demo"])
    ai_guide_enabled: bool = True
    ai_guide_config: AIGuideConfig = field(default_factory=AIGuideConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'auto_save_interval': self.auto_save_interval,
            'max_concurrent_risks': self.max_concurrent_risks,
            'experience_multiplier': self.experience_multiplier,
            'difficulty_scaling': self.difficulty_scaling,
            'tutorial_enabled': self.tutorial_enabled,
            'real_time_mode': self.real_time_mode,
            'data_sources': self.data_sources,
            'ai_guide_enabled': self.ai_guide_enabled,
            'ai_guide_config': self.ai_guide_config.to_dict()
        }


class GameManager:
    """Central game state manager"""
    
    def __init__(self, config: GameConfig = None):
        self.config = config or GameConfig()
        self.state = GameState.INITIALIZING
        self.current_mode = GameMode.PRACTICE
        
        # Core components
        self.data_manager = DataManager()
        self.risk_factory = RiskFactory()
        self.portfolio_manager = PortfolioManager(self.data_manager)
        self.unlock_manager = UnlockManager(self.data_manager)
        self.ai_guide_manager = AIGuideManager(self.config.ai_guide_config) if self.config.ai_guide_enabled else None
        
        # Game state
        self.players: Dict[str, Player] = {}
        self.active_sessions: Dict[str, GameSession] = {}
        self.global_risks: Dict[str, Risk] = {}
        
        # Event system
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._is_running = False
        
        # Save system
        self.save_directory = Path("saves")
        self.save_directory.mkdir(exist_ok=True)
        
        # Metrics
        self.metrics = {
            'total_players': 0,
            'total_sessions': 0,
            'total_risks_created': 0,
            'total_risks_unlocked': 0,
            'uptime_start': datetime.now()
        }
    
    async def initialize(self) -> bool:
        """Initialize game manager"""
        try:
            logger.info("게임 매니저 초기화 시작")
            
            # Initialize data sources
            await self._initialize_data_sources()
            
            # Load saved data
            await self._load_game_data()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.state = GameState.RUNNING
            logger.info("게임 매니저 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"게임 매니저 초기화 실패: {e}")
            self.state = GameState.SHUTDOWN
            return False
    
    async def _initialize_data_sources(self) -> None:
        """Initialize market data sources"""
        for source_name in self.config.data_sources:
            if source_name == "demo":
                config = DataSourceConfig(
                    name="demo_source",
                    symbols=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'SPY']
                )
                await self.data_manager.add_source(
                    "demo", 
                    config, 
                    DataSourcePriority.PRIMARY
                )
            
            elif source_name == "yahoo":
                config = DataSourceConfig(
                    name="yahoo_finance",
                    api_key="",  # No API key needed for Yahoo Finance
                    symbols=['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'SPY']
                )
                await self.data_manager.add_source(
                    "yahoo", 
                    config, 
                    DataSourcePriority.SECONDARY
                )
        
        # Start data manager background tasks
        await self.data_manager.start_background_tasks()
        
        # Start portfolio manager
        await self.portfolio_manager.start()
        
        # Start unlock manager
        await self.unlock_manager.start()
        
        # Start AI guide manager
        if self.ai_guide_manager:
            await self.ai_guide_manager.start()
    
    async def _load_game_data(self) -> None:
        """Load saved game data"""
        try:
            # Load players
            players_file = self.save_directory / "players.json"
            if players_file.exists():
                with open(players_file, 'r', encoding='utf-8') as f:
                    players_data = json.load(f)
                    for player_data in players_data:
                        player = Player(**player_data)
                        self.players[player.id] = player
                        self.metrics['total_players'] += 1
            
            # Load game metrics
            metrics_file = self.save_directory / "metrics.json"
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    saved_metrics = json.load(f)
                    self.metrics.update(saved_metrics)
            
            logger.info(f"게임 데이터 로드 완료: {len(self.players)}명의 플레이어")
            
        except Exception as e:
            logger.error(f"게임 데이터 로드 실패: {e}")
    
    async def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        if self._is_running:
            return
        
        self._is_running = True
        
        # Auto-save task
        async def auto_save_task():
            while self._is_running:
                await asyncio.sleep(self.config.auto_save_interval)
                await self._save_game_data()
        
        # Risk generation task
        async def risk_generation_task():
            while self._is_running:
                await self._generate_global_risks()
                await asyncio.sleep(60)  # Generate risks every minute
        
        # Session cleanup task
        async def session_cleanup_task():
            while self._is_running:
                await self._cleanup_old_sessions()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
        
        self._background_tasks = [
            asyncio.create_task(auto_save_task()),
            asyncio.create_task(risk_generation_task()),
            asyncio.create_task(session_cleanup_task())
        ]
    
    async def _save_game_data(self) -> None:
        """Save game data to disk"""
        try:
            # Save players
            players_data = [
                {
                    'id': player.id,
                    'username': player.username,
                    'email': player.email,
                    'player_class': player.player_class.value,
                    'stats': {
                        'level': player.stats.level,
                        'experience': player.stats.experience,
                        'total_risks_unlocked': player.stats.total_risks_unlocked,
                        'total_risks_mastered': player.stats.total_risks_mastered,
                        'successful_predictions': player.stats.successful_predictions,
                        'failed_predictions': player.stats.failed_predictions
                    },
                    'unlocked_skills': player.unlocked_skills,
                    'active_skill_path': player.active_skill_path.value if player.active_skill_path else None,
                    'owned_keys': [key.__dict__ for key in player.owned_keys],
                    'completed_risks': player.completed_risks,
                    'achievements': player.achievements,
                    'badges': player.badges,
                    'created_at': player.created_at.isoformat(),
                    'last_active': player.last_active.isoformat()
                }
                for player in self.players.values()
            ]
            
            players_file = self.save_directory / "players.json"
            with open(players_file, 'w', encoding='utf-8') as f:
                json.dump(players_data, f, ensure_ascii=False, indent=2)
            
            # Save metrics
            metrics_file = self.save_directory / "metrics.json"
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            
            logger.debug("게임 데이터 자동 저장 완료")
            
        except Exception as e:
            logger.error(f"게임 데이터 저장 실패: {e}")
    
    async def _generate_global_risks(self) -> None:
        """Generate global market risks"""
        try:
            # Get market indices data
            indices_data = await self.data_manager.get_market_indices()
            
            for name, market_data in indices_data.items():
                # Create market risk
                risk = await self.risk_factory.create_risk_from_market_data(
                    symbol=market_data.symbol,
                    market_data=market_data
                )
                
                if risk:
                    self.global_risks[risk.id] = risk
                    self.metrics['total_risks_created'] += 1
                    
                    # Emit risk created event
                    await self._emit_event('risk_created', {
                        'risk_id': risk.id,
                        'risk_name': risk.name,
                        'severity': risk.severity
                    })
            
            # Cleanup old global risks
            current_time = datetime.now()
            old_risk_ids = [
                risk_id for risk_id, risk in self.global_risks.items()
                if (current_time - risk.created_at).total_seconds() > 3600  # 1 hour old
            ]
            
            for risk_id in old_risk_ids:
                del self.global_risks[risk_id]
            
        except Exception as e:
            logger.error(f"글로벌 리스크 생성 실패: {e}")
    
    async def _cleanup_old_sessions(self) -> None:
        """Clean up old inactive sessions"""
        current_time = datetime.now()
        old_session_ids = []
        
        for session_id, session in self.active_sessions.items():
            # Mark sessions older than 24 hours as old
            if (current_time - session.start_time).total_seconds() > 86400:
                old_session_ids.append(session_id)
        
        for session_id in old_session_ids:
            session = self.active_sessions.pop(session_id)
            session.end_time = current_time
            logger.info(f"세션 정리: {session_id}")
    
    # Player Management
    async def create_player(self, username: str, email: str = "") -> Player:
        """Create new player"""
        player = Player(
            username=username,
            email=email
        )
        
        # Create portfolio for player
        portfolio = self.portfolio_manager.create_portfolio(player.id, f"{username}'s Portfolio")
        player.portfolio_id = portfolio.id
        
        self.players[player.id] = player
        self.metrics['total_players'] += 1
        
        # Register player with AI guide manager
        if self.ai_guide_manager:
            self.ai_guide_manager.register_player(player)
        
        # Emit player created event
        await self._emit_event('player_created', {
            'player_id': player.id,
            'username': username,
            'portfolio_id': portfolio.id
        })
        
        logger.info(f"새 플레이어 생성: {username} ({player.id}) with portfolio {portfolio.id}")
        return player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        return self.players.get(player_id)
    
    def get_player_by_username(self, username: str) -> Optional[Player]:
        """Get player by username"""
        for player in self.players.values():
            if player.username == username:
                return player
        return None
    
    async def update_player(self, player_id: str, **updates) -> bool:
        """Update player data"""
        player = self.players.get(player_id)
        if not player:
            return False
        
        for key, value in updates.items():
            if hasattr(player, key):
                setattr(player, key, value)
        
        player.last_active = datetime.now()
        
        # Update player in AI guide manager
        if self.ai_guide_manager:
            self.ai_guide_manager.update_player(player)
        
        return True
    
    # Session Management
    async def start_session(self, player_id: str, mode: GameMode = GameMode.PRACTICE) -> Optional[GameSession]:
        """Start new game session"""
        player = self.players.get(player_id)
        if not player:
            logger.warning(f"플레이어를 찾을 수 없음: {player_id}")
            return None
        
        session = GameSession(
            id=f"session_{player_id}_{int(datetime.now().timestamp())}",
            player_id=player_id,
            mode=mode,
            start_time=datetime.now()
        )
        
        self.active_sessions[session.id] = session
        self.metrics['total_sessions'] += 1
        
        # Update player activity
        player.last_active = datetime.now()
        
        # Emit session started event
        await self._emit_event('session_started', {
            'session_id': session.id,
            'player_id': player_id,
            'mode': mode.value
        })
        
        logger.info(f"세션 시작: {session.id} ({mode.value})")
        return session
    
    async def end_session(self, session_id: str) -> bool:
        """End game session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.end_time = datetime.now()
        
        # Update player stats
        player = self.players.get(session.player_id)
        if player:
            player.add_experience(session.experience_gained)
            player.stats.total_play_time += int(session.duration().total_seconds())
        
        # Emit session ended event
        await self._emit_event('session_ended', {
            'session_id': session_id,
            'duration': session.duration().total_seconds(),
            'experience_gained': session.experience_gained
        })
        
        logger.info(f"세션 종료: {session_id}")
        return True
    
    def get_active_session(self, player_id: str) -> Optional[GameSession]:
        """Get active session for player"""
        for session in self.active_sessions.values():
            if session.player_id == player_id and session.end_time is None:
                return session
        return None
    
    # Risk Management
    def get_available_risks(self, player_id: str) -> List[Risk]:
        """Get risks available to player"""
        player = self.players.get(player_id)
        if not player:
            return []
        
        # Combine global risks and player-specific risks
        available_risks = list(self.global_risks.values())
        
        # Filter based on player level and unlocked skills
        filtered_risks = []
        for risk in available_risks:
            if self._is_risk_available_to_player(risk, player):
                filtered_risks.append(risk)
        
        return sorted(filtered_risks, key=lambda r: r.severity, reverse=True)
    
    def _is_risk_available_to_player(self, risk: Risk, player: Player) -> bool:
        """Check if risk is available to player"""
        # Basic level requirement
        if player.stats.level < 1:
            return False
        
        # Check if already completed
        if risk.id in player.completed_risks:
            return False
        
        # Check complexity vs player level
        required_level = int(risk.complexity * 100)
        if player.stats.level < required_level:
            return False
        
        return True
    
    async def unlock_risk(self, player_id: str, risk_id: str, keys_used: List[str]) -> bool:
        """Attempt to unlock a risk"""
        player = self.players.get(player_id)
        if not player:
            return False
        
        risk = self.global_risks.get(risk_id)
        if not risk:
            return False
        
        # Check if player has required keys
        player_key_names = [key.name for key in player.owned_keys]
        if not all(key_name in player_key_names for key_name in keys_used):
            return False
        
        # Attempt unlock
        if len(keys_used) >= risk.minimum_keys:
            risk.update_level(RiskLevel.UNLOCKED)
            player.complete_risk(risk_id, RiskLevel.UNLOCKED)
            
            # Award experience
            experience = int(risk.severity * 100 * self.config.experience_multiplier)
            player.add_experience(experience)
            
            # Update session
            session = self.get_active_session(player_id)
            if session:
                session.risks_unlocked.append(risk_id)
                session.experience_gained += experience
            
            self.metrics['total_risks_unlocked'] += 1
            
            # Emit risk unlocked event
            await self._emit_event('risk_unlocked', {
                'player_id': player_id,
                'risk_id': risk_id,
                'experience_gained': experience
            })
            
            logger.info(f"리스크 언락: {risk.name} by {player.username}")
            return True
        
        return False
    
    # Event System
    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """Add event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emit event to all handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"이벤트 핸들러 오류 ({event_type}): {e}")
    
    # State Management
    def set_game_mode(self, mode: GameMode) -> None:
        """Set current game mode"""
        self.current_mode = mode
        logger.info(f"게임 모드 변경: {mode.value}")
    
    def pause_game(self) -> None:
        """Pause game"""
        self.state = GameState.PAUSED
        logger.info("게임 일시정지")
    
    def resume_game(self) -> None:
        """Resume game"""
        self.state = GameState.RUNNING
        logger.info("게임 재개")
    
    # Statistics and Monitoring
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get comprehensive game statistics"""
        current_time = datetime.now()
        uptime = current_time - self.metrics['uptime_start']
        
        # Player statistics
        active_players = len([
            p for p in self.players.values()
            if (current_time - p.last_active).total_seconds() < 86400  # Active in last 24h
        ])
        
        player_levels = [p.stats.level for p in self.players.values()]
        avg_level = sum(player_levels) / len(player_levels) if player_levels else 0
        
        # Session statistics
        active_sessions = len([s for s in self.active_sessions.values() if s.end_time is None])
        
        # Risk statistics
        risk_stats = self.risk_factory.get_risk_statistics()
        
        return {
            'system': {
                'state': self.state.value,
                'mode': self.current_mode.value,
                'uptime_seconds': uptime.total_seconds(),
                'uptime_formatted': str(uptime)
            },
            'players': {
                'total': self.metrics['total_players'],
                'active_24h': active_players,
                'average_level': avg_level,
                'max_level': max(player_levels) if player_levels else 0
            },
            'sessions': {
                'total': self.metrics['total_sessions'],
                'active': active_sessions
            },
            'risks': {
                'total_created': self.metrics['total_risks_created'],
                'total_unlocked': self.metrics['total_risks_unlocked'],
                'active': risk_stats.get('total_risks', 0),
                'by_category': risk_stats.get('by_category', {}),
                'average_severity': risk_stats.get('avg_severity', 0.0)
            },
            'data_sources': self.data_manager.get_source_stats()
        }
    
    # Shutdown
    async def shutdown(self) -> None:
        """Shutdown game manager"""
        logger.info("게임 매니저 종료 시작")
        
        self.state = GameState.SHUTDOWN
        self._is_running = False
        
        # Stop background tasks
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # End all active sessions
        for session_id in list(self.active_sessions.keys()):
            await self.end_session(session_id)
        
        # Save game data
        await self._save_game_data()
        
        # Shutdown components
        if self.ai_guide_manager:
            await self.ai_guide_manager.stop()
        await self.unlock_manager.stop()
        await self.portfolio_manager.stop()
        await self.data_manager.shutdown()
        
        logger.info("게임 매니저 종료 완료")
    
    # AI Guide Integration Methods
    
    async def request_ai_guidance(
        self,
        player_id: str,
        context: str,
        guidance_type: str = "advice",
        data: Dict[str, Any] = None,
        preferred_mentor: str = None
    ) -> Optional[Dict[str, Any]]:
        """Request AI guidance for player"""
        if not self.ai_guide_manager:
            return None
        
        from ...ai.ai_guide_engine import GuideContext, GuidanceType
        
        # Convert string context to enum
        context_enum = getattr(GuideContext, context.upper(), GuideContext.GENERAL_ADVICE)
        guidance_type_enum = getattr(GuidanceType, guidance_type.upper(), GuidanceType.ADVICE)
        
        response = await self.ai_guide_manager.request_guidance(
            player_id=player_id,
            context=context_enum,
            guidance_type=guidance_type_enum,
            data=data,
            preferred_mentor=preferred_mentor
        )
        
        return response.to_dict() if response else None
    
    async def request_challenge_hint(self, player_id: str, challenge_id: str) -> Optional[Dict[str, Any]]:
        """Request hint for unlock challenge"""
        if not self.ai_guide_manager:
            return None
        
        response = await self.ai_guide_manager.request_challenge_hint(
            player_id=player_id,
            challenge_id=challenge_id
        )
        
        return response.to_dict() if response else None
    
    async def request_portfolio_guidance(self, player_id: str) -> Optional[Dict[str, Any]]:
        """Request portfolio review guidance"""
        if not self.ai_guide_manager:
            return None
        
        player = self.players.get(player_id)
        if not player:
            return None
        
        # Get portfolio data
        portfolio = self.portfolio_manager.get_portfolio(player.portfolio_id)
        if not portfolio:
            return None
        
        portfolio_data = {
            'allocation': portfolio.get_allocation(),
            'total_value': portfolio.total_value,
            'health_score': portfolio.calculate_health_score()
        }
        
        response = await self.ai_guide_manager.request_portfolio_review(
            player_id=player_id,
            portfolio_data=portfolio_data
        )
        
        return response.to_dict() if response else None
    
    async def request_risk_guidance(self, player_id: str, risk_id: str) -> Optional[Dict[str, Any]]:
        """Request risk analysis guidance"""
        if not self.ai_guide_manager:
            return None
        
        risk = self.global_risks.get(risk_id)
        if not risk:
            return None
        
        response = await self.ai_guide_manager.request_risk_guidance(
            player_id=player_id,
            risk=risk
        )
        
        return response.to_dict() if response else None
    
    def get_mentor_recommendations(self, player_id: str) -> List[Dict[str, Any]]:
        """Get mentor recommendations for player"""
        if not self.ai_guide_manager:
            return []
        
        return self.ai_guide_manager.get_mentor_recommendations(player_id)
    
    def get_guidance_history(self, player_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get player's guidance history"""
        if not self.ai_guide_manager:
            return []
        
        return self.ai_guide_manager.get_guidance_history(player_id, limit)
    
    async def submit_mentor_feedback(
        self,
        player_id: str,
        guidance_id: str,
        feedback: str,
        rating: int
    ) -> bool:
        """Submit feedback on mentor guidance"""
        if not self.ai_guide_manager:
            return False
        
        return await self.ai_guide_manager.submit_mentor_feedback(
            player_id=player_id,
            guidance_id=guidance_id,
            feedback=feedback,
            rating=rating
        )
    
    def update_mentor_preference(self, player_id: str, mentor_id: str, preference: str) -> bool:
        """Update player's mentor preference"""
        if not self.ai_guide_manager:
            return False
        
        return self.ai_guide_manager.update_mentor_preference(player_id, mentor_id, preference)
    
    def get_ai_guide_stats(self) -> Dict[str, Any]:
        """Get AI guide system statistics"""
        if not self.ai_guide_manager:
            return {'enabled': False}
        
        stats = self.ai_guide_manager.get_analytics()
        stats['enabled'] = True
        return stats