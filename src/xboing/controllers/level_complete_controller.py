"""Controller for handling level completion logic and transitions in XBoing."""

import logging
from typing import Any, Callable, List, Optional, cast

import pygame

from xboing.controllers.controller import Controller
from xboing.controllers.game_controller import GameController
from xboing.engine.audio_manager import AudioManager
from xboing.engine.events import TimerUpdatedEvent, post_level_title_message
from xboing.game.ball import Ball
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.layout.game_layout import GameLayout
from xboing.ui.game_view import GameView
from xboing.ui.level_complete_view import LevelCompleteView
from xboing.ui.ui_manager import UIManager


class LevelCompleteController(Controller):
    """Handles input and transitions for the LevelCompleteView.

    Handles spacebar to advance to the next level.
    Also handles LevelCompleteEvent and level advancement logic.
    """

    logger = logging.getLogger(
        "xboing.controllers.level_complete_controller.LevelCompleteController"
    )

    def __init__(
        self,
        balls: List[Ball],
        ui_manager: UIManager,
        game_view: GameView,
        layout: GameLayout,
        game_state: GameState,
        game_controller: GameController,
        level_manager: LevelManager,
        audio_manager: Optional[AudioManager] = None,
        quit_callback: Optional[Callable[[], None]] = None,
        on_advance_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the LevelCompleteController.

        Args:
        ----
            game_state: The current game state.
            level_manager: The level manager instance.
            balls: List of Ball objects in play.
            game_controller: The main game controller instance.
            ui_manager: The UIManager instance.
            game_view: The main game view instance.
            layout: The game layout instance.
            on_advance_callback: Callback to advance to the next level.
            audio_manager: The AudioManager instance.
            quit_callback: Callback to quit the game.

        """
        self.game_state = game_state
        self.level_manager = level_manager
        self.balls = balls
        self.game_controller = game_controller
        self.game_view = game_view
        self.layout = layout
        self.on_advance_callback = on_advance_callback
        self.ui_manager = ui_manager
        self.audio_manager = audio_manager
        self.quit_callback = quit_callback

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle input/events for level complete view and global controls.

        Args:
        ----
            events: List of Pygame events to process.

        """
        for event in events:
            self.logger.debug(f"[handle_events] Event received: {event}")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                LevelCompleteController.logger.debug(
                    "Spacebar pressed on LevelCompleteView. Advancing to next level."
                )
                self.advance_to_next_level()

    def advance_to_next_level(self) -> None:
        """Advance to the next level and switch to the game view/controller."""
        LevelCompleteController.logger.debug(
            "advance_to_next_level called: advancing to next level and switching to game view/controller."
        )
        # Determine the new level
        new_level = self.game_state.level + 1
        if new_level > self.level_manager.MAX_LEVELS:
            new_level = 1

        # Get the events returned by set_level and post them
        level_changed_events = self.game_state.set_level(new_level)

        # Set the correct background index for the new level
        bg_index = self.level_manager.get_current_background_index()
        self.game_view.set_background(bg_index)
        # Post the events to trigger a UI update
        self.post_game_state_events(level_changed_events)

        # Update the level title message
        level_info = self.level_manager.get_level_info()
        level_title = level_info["title"]
        post_level_title_message(level_title)

        # Set the timer for the new level
        self.level_manager.get_next_level()
        time_bonus = self.level_manager.get_level_info().get("time_bonus", 120)
        self.game_state.level_state.set_bonus_time(time_bonus)

        # Post TimerUpdatedEvent to update the UI
        self.post_game_state_events([TimerUpdatedEvent(time_bonus)])

        # Disable sticky paddle on the new level
        self.game_controller.on_new_level_loaded()

        # Set the balls
        self.balls.clear()
        self.balls.append(self.game_controller.create_new_ball())

        # Change the view
        self.ui_manager.set_view("game")

    def add_bonus_to_score(self) -> None:
        """Add bonuses to the score and post the events to trigger a UI update."""
        level_complete_view: LevelCompleteView = cast(
            LevelCompleteView, self.ui_manager.views["level_complete"]
        )
        bonus = level_complete_view.total_bonus
        score_events = self.game_state.add_score(bonus)
        self.post_game_state_events(score_events)

    def update(self, delta_ms: float) -> None:
        """Update logic for level complete view (usually minimal).

        Args:
        ----
            delta_time: Milliseconds elapsed since the last update.

        """
        # No-op for now

    @staticmethod
    def post_game_state_events(changes: List[Any]) -> None:
        """Post all events returned by GameState/model methods to the Pygame event queue.

        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
        ----
            changes: List of event objects to post to the Pygame event queue.

        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
