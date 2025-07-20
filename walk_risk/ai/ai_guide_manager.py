"""
AI Guide Manager - Integrates AI guidance with game systems
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .ai_guide_engine import AIGuideEngine, GuidanceRequest, GuidanceResponse, GuideContext, GuidanceType
from .mentor_personas import MentorLibrary
from ..models.player.base import Player
from ..models.risk.base import Risk
from ..models.portfolio.assets import Asset
from ..utils.logger import logger


@dataclass
class AIGuideConfig:
    """Configuration for AI guide system"""
    proactive_guidance: bool = True
    guidance_frequency: int = 300  # seconds between proactive guidance
    max_daily_guidance: int = 20
    educational_mode: bool = True
    context_awareness: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'proactive_guidance': self.proactive_guidance,
            'guidance_frequency': self.guidance_frequency,
            'max_daily_guidance': self.max_daily_guidance,
            'educational_mode': self.educational_mode,
            'context_awareness': self.context_awareness
        }


class AIGuideManager:
    """Manager for AI guide system integration with game"""
    
    def __init__(self, config: AIGuideConfig = None):
        self.config = config or AIGuideConfig()
        self.guide_engine = AIGuideEngine()
        self.mentor_library = MentorLibrary()
        
        # Active guidance tracking
        self.active_players: Dict[str, Player] = {}
        self.guidance_counters: Dict[str, int] = {}  # Daily guidance count per player
        self.last_guidance_time: Dict[str, datetime] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._is_running = False
        
        # Analytics
        self.analytics = {
            'total_guidance_requests': 0,
            'proactive_guidance_sent': 0,
            'player_interactions': 0,
            'mentor_feedback_received': 0
        }
    
    async def start(self) -> None:
        """Start the AI guide manager"""
        self._is_running = True
        
        # Start background tasks
        if self.config.proactive_guidance:
            self._background_tasks.append(
                asyncio.create_task(self._proactive_guidance_task())
            )
        
        self._background_tasks.append(
            asyncio.create_task(self._daily_reset_task())
        )
        
        logger.info("AI 가이드 매니저 시작됨")
    
    async def stop(self) -> None:
        """Stop the AI guide manager"""
        self._is_running = False
        
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
        logger.info("AI 가이드 매니저 중지됨")
    
    async def _proactive_guidance_task(self) -> None:
        """Background task for proactive guidance"""
        while self._is_running:
            try:
                await self._check_and_send_proactive_guidance()
                await asyncio.sleep(self.config.guidance_frequency)
            except Exception as e:
                logger.error(f"Proactive guidance task error: {e}")
                await asyncio.sleep(60)
    
    async def _daily_reset_task(self) -> None:
        """Reset daily counters at midnight"""
        while self._is_running:
            try:
                # Sleep until next midnight
                now = datetime.now()
                tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                sleep_seconds = (tomorrow - now).total_seconds()
                
                await asyncio.sleep(sleep_seconds)
                
                # Reset daily counters
                self.guidance_counters.clear()
                logger.info("일일 가이드 카운터 리셋")
                
            except Exception as e:
                logger.error(f"Daily reset task error: {e}")
                await asyncio.sleep(3600)  # Sleep for 1 hour on error
    
    async def _check_and_send_proactive_guidance(self) -> None:
        """Check if proactive guidance should be sent to players"""
        current_time = datetime.now()
        
        for player_id, player in self.active_players.items():
            try:
                # Check if player needs guidance
                if await self._should_send_proactive_guidance(player, current_time):
                    guidance_request = await self._create_proactive_guidance_request(player)
                    
                    if guidance_request:
                        response = await self.guide_engine.provide_guidance(guidance_request)
                        await self._send_proactive_guidance(player, response)
                        
                        # Update tracking
                        self.last_guidance_time[player_id] = current_time
                        self.guidance_counters[player_id] = self.guidance_counters.get(player_id, 0) + 1
                        self.analytics['proactive_guidance_sent'] += 1
                        
            except Exception as e:
                logger.error(f"Proactive guidance error for player {player_id}: {e}")
    
    async def _should_send_proactive_guidance(self, player: Player, current_time: datetime) -> bool:
        """Check if proactive guidance should be sent to player"""
        
        # Check daily limit
        daily_count = self.guidance_counters.get(player.id, 0)
        if daily_count >= self.config.max_daily_guidance:
            return False
        
        # Check time since last guidance
        last_guidance = self.last_guidance_time.get(player.id)
        if last_guidance:
            time_diff = (current_time - last_guidance).total_seconds()
            if time_diff < self.config.guidance_frequency:
                return False
        
        # Check player activity
        if player.last_active:
            inactive_time = (current_time - player.last_active).total_seconds()
            if inactive_time > 3600:  # Don't send if inactive for more than 1 hour
                return False
        
        return True
    
    async def _create_proactive_guidance_request(self, player: Player) -> Optional[GuidanceRequest]:
        """Create proactive guidance request based on player state"""
        
        # Analyze player's current situation
        context = await self._analyze_player_context(player)
        
        if context:
            return GuidanceRequest(
                player_id=player.id,
                context=context['context'],
                guidance_type=GuidanceType.ADVICE,
                data=context['data']
            )
        
        return None
    
    async def _analyze_player_context(self, player: Player) -> Optional[Dict[str, Any]]:
        """Analyze player's current context for proactive guidance"""
        
        # Check if player has been inactive on risks
        if not player.completed_risks:
            return {
                'context': GuideContext.EDUCATIONAL,
                'data': {
                    'player_level': player.stats.level,
                    'topic': 'getting_started'
                }
            }
        
        # Check if player has low success rate
        total_predictions = player.stats.successful_predictions + player.stats.failed_predictions
        if total_predictions > 5:
            success_rate = player.stats.successful_predictions / total_predictions
            if success_rate < 0.6:
                return {
                    'context': GuideContext.EDUCATIONAL,
                    'data': {
                        'success_rate': success_rate,
                        'topic': 'improvement_tips'
                    }
                }
        
        # Check if player needs portfolio review
        if player.stats.level > 10 and not self._has_recent_portfolio_review(player):
            return {
                'context': GuideContext.PORTFOLIO_REVIEW,
                'data': {
                    'player_level': player.stats.level,
                    'last_review': 'never'
                }
            }
        
        return None
    
    def _has_recent_portfolio_review(self, player: Player) -> bool:
        """Check if player has recent portfolio review guidance"""
        # In a full implementation, this would check guidance history
        # For now, assume no recent review
        return False
    
    async def _send_proactive_guidance(self, player: Player, response: GuidanceResponse) -> None:
        """Send proactive guidance to player"""
        
        # Emit event for UI to display guidance
        await self._emit_event('proactive_guidance', {
            'player_id': player.id,
            'guidance': response.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"Proactive guidance sent to {player.username}: {response.mentor_name}")
    
    # Public API methods
    
    async def request_guidance(
        self,
        player_id: str,
        context: GuideContext,
        guidance_type: GuidanceType = GuidanceType.ADVICE,
        data: Dict[str, Any] = None,
        preferred_mentor: str = None
    ) -> GuidanceResponse:
        """Request guidance for player"""
        
        try:
            # Check daily limit
            daily_count = self.guidance_counters.get(player_id, 0)
            if daily_count >= self.config.max_daily_guidance:
                logger.warning(f"Daily guidance limit reached for player {player_id}")
                return self._create_limit_exceeded_response()
            
            # Create guidance request
            request = GuidanceRequest(
                player_id=player_id,
                context=context,
                guidance_type=guidance_type,
                data=data or {},
                preferred_mentor=preferred_mentor
            )
            
            # Get guidance
            response = await self.guide_engine.provide_guidance(request)
            
            # Update tracking
            self.guidance_counters[player_id] = daily_count + 1
            self.analytics['total_guidance_requests'] += 1
            
            # Emit event
            await self._emit_event('guidance_provided', {
                'player_id': player_id,
                'context': context.value,
                'guidance_type': guidance_type.value,
                'mentor': response.mentor_name,
                'confidence': response.confidence
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Guidance request failed for player {player_id}: {e}")
            return self._create_error_response()
    
    async def request_challenge_hint(
        self,
        player_id: str,
        challenge_id: str,
        challenge_data: Dict[str, Any] = None
    ) -> GuidanceResponse:
        """Request hint for unlock challenge"""
        
        return await self.request_guidance(
            player_id=player_id,
            context=GuideContext.UNLOCK_CHALLENGE,
            guidance_type=GuidanceType.CHALLENGE_HINT,
            data={
                'challenge_id': challenge_id,
                'challenge_data': challenge_data or {}
            }
        )
    
    async def request_market_analysis(
        self,
        player_id: str,
        market_data: Dict[str, Any]
    ) -> GuidanceResponse:
        """Request market event analysis"""
        
        return await self.request_guidance(
            player_id=player_id,
            context=GuideContext.MARKET_EVENT,
            guidance_type=GuidanceType.ADVICE,
            data={
                'market_data': market_data,
                'event_type': market_data.get('event_type', 'normal')
            }
        )
    
    async def request_portfolio_review(
        self,
        player_id: str,
        portfolio_data: Dict[str, Any]
    ) -> GuidanceResponse:
        """Request portfolio review"""
        
        return await self.request_guidance(
            player_id=player_id,
            context=GuideContext.PORTFOLIO_REVIEW,
            guidance_type=GuidanceType.ADVICE,
            data={
                'portfolio_data': portfolio_data,
                'health_score': portfolio_data.get('health_score', 0.7)
            }
        )
    
    async def request_risk_guidance(
        self,
        player_id: str,
        risk: Risk,
        analysis_data: Dict[str, Any] = None
    ) -> GuidanceResponse:
        """Request risk analysis guidance"""
        
        return await self.request_guidance(
            player_id=player_id,
            context=GuideContext.RISK_ANALYSIS,
            guidance_type=GuidanceType.ADVICE,
            data={
                'risk_id': risk.id,
                'risk_name': risk.name,
                'risk_level': risk.level.value,
                'risk_severity': risk.severity,
                'analysis_data': analysis_data or {}
            }
        )
    
    def register_player(self, player: Player) -> None:
        """Register player for AI guidance"""
        self.active_players[player.id] = player
        
        if player.id not in self.guidance_counters:
            self.guidance_counters[player.id] = 0
        
        logger.info(f"Player registered for AI guidance: {player.username}")
    
    def unregister_player(self, player_id: str) -> None:
        """Unregister player from AI guidance"""
        if player_id in self.active_players:
            del self.active_players[player_id]
            logger.info(f"Player unregistered from AI guidance: {player_id}")
    
    def update_player(self, player: Player) -> None:
        """Update player data for AI guidance"""
        self.active_players[player.id] = player
    
    def get_mentor_recommendations(self, player_id: str) -> List[Dict[str, Any]]:
        """Get mentor recommendations for player"""
        return self.guide_engine.get_mentor_recommendations(player_id)
    
    def get_guidance_history(self, player_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get player's guidance history"""
        return self.guide_engine.get_guidance_history(player_id, limit)
    
    async def submit_mentor_feedback(
        self,
        player_id: str,
        guidance_id: str,
        feedback: str,
        rating: int
    ) -> bool:
        """Submit feedback on mentor guidance"""
        
        try:
            # Store feedback (in a real implementation, this would be stored in database)
            feedback_data = {
                'player_id': player_id,
                'guidance_id': guidance_id,
                'feedback': feedback,
                'rating': rating,
                'timestamp': datetime.now().isoformat()
            }
            
            # Emit event for analytics
            await self._emit_event('mentor_feedback', feedback_data)
            
            # Update analytics
            self.analytics['mentor_feedback_received'] += 1
            
            logger.info(f"Mentor feedback received from {player_id}: {rating}/5")
            return True
            
        except Exception as e:
            logger.error(f"Failed to submit mentor feedback: {e}")
            return False
    
    def update_mentor_preference(self, player_id: str, mentor_id: str, preference: str) -> bool:
        """Update player's mentor preference"""
        return self.guide_engine.update_mentor_preference(player_id, mentor_id, preference)
    
    # Event system
    
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
                    logger.error(f"Event handler error ({event_type}): {e}")
    
    # Analytics and monitoring
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get AI guide analytics"""
        
        # Get engine stats
        engine_stats = self.guide_engine.get_mentor_stats()
        
        return {
            'manager_stats': self.analytics.copy(),
            'engine_stats': engine_stats,
            'active_players': len(self.active_players),
            'daily_guidance_usage': sum(self.guidance_counters.values()),
            'config': self.config.to_dict()
        }
    
    def get_player_guidance_stats(self, player_id: str) -> Dict[str, Any]:
        """Get guidance statistics for specific player"""
        
        daily_count = self.guidance_counters.get(player_id, 0)
        history = self.guide_engine.get_guidance_history(player_id, 50)
        
        return {
            'daily_guidance_count': daily_count,
            'daily_limit': self.config.max_daily_guidance,
            'remaining_guidance': max(0, self.config.max_daily_guidance - daily_count),
            'total_guidance_received': len(history),
            'last_guidance_time': self.last_guidance_time.get(player_id),
            'guidance_history': history[-5:]  # Last 5 guidance
        }
    
    # Helper methods
    
    def _create_limit_exceeded_response(self) -> GuidanceResponse:
        """Create response for when daily limit is exceeded"""
        return GuidanceResponse(
            mentor_id="system",
            mentor_name="AI 가이드",
            message="오늘의 가이드 한도를 초과했습니다. 내일 다시 시도해주세요. 그동안 기존 조언들을 복습해보시는 것도 좋습니다.",
            confidence=0.8,
            follow_up_questions=["이전 조언들을 다시 확인해보시겠어요?"]
        )
    
    def _create_error_response(self) -> GuidanceResponse:
        """Create response for when guidance generation fails"""
        return GuidanceResponse(
            mentor_id="system",
            mentor_name="AI 가이드",
            message="죄송합니다. 현재 가이드를 제공할 수 없습니다. 잠시 후 다시 시도해주세요.",
            confidence=0.3,
            follow_up_questions=["도움이 필요하시면 언제든지 말씀해주세요."]
        )
    
    # Configuration methods
    
    def update_config(self, config: AIGuideConfig) -> None:
        """Update AI guide configuration"""
        self.config = config
        logger.info("AI 가이드 설정 업데이트됨")
    
    def enable_proactive_guidance(self, enable: bool) -> None:
        """Enable/disable proactive guidance"""
        self.config.proactive_guidance = enable
        
        if enable and not any(task for task in self._background_tasks if not task.done()):
            # Start proactive guidance task if not already running
            if self._is_running:
                self._background_tasks.append(
                    asyncio.create_task(self._proactive_guidance_task())
                )
        
        logger.info(f"Proactive guidance {'enabled' if enable else 'disabled'}")
    
    def set_daily_limit(self, limit: int) -> None:
        """Set daily guidance limit"""
        self.config.max_daily_guidance = limit
        logger.info(f"Daily guidance limit set to {limit}")