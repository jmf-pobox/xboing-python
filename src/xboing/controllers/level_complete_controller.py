"""Controller for handling level completion logic and transitions in XBoing."""

import logging
from typing import Any, Callable, List, Optional

import pygame

from xboing.controllers.controller import Controller
from xboing.engine.audio_manager import AudioManager
from xboing.engine.events import post_level_title_message
from xboing.ui.ui_manager import UIManager

logger = logging.getLogger("xboing.LevelCompleteController")


class LevelCompleteController(Controller):
    """Handles input and transitions for the LevelCompleteView.

    Handles spacebar to advance to next level.
    Also handles LevelCompleteEvent and level advancement logic.
    """

    def __init__(
        self,
        game_state: Any,
        level_manager: Any,
        balls: List[Any],
        game_controller: Any,
        ui_manager: UIManager,
        game_view: Any,
        layout: Any,
        on_advance_callback: Optional[Callable[[], None]] = None,
        audio_manager: Optional[AudioManager] = None,
        quit_callback: Optional[Callable[[], None]] = None,
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
            on_advance_callback: Callback to advance to the next level (optional).
            audio_manager: The AudioManager instance (optional).
            quit_callback: Callback to quit the game (optional).

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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                logger.debug(
                    "Spacebar pressed on LevelCompleteView. Advancing to next level."
                )
                self.advance_to_next_level()

    def advance_to_next_level(self) -> None:
        """Advance to the next level and switch to the game view/controller."""
        logger.debug(
            "advance_to_next_level called: advancing to next level and switching to game view/controller."
        )
        self.game_controller.level_complete = False  # Reset for new level
        # Disable sticky paddle on new level
        self.game_controller.on_new_level_loaded()
        # Get the events returned by set_level and post them
        level_changed_events = self.game_state.set_level(self.game_state.level + 1)
        self.post_game_state_events(level_changed_events)

        self.level_manager.get_next_level()
        pygame.event.post(
            pygame.event.Event(
                pygame.USEREVENT, {"event": type("UIButtonClickEvent", (), {})()}
            )
        )
        level_info = self.level_manager.get_level_info()
        level_title = level_info["title"]
        post_level_title_message(level_title)
        self.balls.clear()
        self.balls.append(self.game_controller.create_new_ball())
        self.game_view.balls = self.balls
        self.ui_manager.set_view("game")
        # Optionally sync controller with view if needed

    def handle_event(self, _event: Any) -> None:
        """Handle a LevelCompleteEvent and switch to the level_complete view.

        Args:
        ----
            event: A single event object (type may vary).

        """
        logger.info(
            "handle_event called: LevelCompleteEvent received. Switching to level_complete view."
        )
        self.ui_manager.set_view("level_complete")

    def update(self, delta_ms: float) -> None:
        """Update logic for level complete view (usually minimal).

        Args:
        ----
            delta_time: Time elapsed since last update in milliseconds.

        """
        # No-op for now

    def post_game_state_events(self, changes: List[Any]) -> None:
        """Post all events returned by GameState/model methods to the Pygame event queue.

        This implements the decoupled event firing pattern: models return events, controllers post them.

        Args:
        ----
            changes: List of event objects to post to the Pygame event queue.

        """
        for event in changes:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": event}))
