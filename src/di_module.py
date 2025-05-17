from typing import Callable, Optional

import pygame
from injector import Module, provider

from controllers.controller_manager import ControllerManager
from controllers.game_controller import GameController
from controllers.game_over_controller import GameOverController
from controllers.instructions_controller import InstructionsController
from controllers.level_complete_controller import LevelCompleteController
from engine.audio_manager import AudioManager
from engine.graphics import Renderer
from engine.input import InputManager
from game.ball_manager import BallManager
from game.game_state import GameState
from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlockManager
from layout.game_layout import GameLayout
from renderers.digit_renderer import DigitRenderer
from renderers.lives_renderer import LivesRenderer
from ui.bottom_bar_view import BottomBarView
from ui.game_over_view import GameOverView
from ui.game_view import GameView
from ui.instructions_view import InstructionsView
from ui.level_complete_view import LevelCompleteView
from ui.level_display import LevelDisplay
from ui.lives_display import LivesDisplayComponent
from ui.message_display import MessageDisplay
from ui.score_display import ScoreDisplay
from ui.special_display import SpecialDisplay
from ui.timer_display import TimerDisplay
from ui.top_bar_view import TopBarView
from ui.ui_manager import UIManager
from utils.asset_loader import create_font


class XBoingModule(Module):
    """
    Dependency injection module for XBoing, providing all core controllers and views.
    Binds game state, managers, controllers, UI, and callback dependencies for injection.
    """

    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        ball_manager: BallManager,
        paddle: Paddle,
        block_manager: SpriteBlockManager,
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
    ):
        """
        Initialize the XBoingModule with all dependencies for DI.

        Args:
            game_state: The main GameState instance.
            level_manager: The LevelManager instance.
            ball_manager: The BallManager instance.
            paddle: The Paddle instance.
            block_manager: The SpriteBlockManager instance.
            game_controller: The main GameController instance.
            game_view: The main GameView instance.
            layout: The GameLayout instance.
            ui_manager: The UIManager instance.
            audio_manager: The AudioManager instance.
            quit_callback: Callback to quit the game.
            get_score_callback: Callback to get the current score.
            font: Main font for UI and overlays.
            small_font: Secondary font for UI and overlays.
            reset_game_callback: Callback to reset the game (optional).
            instructions_font: Font for instructions view.
            instructions_headline_font: Headline font for instructions view.
            instructions_text_font: Text font for instructions view.
            on_exit_callback: Callback to exit instructions (optional).
            input_manager: The InputManager instance.
        """
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

    # --- UI Providers ---
    @provider
    def provide_digit_renderer(self) -> DigitRenderer:
        return DigitRenderer()

    @provider
    def provide_lives_renderer(self) -> LivesRenderer:
        return LivesRenderer()

    @provider
    def provide_score_display(self, digit_renderer: DigitRenderer) -> ScoreDisplay:
        return ScoreDisplay(self._layout, digit_renderer, x=70, width=6)

    @provider
    def provide_lives_display_component(
        self, lives_renderer: LivesRenderer
    ) -> LivesDisplayComponent:
        return LivesDisplayComponent(self._layout, lives_renderer, x=365, max_lives=3)

    @provider
    def provide_level_display(self, digit_renderer: DigitRenderer) -> LevelDisplay:
        return LevelDisplay(self._layout, digit_renderer, x=510)

    @provider
    def provide_timer_display(self) -> TimerDisplay:
        ui_font = create_font(34)
        return TimerDisplay(self._layout, self._game_view.renderer, ui_font)

    @provider
    def provide_message_display(self) -> MessageDisplay:
        message_font = create_font(28)
        return MessageDisplay(self._layout, self._game_view.renderer, message_font)

    @provider
    def provide_special_display(self) -> SpecialDisplay:
        special_font = create_font(16)
        return SpecialDisplay(self._layout, self._game_view.renderer, special_font)

    @provider
    def provide_top_bar_view(
        self,
        score_display: ScoreDisplay,
        lives_display_component: LivesDisplayComponent,
        level_display: LevelDisplay,
    ) -> TopBarView:
        return TopBarView(score_display, lives_display_component, level_display)

    @provider
    def provide_bottom_bar_view(
        self,
        message_display: MessageDisplay,
        special_display: SpecialDisplay,
        timer_display: TimerDisplay,
    ) -> BottomBarView:
        return BottomBarView(message_display, special_display, timer_display)

    @provider
    def provide_game_view(self) -> GameView:
        return GameView(
            self._layout,
            self._block_manager,
            self._paddle,
            self._ball_manager,
            self._game_view.renderer,
        )

    @provider
    def provide_level_complete_view(self) -> LevelCompleteView:
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

    # --- Existing controller/view providers ---
    @provider
    def provide_game_over_controller(self) -> GameOverController:
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
    def provide_game_over_view(
        self, game_over_controller: GameOverController
    ) -> GameOverView:
        return GameOverView(
            layout=self._layout,
            renderer=self._game_view.renderer,
            font=self._font,
            small_font=self._small_font,
            get_score_callback=self._get_score_callback,
        )

    @provider
    def provide_instructions_view(self) -> InstructionsView:
        return InstructionsView(
            layout=self._layout,
            renderer=self._game_view.renderer,
            font=self._instructions_font,
            headline_font=self._instructions_headline_font,
            text_font=self._instructions_text_font,
        )

    @provider
    def provide_instructions_controller(self) -> InstructionsController:
        return InstructionsController(
            on_exit_callback=self._on_exit_callback,
            audio_manager=self._audio_manager,
            quit_callback=self._quit_callback,
            ui_manager=self._ui_manager,
        )

    # --- Controller Providers ---
    @provider
    def provide_game_controller(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        ball_manager: BallManager,
        paddle: Paddle,
        block_manager: SpriteBlockManager,
        input_manager: InputManager,
        layout: GameLayout,
        renderer: Renderer,
    ) -> GameController:
        return GameController(
            game_state,
            level_manager,
            ball_manager,
            paddle,
            block_manager,
            input_manager=input_manager,
            layout=layout,
            renderer=renderer,
        )

    @provider
    def provide_level_complete_controller(
        self,
        game_view: GameView,
    ) -> LevelCompleteController:
        return LevelCompleteController(
            self._game_state,
            self._level_manager,
            self._ball_manager.balls,
            self._game_controller,
            self._ui_manager,
            game_view,  # Use the injected GameView
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
        manager = ControllerManager()
        manager.register_controller("game", game_controller)
        manager.register_controller("instructions", instructions_controller)
        manager.register_controller("level_complete", level_complete_controller)
        manager.register_controller("game_over", game_over_controller)
        manager.set_controller("game")
        # Set controller_manager on game_over_controller to break DI cycle
        game_over_controller.controller_manager = manager
        return manager

    @provider
    def provide_game_state(self) -> GameState:
        return self._game_state

    @provider
    def provide_level_manager(self) -> LevelManager:
        return self._level_manager

    @provider
    def provide_ball_manager(self) -> BallManager:
        return self._ball_manager

    @provider
    def provide_paddle(self) -> Paddle:
        return self._paddle

    @provider
    def provide_block_manager(self) -> SpriteBlockManager:
        return self._block_manager

    @provider
    def provide_game_layout(self) -> GameLayout:
        return self._layout

    @provider
    def provide_renderer(self) -> Renderer:
        return self._game_view.renderer

    @provider
    def provide_input_manager(self) -> InputManager:
        return self._input_manager

    @provider
    def provide_audio_manager(self) -> AudioManager:
        return self._audio_manager

    @provider
    def provide_ui_manager(self) -> UIManager:
        return self._ui_manager
