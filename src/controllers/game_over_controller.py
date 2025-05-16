import logging
from typing import Any, Callable, List

import pygame
from injector import inject

from controllers.game_controller import GameController
from engine.audio_manager import AudioManager
from game.ball import Ball
from game.game_state import GameState
from game.level_manager import LevelManager
from layout.game_layout import GameLayout
from ui.game_view import GameView
from ui.ui_manager import UIManager

logger = logging.getLogger("xboing.GameOverController")


class GameOverController:
    """
    Controller for handling the game over state, including resetting the game and handling input events.
    """

    @inject
    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        balls: List[Ball],
        game_controller: GameController,
        game_view: GameView,
        layout: GameLayout,
        ui_manager: UIManager,
        audio_manager: AudioManager,
        quit_callback: Callable[[], None],
    ) -> None:
        """
        Initialize the GameOverController with all required dependencies.

        Args:
            game_state: The current game state.
            level_manager: The level manager instance.
            balls: List of Ball objects in play.
            game_controller: The main game controller instance.
            game_view: The main game view instance.
            layout: The game layout instance.
            ui_manager: The UIManager instance.
            audio_manager: The AudioManager instance.
            quit_callback: Callback to quit the game.
        """
        self.game_state = game_state
        self.level_manager = level_manager
        self.balls = balls
        self.game_controller = game_controller
        self.game_view = game_view
        self.layout = layout
        self.reset_callback = self.reset_game
        self.audio_manager = audio_manager
        self.quit_callback = quit_callback
        self.ui_manager = ui_manager

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Handle Pygame events for the game over screen.

        Args:
            events: List of Pygame events to process.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.reset_callback is not None:
                    self.reset_callback()

    def reset_game(self) -> None:
        """
        Reset the game state and return to gameplay view.
        """
        logger.info(
            "reset_game called: restarting game state and returning to gameplay view."
        )
        changes = self.game_state.full_restart(
            self.level_manager,
        )
        self.game_controller.post_game_state_events(changes)
        logger.info(
            f"After full_restart: game_state.is_game_over() = {self.game_state.is_game_over()}"
        )
        if self.layout:
            self.layout.get_play_rect()
        self.balls.clear()
        self.balls.append(self.game_controller.create_new_ball())
        self.game_view.balls = self.balls
        self.game_controller.waiting_for_launch = True
        # If waiting_for_launch is needed, it should be handled by main or passed in
        if self.ui_manager:
            self.ui_manager.set_view("game")

    def handle_event(self, event: Any) -> None:
        """
        Handle a single event (protocol stub for future use).

        Args:
            event: A single event object (type may vary).
        """
        pass  # No EventBus events handled yet, but protocol is implemented for future use

    def update(self, delta_ms: float) -> None:
        """
        Update method (no-op for GameOverController).

        Args:
            delta_ms: Time elapsed since last update in milliseconds.
        """
        pass  # GameOverController does not need to update per frame
