"""Controller for handling the game over state in XBoing."""

import logging
from typing import Any, Callable, List, Optional

from injector import inject
import pygame

from xboing.controllers.controller import Controller
from xboing.controllers.controller_manager import ControllerManager
from xboing.controllers.game_controller import GameController
from xboing.engine.audio_manager import AudioManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.layout.game_layout import GameLayout
from xboing.ui.game_view import GameView
from xboing.ui.ui_manager import UIManager

logger = logging.getLogger("xboing.GameOverController")


class GameOverController(Controller):
    """Controller for handling the game over state, including resetting the game and handling input events.

    The controller_manager attribute is set after construction to avoid DI circular dependency.
    """

    @inject
    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        game_controller: GameController,
        game_view: GameView,
        layout: GameLayout,
        ui_manager: UIManager,
        audio_manager: AudioManager,
        quit_callback: Callable[[], None],
    ) -> None:
        """Initialize the GameOverController with all required dependencies.

        Args:
        ----
            game_state: The current game state.
            level_manager: The level manager instance.
            game_controller: The main game controller instance.
            game_view: The main game view instance.
            layout: The game layout instance.
            ui_manager: The UIManager instance.
            audio_manager: The AudioManager instance.
            quit_callback: Callback to quit the game.

        """
        self.game_state = game_state
        self.level_manager = level_manager
        self.game_controller = game_controller
        self.game_view = game_view
        self.layout = layout
        self.reset_callback = self.reset_game
        self.audio_manager = audio_manager
        self.quit_callback = quit_callback
        self.ui_manager = ui_manager
        self.controller_manager: Optional[ControllerManager] = (
            None  # Set after construction
        )

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle Pygame events for the game over screen.

        Args:
        ----
            events: List of Pygame events to process.

        """
        for event in events:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and self.reset_callback is not None
            ):
                self.reset_callback()

    def reset_game(self) -> None:
        """Reset the game state and return to gameplay view.

        Note: controller_manager must be set before calling this method.
        """
        logger.debug(
            f"[reset_game] ENTER id(self)={id(self)}, id(self.game_controller)={id(self.game_controller)}, id(self.game_controller.ball_manager)={id(self.game_controller.ball_manager)}"
        )
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
        self.game_controller.ball_manager.clear()
        new_ball = self.game_controller.create_new_ball()
        self.game_controller.ball_manager.add_ball(new_ball)
        logger.debug(
            f"[reset_game] New ball created: id={id(new_ball)}, stuck_to_paddle={new_ball.stuck_to_paddle}"
        )

        # Assert ball state
        balls = self.game_controller.ball_manager.balls
        assert len(balls) == 1, f"Expected 1 ball after reset, got {len(balls)}"
        assert balls[0].stuck_to_paddle, "Ball should be stuck to paddle after reset"

        # Switch active controller to 'game'
        if self.controller_manager is not None:
            self.controller_manager.set_controller("game")
        else:
            logger.error("[reset_game] controller_manager is not set or None!")

        # Switch UI view to 'game'
        if self.ui_manager is not None:
            self.ui_manager.set_view("game")
        else:
            logger.error("[reset_game] ui_manager is not set or None!")
        logger.debug(
            f"[reset_game] EXIT id(self)={id(self)}, id(self.game_controller)={id(self.game_controller)}, id(self.game_controller.ball_manager)={id(self.game_controller.ball_manager)}"
        )

    def handle_event(self, event: Any) -> None:
        """Handle a single event (protocol stub for future use).

        Args:
        ----
            event: A single event object (type may vary).

        """
        # No-op for now

    def update(self, delta_ms: float) -> None:
        """Update method (no-op for GameOverController).

        Args:
        ----
            delta_ms: Time elapsed since last update in milliseconds.

        """
        # No-op for now
