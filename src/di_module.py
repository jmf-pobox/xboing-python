from typing import Callable, List, Optional

import pygame
from injector import Module, provider

from controllers.game_controller import GameController
from controllers.game_over_controller import GameOverController
from controllers.instructions_controller import InstructionsController
from engine.audio_manager import AudioManager
from game.ball import Ball
from game.game_state import GameState
from game.level_manager import LevelManager
from layout.game_layout import GameLayout
from ui.game_over_view import GameOverView
from ui.game_view import GameView
from ui.instructions_view import InstructionsView
from ui.ui_manager import UIManager


class XBoingModule(Module):
    """
    Dependency injection module for XBoing, providing all core controllers and views.
    Binds game state, managers, controllers, UI, and callback dependencies for injection.
    """

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
        get_score_callback: Callable[[], int],
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        reset_game_callback: Optional[Callable[[], None]],
        instructions_font: pygame.font.Font,
        instructions_headline_font: pygame.font.Font,
        instructions_text_font: pygame.font.Font,
        on_exit_callback: Optional[Callable[[], None]],
    ):
        """
        Initialize the XBoingModule with all dependencies for DI.

        Args:
            game_state: The main GameState instance.
            level_manager: The LevelManager instance.
            balls: List of Ball objects in play.
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
        """
        self._game_state = game_state
        self._level_manager = level_manager
        self._balls = balls
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

    @provider
    def provide_game_over_controller(self) -> GameOverController:
        return GameOverController(
            game_state=self._game_state,
            level_manager=self._level_manager,
            balls=self._balls,
            game_controller=self._game_controller,
            game_view=self._game_view,
            layout=self._layout,
            ui_manager=self._ui_manager,
            audio_manager=self._audio_manager,
            quit_callback=self._quit_callback,
        )

    @provider
    def provide_game_over_view(self) -> GameOverView:
        return GameOverView(
            layout=self._layout,
            renderer=self._game_view.renderer,
            font=self._font,
            small_font=self._small_font,
            get_score_callback=self._get_score_callback,
            reset_game_callback=self._reset_game_callback,
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
