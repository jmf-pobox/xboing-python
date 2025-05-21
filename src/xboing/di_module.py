"""Dependency injection registry for XBoing.

Provides canonical, pre-initialized instances of all core game objects, managers, controllers, and UI components.
All providers return the instance passed to __init__, ensuring singleton-like behavior and consistency throughout the app.
No provider constructs or accepts dependencies as parameters; all are returned from instance variables.
"""

import logging
from typing import Callable, Optional

from injector import Module, provider
import pygame

from xboing.controllers.controller_manager import ControllerManager
from xboing.controllers.game_controller import GameController
from xboing.controllers.game_over_controller import GameOverController
from xboing.controllers.instructions_controller import InstructionsController
from xboing.controllers.level_complete_controller import LevelCompleteController
from xboing.engine.audio_manager import AudioManager
from xboing.engine.graphics import Renderer
from xboing.engine.input import InputManager
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout
from xboing.renderers.ammo_renderer import MAX_AMMO, AmmoRenderer
from xboing.renderers.bullet_renderer import BulletRenderer
from xboing.renderers.digit_renderer import DigitRenderer
from xboing.renderers.lives_renderer import LivesRenderer
from xboing.ui.ammo_display import AmmoDisplayComponent
from xboing.ui.bottom_bar_view import BottomBarView
from xboing.ui.game_over_view import GameOverView
from xboing.ui.game_view import GameView
from xboing.ui.instructions_view import InstructionsView
from xboing.ui.level_complete_view import LevelCompleteView
from xboing.ui.level_display import LevelDisplay
from xboing.ui.lives_display import LivesDisplayComponent
from xboing.ui.message_display import MessageDisplay
from xboing.ui.score_display import ScoreDisplay
from xboing.ui.special_display import SpecialDisplay
from xboing.ui.timer_display import TimerDisplay
from xboing.ui.top_bar_view import TopBarView
from xboing.ui.ui_manager import UIManager
from xboing.utils.asset_loader import create_font

WINDOW_WIDTH = 565  # Update if your window width is different
RIGHT_MARGIN = 20
RIGHT_EDGE_X = 475


