"""Game state manager for XBoing.

This module manages game state transitions including lives, level completion,
and bonus timer management. It centralizes state logic that was previously
scattered across GameController.
"""

import logging
from typing import List

from xboing.engine.events import (
    ApplauseEvent,
    LevelCompleteEvent,
    TimerUpdatedEvent,
)
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager


class GameStateManager:
    """Manages game state transitions: lives, levels, game over, timers.

    This manager is responsible for:
    - Life loss detection and handling
    - Level completion detection
    - Bonus timer management
    - Game over state coordination

    It separates state management concerns from GameController,
    making the code more maintainable and testable.
    """

    def __init__(self, game_state: GameState, level_manager: LevelManager) -> None:
        """Initialize the game state manager.

        Args:
            game_state: The game state instance to manage.
            level_manager: The level manager for level-related operations.

        """
        self.game_state = game_state
        self.level_manager = level_manager
        self.logger = logging.getLogger("xboing.GameStateManager")

    def handle_life_loss(self, has_active_balls: bool) -> List[object]:
        """Handle life loss logic and return events to post.

        This method determines if a life should be lost based on whether
        there are active balls remaining. It does NOT create balls or
        manage sticky state - those are separate concerns.

        Args:
            has_active_balls: Whether there are active balls still in play.

        Returns:
            List of events to post (LifeLostEvent, GameOverEvent, etc.).

        """
        events: List[object] = []

        self.logger.debug(
            f"handle_life_loss called. Lives: {self.game_state.lives}, "
            f"Active balls: {has_active_balls}"
        )

        # Check if game is already over
        if self.game_state.is_game_over():
            self.logger.debug("Game is already over, ignoring life loss.")
            return events

        # Only lose a life if there are no active balls in play
        if not has_active_balls:
            # Lose a life through game_state
            life_events = self.game_state.lose_life()
            events.extend(life_events)
            self.logger.debug(f"Life lost. Remaining lives: {self.game_state.lives}")

            # Check if game is now over
            if self.game_state.is_game_over():
                self.logger.debug("Game over after life loss.")
                # game_state.lose_life() should have added GameOverEvent
        else:
            self.logger.debug(
                "Ball lost but other balls still in play, not losing a life."
            )

        return events

    def check_level_complete(self, blocks_remaining: int) -> List[object]:
        """Check if level is complete based on block count.

        Args:
            blocks_remaining: Number of blocks remaining in the level.

        Returns:
            List of events to post (LevelCompleteEvent, ApplauseEvent) if complete.

        """
        events: List[object] = []

        # Check if level is already marked complete to avoid duplicate events
        if self.game_state.level_state.is_level_complete():
            return events

        # Level is complete when no blocks remain
        if blocks_remaining == 0:
            self.logger.debug("Level complete! No blocks remaining.")
            self.game_state.level_state.set_level_complete()
            events.append(LevelCompleteEvent())
            events.append(ApplauseEvent())

        return events

    def update_timer(self, delta_ms: float, is_active: bool) -> List[object]:
        """Update bonus timer if game is active.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
            is_active: Whether the game is active (not game over, not level complete).

        Returns:
            List of events to post (TimerUpdatedEvent with current time).

        """
        events: List[object] = []

        if is_active:
            # Decrement bonus time
            self.game_state.level_state.decrement_bonus_time(delta_ms)
            time_remaining = self.game_state.level_state.get_bonus_time()
            events.append(TimerUpdatedEvent(time_remaining))

        return events

    def is_game_over(self) -> bool:
        """Check if game is over.

        Returns:
            True if game is over, False otherwise.

        """
        return self.game_state.is_game_over()

    def reset_level(self) -> None:
        """Reset state for new level.

        This is called when starting a new level to reset timer and
        other level-specific state.
        """
        # Timer is reset through level_state when new level is loaded
        # No additional reset needed here currently
        self.logger.debug("Level state reset.")
