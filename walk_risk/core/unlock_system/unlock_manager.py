"""
Unlock system manager - Integrates unlock engine with game state
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal

from .unlock_engine import UnlockEngine, UnlockAttempt, UnlockAttemptResult, UnlockMethod
from .challenge_types import ChallengeLibrary, InteractiveChallenge, RealTimeMarketChallenge
from ...models.risk.base import Risk, RiskLevel, RiskKey
from ...models.player.base import Player
from ...data.sources.data_manager import DataManager
from ...utils.logger import logger


class UnlockManager:
    """Manages the risk unlock system integration with game state"""
    
    def __init__(self, data_manager: DataManager):
        self.unlock_engine = UnlockEngine()
        self.data_manager = data_manager
        self.challenge_library = ChallengeLibrary()
        
        # Real-time market integration
        self.market_challenges: Dict[str, RealTimeMarketChallenge] = {}
        self.market_events_queue: List[Dict[str, Any]] = []
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        self._is_running = False
        
        # Performance tracking
        self.player_performance: Dict[str, List[float]] = {}  # player_id -> scores
        
    async def start(self) -> None:
        """Start the unlock manager"""
        self._is_running = True
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._market_event_monitor()),
            asyncio.create_task(self._cleanup_expired_attempts())
        ]
        
        logger.info("Unlock manager started")
    
    async def stop(self) -> None:
        """Stop the unlock manager"""
        self._is_running = False
        
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._background_tasks.clear()
        logger.info("Unlock manager stopped")
    
    async def _market_event_monitor(self) -> None:
        """Monitor market events for real-time challenges"""
        while self._is_running:
            try:
                # Get current market data
                indices = await self.data_manager.get_market_indices()
                
                if indices:
                    # Check for significant market events
                    await self._detect_market_events(indices)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Market event monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _detect_market_events(self, market_data: Dict[str, Any]) -> None:
        """Detect significant market events"""
        try:
            # Get VIX data
            vix_data = market_data.get('VIX')
            if vix_data and vix_data.price > 30:
                event = {
                    'type': 'high_volatility',
                    'severity': min(1.0, vix_data.price / 50),
                    'timestamp': datetime.now(),
                    'data': {'vix': vix_data.price}
                }
                self.market_events_queue.append(event)
            
            # Get S&P 500 data for market movements
            spy_data = market_data.get('S&P 500')
            if spy_data and spy_data.daily_return:
                if abs(spy_data.daily_return) > 0.02:  # >2% movement
                    event = {
                        'type': 'significant_movement',
                        'severity': min(1.0, abs(spy_data.daily_return) * 10),
                        'timestamp': datetime.now(),
                        'data': {
                            'symbol': 'SPY',
                            'change': spy_data.daily_return,
                            'price': spy_data.price
                        }
                    }
                    self.market_events_queue.append(event)
            
            # Limit queue size
            if len(self.market_events_queue) > 50:
                self.market_events_queue = self.market_events_queue[-50:]
                
        except Exception as e:
            logger.error(f"Market event detection error: {e}")
    
    async def _cleanup_expired_attempts(self) -> None:
        """Clean up expired unlock attempts"""
        while self._is_running:
            try:
                current_time = datetime.now()
                expired_attempts = []
                
                for attempt_id, attempt in self.unlock_engine.active_attempts.items():
                    # Mark attempts older than 1 hour as expired
                    if (current_time - attempt.start_time).total_seconds() > 3600:
                        expired_attempts.append(attempt_id)
                
                # Complete expired attempts as failures
                for attempt_id in expired_attempts:
                    await self.unlock_engine.complete_unlock_attempt(attempt_id)
                    logger.info(f"Expired unlock attempt: {attempt_id}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(30)
    
    async def initiate_risk_unlock(
        self, 
        player: Player, 
        risk: Risk, 
        method: UnlockMethod = UnlockMethod.ANALYSIS
    ) -> Optional[UnlockAttempt]:
        """Initiate risk unlock attempt for player"""
        try:
            # Check if player already has an active attempt
            existing_attempt = self.unlock_engine.get_active_attempt(player.id)
            if existing_attempt:
                logger.warning(f"Player {player.id} already has active unlock attempt")
                return existing_attempt
            
            # Check if player meets requirements
            if not await self._check_unlock_requirements(player, risk):
                logger.warning(f"Player {player.id} doesn't meet requirements for risk {risk.id}")
                return None
            
            # Create unlock attempt
            attempt = await self.unlock_engine.initiate_unlock_attempt(player, risk, method)
            
            # Add real-time market challenges if applicable
            await self._add_market_challenges(attempt, risk)
            
            # Track attempt initiation
            await self._track_attempt_initiation(player, risk, attempt)
            
            logger.info(f"Risk unlock initiated: {risk.name} for player {player.username}")
            return attempt
            
        except Exception as e:
            logger.error(f"Failed to initiate unlock: {e}")
            return None
    
    async def _check_unlock_requirements(self, player: Player, risk: Risk) -> bool:
        """Check if player meets requirements to attempt unlock"""
        # Level requirement
        min_level = max(1, int(risk.complexity * 50))
        if player.stats.level < min_level:
            return False
        
        # Key requirements (simplified)
        required_key_types = set()
        for key in risk.required_keys:
            required_key_types.add(key.key_type)
        
        player_key_types = set(key.key_type for key in player.owned_keys)
        
        # Need at least one matching key type
        if required_key_types and not required_key_types.intersection(player_key_types):
            return False
        
        # Cooldown check (can't attempt same risk type too frequently)
        if not await self._check_cooldown(player, risk):
            return False
        
        return True
    
    async def _check_cooldown(self, player: Player, risk: Risk) -> bool:
        """Check if player is on cooldown for this risk type"""
        # Get recent attempts for this player and risk category
        recent_attempts = [
            a for a in self.unlock_engine.completed_attempts
            if (a.player_id == player.id and 
                (datetime.now() - a.start_time).total_seconds() < 3600)  # Last hour
        ]
        
        # Limit to 3 attempts per hour per player
        return len(recent_attempts) < 3
    
    async def _add_market_challenges(self, attempt: UnlockAttempt, risk: Risk) -> None:
        """Add real-time market challenges to attempt"""
        try:
            # Get current market data
            indices = await self.data_manager.get_market_indices()
            
            if indices:
                # Create real-time market challenge
                market_challenge = RealTimeMarketChallenge({
                    'vix': indices.get('VIX', {}).price if indices.get('VIX') else 20,
                    'market_change': indices.get('S&P 500', {}).daily_return if indices.get('S&P 500') else 0
                })
                
                real_time_challenge = market_challenge.generate_event_challenge()
                if real_time_challenge:
                    attempt.challenges.append(real_time_challenge)
                    
        except Exception as e:
            logger.error(f"Failed to add market challenges: {e}")
    
    async def _track_attempt_initiation(self, player: Player, risk: Risk, attempt: UnlockAttempt) -> None:
        """Track attempt initiation for analytics"""
        # Initialize player performance tracking if needed
        if player.id not in self.player_performance:
            self.player_performance[player.id] = []
        
        # Log attempt details for future analysis
        logger.info(f"Unlock attempt tracking: Player {player.username} (L{player.stats.level}) "
                   f"attempting {risk.name} (complexity: {risk.complexity:.2f})")
    
    async def submit_challenge_answer(
        self, 
        player: Player, 
        challenge_id: str, 
        answer: Any
    ) -> Dict[str, Any]:
        """Submit answer for a challenge"""
        try:
            # Get player's active attempt
            attempt = self.unlock_engine.get_active_attempt(player.id)
            if not attempt:
                return {'success': False, 'error': 'No active unlock attempt'}
            
            # Submit answer
            success = await self.unlock_engine.submit_challenge_answer(
                attempt.id, challenge_id, answer
            )
            
            if not success:
                return {'success': False, 'error': 'Failed to submit answer'}
            
            # Check if all challenges are completed
            completed_challenges = [c for c in attempt.challenges if c.completed]
            total_challenges = len(attempt.challenges)
            
            response = {
                'success': True,
                'completed_challenges': len(completed_challenges),
                'total_challenges': total_challenges,
                'progress': len(completed_challenges) / total_challenges if total_challenges > 0 else 0
            }
            
            # If all challenges completed, finish attempt
            if len(completed_challenges) == total_challenges:
                result = await self.complete_unlock_attempt(player)
                response['unlock_result'] = result
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to submit challenge answer: {e}")
            return {'success': False, 'error': str(e)}
    
    async def complete_unlock_attempt(self, player: Player) -> Dict[str, Any]:
        """Complete unlock attempt for player"""
        try:
            attempt = self.unlock_engine.get_active_attempt(player.id)
            if not attempt:
                return {'success': False, 'error': 'No active unlock attempt'}
            
            # Complete the attempt
            result = await self.unlock_engine.complete_unlock_attempt(attempt.id)
            
            # Apply results to player
            await self._apply_unlock_results(player, attempt, result)
            
            # Generate detailed report
            report = self.unlock_engine.generate_unlock_report(attempt)
            
            # Track performance
            self._track_player_performance(player.id, attempt.success_rate)
            
            return {
                'success': True,
                'result': result.value,
                'experience_gained': attempt.experience_gained,
                'new_keys': len(attempt.new_keys_earned),
                'report': report
            }
            
        except Exception as e:
            logger.error(f"Failed to complete unlock attempt: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _apply_unlock_results(
        self, 
        player: Player, 
        attempt: UnlockAttempt, 
        result: UnlockAttemptResult
    ) -> None:
        """Apply unlock results to player"""
        try:
            # Award experience
            player.add_experience(attempt.experience_gained)
            
            # Add new keys to player inventory
            for key in attempt.new_keys_earned:
                player.add_key(key)
            
            # Update player stats based on result
            if result in [UnlockAttemptResult.SUCCESS, UnlockAttemptResult.CRITICAL_SUCCESS]:
                player.stats.successful_predictions += 1
                
                # Mark risk as completed if it was a success
                if attempt.risk_id not in player.completed_risks:
                    player.complete_risk(attempt.risk_id, RiskLevel.UNLOCKED)
                
                # Bonus for critical success
                if result == UnlockAttemptResult.CRITICAL_SUCCESS:
                    player.add_experience(50)  # Bonus experience
                    
            else:
                player.stats.failed_predictions += 1
            
            # Update last active time
            player.last_active = datetime.now()
            
            logger.info(f"Applied unlock results to player {player.username}: "
                       f"{result.value}, +{attempt.experience_gained} exp")
            
        except Exception as e:
            logger.error(f"Failed to apply unlock results: {e}")
    
    def _track_player_performance(self, player_id: str, score: float) -> None:
        """Track player performance for adaptive difficulty"""
        if player_id not in self.player_performance:
            self.player_performance[player_id] = []
        
        self.player_performance[player_id].append(score)
        
        # Keep only last 20 scores
        if len(self.player_performance[player_id]) > 20:
            self.player_performance[player_id] = self.player_performance[player_id][-20:]
    
    async def get_hint_for_challenge(self, player: Player, challenge_id: str) -> Optional[str]:
        """Get hint for specific challenge"""
        attempt = self.unlock_engine.get_active_attempt(player.id)
        if not attempt:
            return None
        
        return await self.unlock_engine.provide_hint(attempt.id, challenge_id)
    
    def get_player_unlock_history(self, player: Player) -> List[Dict[str, Any]]:
        """Get unlock attempt history for player"""
        attempts = self.unlock_engine.get_attempt_history(player.id)
        
        history = []
        for attempt in attempts:
            history.append({
                'attempt_id': attempt.id,
                'risk_id': attempt.risk_id,
                'result': attempt.result.value,
                'success_rate': attempt.success_rate,
                'experience_gained': attempt.experience_gained,
                'start_time': attempt.start_time.isoformat(),
                'duration': attempt.duration.total_seconds() if attempt.duration else 0,
                'challenges_completed': len([c for c in attempt.challenges if c.completed]),
                'total_challenges': len(attempt.challenges)
            })
        
        return history
    
    def get_unlock_statistics(self) -> Dict[str, Any]:
        """Get comprehensive unlock statistics"""
        engine_stats = self.unlock_engine.get_unlock_statistics()
        
        # Add manager-specific stats
        manager_stats = {
            'market_events_detected': len(self.market_events_queue),
            'players_tracked': len(self.player_performance),
            'average_player_performance': self._calculate_average_performance(),
            'recent_market_events': self.market_events_queue[-10:] if self.market_events_queue else []
        }
        
        return {**engine_stats, **manager_stats}
    
    def _calculate_average_performance(self) -> float:
        """Calculate average player performance across all players"""
        all_scores = []
        for scores in self.player_performance.values():
            all_scores.extend(scores)
        
        return sum(all_scores) / len(all_scores) if all_scores else 0.0
    
    async def create_custom_challenge(
        self, 
        player: Player, 
        challenge_type: str, 
        parameters: Dict[str, Any]
    ) -> Optional[str]:
        """Create custom challenge for specific scenarios"""
        try:
            if challenge_type == "market_crash":
                challenge = self.challenge_library.create_market_crash_challenge(
                    parameters.get('severity', 0.8)
                )
            elif challenge_type == "volatility_spike":
                challenge = self.challenge_library.create_volatility_spike_challenge(
                    parameters.get('vix_level', 40.0)
                )
            elif challenge_type == "interest_rate":
                challenge = self.challenge_library.create_interest_rate_challenge(
                    parameters.get('rate_change', 0.02)
                )
            else:
                return None
            
            # For now, store challenge and return ID
            # In a full implementation, this would integrate with the attempt system
            challenge_id = challenge.id
            
            logger.info(f"Created custom challenge: {challenge_type} for player {player.username}")
            return challenge_id
            
        except Exception as e:
            logger.error(f"Failed to create custom challenge: {e}")
            return None
    
    async def simulate_unlock_scenario(
        self, 
        risk: Risk, 
        player_skill_level: float = 0.5
    ) -> Dict[str, Any]:
        """Simulate unlock scenario for testing/demonstration"""
        try:
            # Create mock challenges based on risk
            mock_challenges = []
            
            if risk.category.value == "market":
                mock_challenges = [
                    "volatility_analysis",
                    "correlation_detection", 
                    "scenario_analysis"
                ]
            elif risk.category.value == "liquidity":
                mock_challenges = [
                    "liquidity_calculation",
                    "market_depth_analysis"
                ]
            
            # Simulate challenge completion based on skill level
            results = []
            for challenge_type in mock_challenges:
                # Higher skill level = higher success probability
                success_prob = 0.3 + (player_skill_level * 0.6)
                success = random.random() < success_prob
                score = random.uniform(0.5, 1.0) if success else random.uniform(0.0, 0.4)
                
                results.append({
                    'challenge_type': challenge_type,
                    'success': success,
                    'score': score
                })
            
            # Calculate overall result
            avg_score = sum(r['score'] for r in results) / len(results)
            
            if avg_score >= 0.75:
                overall_result = "SUCCESS"
                exp_gained = 150
            elif avg_score >= 0.5:
                overall_result = "PARTIAL_SUCCESS" 
                exp_gained = 100
            else:
                overall_result = "FAILURE"
                exp_gained = 50
            
            return {
                'risk_name': risk.name,
                'challenge_results': results,
                'overall_result': overall_result,
                'average_score': avg_score,
                'experience_gained': exp_gained,
                'simulation': True
            }
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return {'error': str(e)}