class XBoingModule(Module):
    """Dependency injection registry for XBoing.

    Provides canonical, pre-initialized instances of all core game objects, managers, controllers, and UI components.
    All providers return the instance passed to __init__, ensuring singleton-like behavior and consistency throughout the app.
    No provider constructs or accepts dependencies as parameters; all are returned from instance variables.
    """

    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        ball_manager: BallManager,
        paddle: Paddle,
        block_manager: BlockManager,
        game_controller: GameController,
        game_view: GameView,
        layout: GameLayout,
        ui_manager: UIManager,
        audio_manager: AudioManager,
        quit_callback: Callable[[], None],
        get_score_callback: Callable[[], int],
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        reset_game_callback: Optional[Callable[[], None]],
        instructions_font: pygame.font.Font,
        instructions_headline_font: pygame.font.Font,
        instructions_text_font: pygame.font.Font,
        on_exit_callback: Optional[Callable[[], None]],
        input_manager: InputManager,
        bullet_manager: BulletManager,
        bullet_renderer: BulletRenderer,
    ) -> None:
        """Initialize the registry with all canonical game objects and managers."""
        self._game_state = game_state
        self._level_manager = level_manager
        self._ball_manager = ball_manager
        self._paddle = paddle
        self._block_manager = block_manager
        self._game_controller = game_controller
        self._game_view = game_view
        self._layout = layout
        self._ui_manager = ui_manager
        self._audio_manager = audio_manager
        self._quit_callback = quit_callback
        self._get_score_callback = get_score_callback
        self._font = font
        self._small_font = small_font
        self._reset_game_callback = reset_game_callback
        self._instructions_font = instructions_font
        self._instructions_headline_font = instructions_headline_font
        self._instructions_text_font = instructions_text_font
        self._on_exit_callback = on_exit_callback
        self._input_manager = input_manager
        self._bullet_manager = bullet_manager
        self._bullet_renderer = bullet_renderer
        self._renderer = game_view.renderer
        self.logger = logging.getLogger(f"xboing.{self.__class__.__name__}")

    @provider
    def provide_digit_renderer(self) -> DigitRenderer:
        """Return a DigitRenderer for digit rendering in the UI."""
        return DigitRenderer()

    @provider
    def provide_lives_renderer(self) -> LivesRenderer:
        """Return a LivesRenderer for rendering lives in the UI."""
        return LivesRenderer()

    @provider
    def provide_score_display(self, digit_renderer: DigitRenderer) -> ScoreDisplay:
        """Return a ScoreDisplay for the UI."""
        return ScoreDisplay(self._layout, digit_renderer, x=70, width=6)

    @provider
    def provide_lives_display_component(
        self, lives_renderer: LivesRenderer
    ) -> LivesDisplayComponent:
        """Return a LivesDisplayComponent for the UI."""
        max_lives = 3
        lives_surf = lives_renderer.render(
            max_lives, spacing=10, scale=1.0, max_lives=max_lives
        )
        lives_x = RIGHT_EDGE_X - lives_surf.get_width()
        return LivesDisplayComponent(
            self._layout, lives_renderer, x=lives_x, max_lives=max_lives
        )

    @provider
    def provide_ammo_renderer(self) -> AmmoRenderer:
        """Return an AmmoRenderer for rendering ammo in the UI."""
        return AmmoRenderer()

    @provider
    def provide_ammo_display_component(
        self,
        ammo_renderer: AmmoRenderer,
        lives_display_component: LivesDisplayComponent,
        game_state: "GameState",
    ) -> AmmoDisplayComponent:
        """Return an AmmoDisplayComponent for the UI."""
        lives_y, lives_height = lives_display_component.get_y_and_height()
        max_lives = 3
        lives_surf = lives_display_component.lives_display_util.render(
            max_lives, spacing=10, scale=1.0, max_lives=max_lives
        )
        lives_x = RIGHT_EDGE_X - lives_surf.get_width()
        lives_width = lives_surf.get_width()
        return AmmoDisplayComponent(
            self._layout,
            ammo_renderer,
            game_state,
            max_ammo=MAX_AMMO,
            lives_x=lives_x,
            lives_width=lives_width,
            lives_y=lives_y,
            lives_height=lives_height,
        )

    @provider
    def provide_level_display(self, digit_renderer: DigitRenderer) -> LevelDisplay:
        """Return a LevelDisplay for the UI."""
        return LevelDisplay(self._layout, digit_renderer, x=510)

    @provider
    def provide_timer_display(self) -> TimerDisplay:
        """Return a TimerDisplay for the UI."""
        ui_font = create_font(34)
        return TimerDisplay(self._layout, self._game_view.renderer, ui_font)

    @provider
    def provide_message_display(self) -> MessageDisplay:
        """Return a MessageDisplay for the UI."""
        message_font = create_font(28)
        return MessageDisplay(self._layout, self._game_view.renderer, message_font)

    @provider
    def provide_special_display(self) -> SpecialDisplay:
        """Return a SpecialDisplay for the UI."""
        special_font = create_font(16)
        return SpecialDisplay(self._layout, self._game_view.renderer, special_font)

    @provider
    def provide_top_bar_view(
        self,
        score_display: ScoreDisplay,
        lives_display_component: LivesDisplayComponent,
        level_display: LevelDisplay,
        ammo_display_component: AmmoDisplayComponent,
    ) -> TopBarView:
        """Return a TopBarView for the UI."""
        return TopBarView(
            score_display,
            lives_display_component,
            level_display,
            ammo_display_component,
        )

    @provider
    def provide_bottom_bar_view(
        self,
        message_display: MessageDisplay,
        special_display: SpecialDisplay,
        timer_display: TimerDisplay,
    ) -> BottomBarView:
        """Return a BottomBarView for the UI."""
        return BottomBarView(message_display, special_display, timer_display)

    @provider
    def provide_game_view(self) -> GameView:
        """Return the canonical GameView instance."""
        return self._game_view

    @provider
    def provide_level_complete_view(self) -> LevelCompleteView:
        """Return a LevelCompleteView for the UI."""
        font = self._font
        small_font = self._small_font
        return LevelCompleteView(
            self._layout,
            self._game_view.renderer,
            font,
            small_font,
            self._game_state,
            self._level_manager,
            on_advance_callback=None,  # To be set in main.py after instantiation
        )

    @provider
    def provide_game_over_controller(self) -> GameOverController:
        """Return a GameOverController for handling game over state."""
        return GameOverController(
            game_state=self._game_state,
            level_manager=self._level_manager,
            game_controller=self._game_controller,
            game_view=self._game_view,
            layout=self._layout,
            ui_manager=self._ui_manager,
            audio_manager=self._audio_manager,
            quit_callback=self._quit_callback,
        )

    @provider
    def provide_game_over_view(self) -> GameOverView:
        """Return a GameOverView for the UI."""
        return GameOverView(
            layout=self._layout,
            renderer=self._game_view.renderer,
            font=self._font,
            small_font=self._small_font,
            get_score_callback=self._get_score_callback,
        )

    @provider
    def provide_instructions_view(self) -> InstructionsView:
        """Return an InstructionsView for the UI."""
        return InstructionsView(
            layout=self._layout,
            renderer=self._game_view.renderer,
            font=self._instructions_font,
            headline_font=self._instructions_headline_font,
            text_font=self._instructions_text_font,
        )

    @provider
    def provide_instructions_controller(self) -> InstructionsController:
        """Return an InstructionsController for handling instructions view events."""
        return InstructionsController(
            on_exit_callback=self._on_exit_callback,
            audio_manager=self._audio_manager,
            quit_callback=self._quit_callback,
            ui_manager=self._ui_manager,
        )

    @provider
    def provide_game_controller(self) -> GameController:
        """Return the canonical GameController instance."""
        self.logger.debug(
            f"BulletManager id in GameController: {id(self._bullet_manager)}"
        )
        return self._game_controller

    @provider
    def provide_level_complete_controller(self) -> LevelCompleteController:
        """Return a LevelCompleteController for handling level completion logic."""
        return LevelCompleteController(
            self._game_state,
            self._level_manager,
            self._ball_manager.balls,
            self._game_controller,
            self._ui_manager,
            self._game_view,
            self._layout,
            on_advance_callback=None,  # To be set in main.py after instantiation
            audio_manager=self._audio_manager,
            quit_callback=self._quit_callback,
        )

    @provider
    def provide_controller_manager(
        self,
        game_controller: GameController,
        instructions_controller: InstructionsController,
        level_complete_controller: LevelCompleteController,
        game_over_controller: GameOverController,
    ) -> ControllerManager:
        """Return a ControllerManager for managing controllers and breaking DI cycles.

        This method wires up all controllers, registers them, and sets the initial controller.
        It also sets the controller_manager on game_over_controller to break the DI cycle.
        """
        manager = ControllerManager()
        manager.register_controller("game", game_controller)
        manager.register_controller("instructions", instructions_controller)
        manager.register_controller("level_complete", level_complete_controller)
        manager.register_controller("game_over", game_over_controller)
        manager.set_controller("game")
        game_over_controller.controller_manager = manager
        return manager

    @provider
    def provide_game_state(self) -> GameState:
        """Return the canonical GameState instance."""
        return self._game_state

    @provider
    def provide_level_manager(self) -> LevelManager:
        """Return the canonical LevelManager instance."""
        return self._level_manager

    @provider
    def provide_ball_manager(self) -> BallManager:
        """Return the canonical BallManager instance."""
        return self._ball_manager

    @provider
    def provide_paddle(self) -> Paddle:
        """Return the canonical Paddle instance."""
        return self._paddle

    @provider
    def provide_block_manager(self) -> BlockManager:
        """Return the canonical BlockManager instance."""
        return self._block_manager

    @provider
    def provide_game_layout(self) -> GameLayout:
        """Return the canonical GameLayout instance."""
        return self._layout

    @provider
    def provide_renderer(self) -> Renderer:
        """Return the canonical Renderer instance."""
        return self._renderer

    @provider
    def provide_input_manager(self) -> InputManager:
        """Return the canonical InputManager instance."""
        return self._input_manager

    @provider
    def provide_audio_manager(self) -> AudioManager:
        """Return the canonical AudioManager instance."""
        return self._audio_manager

    @provider
    def provide_ui_manager(self) -> UIManager:
        """Return the canonical UIManager instance."""
        return self._ui_manager

    @provider
    def provide_bullet_manager(self) -> BulletManager:
        """Return the canonical BulletManager instance."""
        return self._bullet_manager

    @provider
    def provide_bullet_renderer(self) -> BulletRenderer:
        """Return the canonical BulletRenderer instance."""
        return self._bullet_renderer
