"""Main entry point for the XBoing game application.

This module defines the XBoingApp class, which encapsulates all game setup and the main loop.
"""

import logging
import time
import typing
from typing import Dict, cast

from injector import Injector
import pygame

from xboing.app_coordinator import AppCoordinator
from xboing.controllers.controller import Controller
from xboing.controllers.controller_manager import ControllerManager
from xboing.controllers.game_controller import GameController
from xboing.controllers.level_complete_controller import LevelCompleteController
from xboing.controllers.window_controller import WindowController
from xboing.di_module import XBoingModule
from xboing.engine.audio_manager import AudioManager
from xboing.engine.graphics import Renderer
from xboing.engine.input import InputManager
from xboing.engine.window import Window
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_setup import create_game_objects
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout
from xboing.renderers.bullet_renderer import BulletRenderer
from xboing.ui.bottom_bar_view import BottomBarView
from xboing.ui.game_over_view import GameOverView
from xboing.ui.game_view import GameView
from xboing.ui.instructions_view import InstructionsView
from xboing.ui.level_complete_view import LevelCompleteView
from xboing.ui.top_bar_view import TopBarView
from xboing.ui.ui_manager import UIManager
from xboing.ui.view import View
from xboing.utils.asset_loader import create_font, load_image
from xboing.utils.asset_paths import get_asset_path, get_sounds_dir
from xboing.utils.logging_config import setup_logging

# Setup logging
setup_logging(logging.CRITICAL)

# Game constants - matching the original XBoing dimensions
PLAY_WIDTH: int = 495  # Original game's play area width
PLAY_HEIGHT: int = 580  # Original game's play area height
MAIN_WIDTH: int = 70  # Width of the side panels in original
MAIN_HEIGHT: int = 130  # Height of additional UI elements

# Total window size
WINDOW_WIDTH: int = PLAY_WIDTH + MAIN_WIDTH  # 565
WINDOW_HEIGHT: int = PLAY_HEIGHT + MAIN_HEIGHT  # 710

# Game element sizes
PADDLE_WIDTH: int = 70  # Width of HUGE paddle in original
PADDLE_HEIGHT: int = 15  # Original paddle height
PADDLE_Y: int = WINDOW_HEIGHT - 40
BALL_RADIUS: int = 8  # Approximated from the original game
MAX_BALLS: int = 3
BLOCK_WIDTH: int = 40  # Original block width
BLOCK_HEIGHT: int = 20  # Original block height
BLOCK_MARGIN: int = 7  # Original spacing (SPACE constant)
GAME_TITLE: str = "- XBoing II -"

logger: logging.Logger = logging.getLogger(__name__)


