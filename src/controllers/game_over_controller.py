import logging
from typing import Callable

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
    @inject
    def __init__(
        self,
        game_state: GameState,
        level_manager: LevelManager,
        balls: list[Ball],
        game_controller: GameController,
        game_view: GameView,
        layout: GameLayout,
        ui_manager: UIManager,
        audio_manager: AudioManager,
        quit_callback: Callable[[], None],
    ):
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

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.reset_callback:
                    self.reset_callback()

    def reset_game(self):
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
            play_rect = self.layout.get_play_rect()
        self.balls.clear()
        self.balls.append(self.game_controller.create_new_ball())
        self.game_view.balls = self.balls
        self.game_controller.waiting_for_launch = True
        # If waiting_for_launch is needed, it should be handled by main or passed in
        if self.ui_manager:
            self.ui_manager.set_view("game")

    def handle_event(self, event):
        pass  # No EventBus events handled yet, but protocol is implemented for future use

    def update(self, delta_ms):
        pass  # GameOverController does not need to update per frame