class XBoingApp:
    """Main application class for XBoing.

    Handles all game setup, dependency injection, and the main game loop.
    """

    game_state: GameState
    audio_manager: AudioManager
    window: Window
    renderer: Renderer
    input_manager: InputManager
    layout: GameLayout
    paddle: Paddle
    ball_manager: BallManager
    block_manager: BlockManager
    level_manager: LevelManager
    bullet_manager: BulletManager
    bullet_renderer: BulletRenderer
    ui_manager: UIManager
    nonlocal_vars: Dict[str, bool]
    font: pygame.font.Font
    small_font: pygame.font.Font
    instructions_headline_font: pygame.font.Font
    instructions_text_font: pygame.font.Font
    game_view: GameView
    game_controller: GameController
    injector: Injector
    controller_manager: ControllerManager
    level_complete_controller: LevelCompleteController
    views: Dict[str, View]
    top_bar_view: TopBarView
    bottom_bar_view: BottomBarView
    game_over_view: GameOverView
    level_complete_view: LevelCompleteView
    window_controller: WindowController

    def __init__(self) -> None:
        """Initialize the XBoing application and all dependencies."""
        # --- Logging and Pygame/Audio Initialization ---
        self.game_state = GameState()
        pygame.mixer.init()
        self.audio_manager = AudioManager(sound_dir=get_sounds_dir())
        self.audio_manager.load_sounds_from_events()

        # --- Window and Renderer Setup ---
        self.window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
        icon_path = get_asset_path("images/icon.png")
        icon_surface = load_image(icon_path, alpha=True)
        self.window.set_icon(icon_surface)
        self.renderer = Renderer(self.window.surface)
        self.input_manager = InputManager()

        # --- Layout and Core Game Objects ---
        self.layout = GameLayout(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.layout.load_backgrounds()
        game_objects = create_game_objects(self.layout)
        self.paddle = game_objects["paddle"]
        self.ball_manager = game_objects["ball_manager"]
        self.block_manager = game_objects["block_manager"]
        self.level_manager = game_objects["level_manager"]
        self.bullet_manager = game_objects["bullet_manager"]
        self.bullet_renderer = game_objects["bullet_renderer"]
        self.game_state.set_timer(self.level_manager.get_time_remaining())

        # --- UI Manager and Fonts ---
        self.ui_manager = UIManager()
        self.nonlocal_vars = {"running": True}
        self.font = create_font(24)
        self.small_font = create_font(18)
        self.instructions_headline_font = create_font(26)
        self.instructions_text_font = create_font(21)

        # --- Dummy GameView and GameController for Partial DI ---
        dummy_game_view = GameView(
            self.layout,
            self.block_manager,
            self.paddle,
            self.ball_manager,
            self.renderer,
            self.bullet_manager,
            self.bullet_renderer,
        )
        self.game_controller = GameController(
            self.game_state,
            self.level_manager,
            self.ball_manager,
            self.paddle,
            self.block_manager,
            input_manager=self.input_manager,
            layout=self.layout,
            renderer=self.renderer,
            bullet_manager=self.bullet_manager,
        )
        xboing_module_partial = XBoingModule(
            game_state=self.game_state,
            level_manager=self.level_manager,
            ball_manager=self.ball_manager,
            paddle=self.paddle,
            block_manager=self.block_manager,
            game_controller=self.game_controller,
            game_view=dummy_game_view,
            layout=self.layout,
            ui_manager=self.ui_manager,
            audio_manager=self.audio_manager,
            quit_callback=lambda: self.nonlocal_vars.update({"running": False}),
            get_score_callback=lambda: self.game_state.score,
            font=self.font,
            small_font=self.small_font,
            reset_game_callback=lambda: None,
            instructions_font=self.font,
            instructions_headline_font=self.instructions_headline_font,
            instructions_text_font=self.instructions_text_font,
            on_exit_callback=lambda: self.ui_manager.set_view("game"),
            input_manager=self.input_manager,
            bullet_manager=self.bullet_manager,
            bullet_renderer=self.bullet_renderer,
        )
        injector_partial = Injector([xboing_module_partial])
        self.game_view = injector_partial.get(GameView)

        # --- Full DI Setup with Real GameView and GameController ---
        xboing_module = XBoingModule(
            game_state=self.game_state,
            level_manager=self.level_manager,
            ball_manager=self.ball_manager,
            paddle=self.paddle,
            block_manager=self.block_manager,
            game_controller=self.game_controller,
            game_view=self.game_view,
            layout=self.layout,
            ui_manager=self.ui_manager,
            audio_manager=self.audio_manager,
            quit_callback=lambda: self.nonlocal_vars.update({"running": False}),
            get_score_callback=lambda: self.game_state.score,
            font=self.font,
            small_font=self.small_font,
            reset_game_callback=lambda: None,
            instructions_font=self.font,
            instructions_headline_font=self.instructions_headline_font,
            instructions_text_font=self.instructions_text_font,
            on_exit_callback=lambda: self.ui_manager.set_view("game"),
            input_manager=self.input_manager,
            bullet_manager=self.bullet_manager,
            bullet_renderer=self.bullet_renderer,
        )
        self.injector = Injector([xboing_module])

        # --- Controller and View Setup via DI ---
        self.controller_manager = self.injector.get(ControllerManager)
        self.game_controller = self.injector.get(GameController)
        self.level_complete_controller = self.injector.get(LevelCompleteController)
        assert (
            self.controller_manager is not None
        ), "controller_manager should never be None after DI setup"
        self.ball_manager.add_ball(self.game_controller.create_new_ball())
        self.views = {
            "game": self.game_view,
            "instructions": self.injector.get(InstructionsView),
            "game_over": self.injector.get(GameOverView),
            "level_complete": self.injector.get(LevelCompleteView),
        }
        self.top_bar_view = self.injector.get(TopBarView)
        self.bottom_bar_view = self.injector.get(BottomBarView)
        self.game_over_view = cast(GameOverView, self.views["game_over"])
        self.level_complete_view = cast(LevelCompleteView, self.views["level_complete"])

        # --- UI Wiring and App Coordination ---
        self.ui_manager.setup_ui(
            views=self.views,
            top_bar=self.top_bar_view,
            bottom_bar=self.bottom_bar_view,
            initial_view="game",
        )
        AppCoordinator(self.ui_manager, self.controller_manager)
        self.level_complete_view.on_advance_callback = (
            self.level_complete_controller.advance_to_next_level
        )

        # --- Window Controller Setup ---
        self.window_controller = WindowController(
            audio_manager=self.audio_manager,
            quit_callback=lambda: self.nonlocal_vars.update({"running": False}),
            ui_manager=self.ui_manager,
        )
        self.ball_manager = self.injector.get(BallManager)
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"BulletManager id in XBoingApp: {id(self.bullet_manager)}")

    def run(self) -> None:
        """Run the main game loop."""
        last_time = time.time()
        while self.nonlocal_vars["running"]:
            now = time.time()
            delta_time = now - last_time
            last_time = now
            events = pygame.event.get()
            for event in events:
                self.logger.debug(
                    f"[main loop] Event type: {event.type}, event: {event}"
                )
            self.input_manager.update(events)
            self.window_controller.handle_events(events)
            assert (
                self.controller_manager is not None
            ), "controller_manager should never be None in main loop"
            active_controller = self.controller_manager.active_controller
            controller_name = getattr(
                active_controller, "name", type(active_controller).__name__
            )
            self.logger.debug(
                f"[main loop] Active controller: {controller_name}, id={id(active_controller)}"
            )
            assert (
                active_controller is not None
            ), "active_controller should never be None in main loop"
            active_controller = typing.cast(Controller, active_controller)
            active_controller.handle_events(events)
            self.audio_manager.handle_events(events)
            self.ui_manager.handle_events(events)
            active_controller.update(delta_time * 1000)
            self.layout.draw(self.window.surface)
            self.ui_manager.draw_all(self.window.surface)
            self.window.update()
        pygame.quit()


def main() -> None:
    """Application entry point. Instantiates and runs the XBoingApp."""
    app = XBoingApp()
    app.run()


if __name__ == "__main__":
    main()
