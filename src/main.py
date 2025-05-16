#!/usr/bin/env python3
"""
XBoing - A classic breakout-style game.

This is the main entry point for the game. It initializes the game
engine and runs the main game loop.
"""

import logging
import time

import pygame
from injector import Injector

from app_coordinator import AppCoordinator
from controllers.controller_factory import ControllerFactory
from controllers.game_over_controller import GameOverController
from controllers.instructions_controller import InstructionsController
from controllers.window_controller import WindowController
from di_module import XBoingModule
from engine.audio_manager import AudioManager
from engine.events import (
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    BlockHitEvent,
    BombExplodedEvent,
    BonusCollectedEvent,
    GameOverEvent,
    PaddleHitEvent,
    PowerUpCollectedEvent,
    UIButtonClickEvent,
    WallHitEvent,
)
from engine.graphics import Renderer
from engine.input import InputManager
from engine.window import Window
from game.game_setup import create_game_objects
from game.game_state import GameState
from layout.game_layout import GameLayout
from ui.game_over_view import GameOverView
from ui.instructions_view import InstructionsView
from ui.ui_factory import UIFactory
from ui.ui_manager import UIManager
from utils.asset_loader import create_font, load_image
from utils.asset_paths import get_asset_path, get_sounds_dir
from utils.logging_config import setup_logging

# Setup logging
setup_logging(logging.DEBUG)

# Game constants - matching the original XBoing dimensions
PLAY_WIDTH = 495  # Original game's play area width
PLAY_HEIGHT = 580  # Original game's play area height
MAIN_WIDTH = 70  # Width of the side panels in original
MAIN_HEIGHT = 130  # Height of additional UI elements

# Total window size
WINDOW_WIDTH = PLAY_WIDTH + MAIN_WIDTH  # 565
WINDOW_HEIGHT = PLAY_HEIGHT + MAIN_HEIGHT  # 710

# Game element sizes
PADDLE_WIDTH = 70  # Width of HUGE paddle in original
PADDLE_HEIGHT = 15  # Original paddle height
PADDLE_Y = WINDOW_HEIGHT - 40
BALL_RADIUS = 8  # Approximated from the original game
MAX_BALLS = 3
BLOCK_WIDTH = 40  # Original block width
BLOCK_HEIGHT = 20  # Original block height
BLOCK_MARGIN = 7  # Original spacing (SPACE constant)
GAME_TITLE = "- XBoing II -"

# Definition of event to sound mapping
event_sound_map = {
    BlockHitEvent: "boing",
    UIButtonClickEvent: "click",
    PowerUpCollectedEvent: "powerup",
    GameOverEvent: "game_over",
    BallShotEvent: "ballshot",
    BallLostEvent: "balllost",
    BombExplodedEvent: "bomb",
    ApplauseEvent: "applause",
    BonusCollectedEvent: "bonus",
    PaddleHitEvent: "paddle",
    WallHitEvent: "boing",
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    """Main entry point for the game."""
    logger.info("Starting XBoing initialization...")

    # --- Initialization: game state, audio, window, input, layout ---
    game_state = GameState()

    pygame.mixer.init()
    audio_manager = AudioManager(
        sound_dir=get_sounds_dir(), event_sound_map=event_sound_map
    )
    audio_manager.load_sounds_from_map()

    window = Window(WINDOW_WIDTH, WINDOW_HEIGHT, GAME_TITLE)
    # Set application icon
    icon_path = get_asset_path("images/icon.png")
    icon_surface = load_image(icon_path, alpha=True)
    window.set_icon(icon_surface)
    renderer = Renderer(window.surface)
    input_manager = InputManager()
    layout = GameLayout(WINDOW_WIDTH, WINDOW_HEIGHT)
    layout.load_backgrounds()

    # --- Create game objects: paddle, balls, blocks, level manager ---
    game_objects = create_game_objects(layout)
    paddle = game_objects["paddle"]
    balls = game_objects["balls"]
    block_manager = game_objects["block_manager"]
    level_manager = game_objects["level_manager"]
    bg_color = (40, 44, 52)
    # Set the timer in GameState to match the loaded level
    game_state.set_timer(level_manager.get_time_remaining())

    # --- UI Setup via UIFactory ---
    ui_elements = UIFactory.create_ui_components(
        game_state=game_state,
        layout=layout,
        renderer=renderer,
        balls=balls,
        paddle=paddle,
        block_manager=block_manager,
        level_manager=level_manager,
    )
    views = ui_elements["views"]
    top_bar_view = ui_elements["top_bar"]
    bottom_bar_view = ui_elements["bottom_bar"]
    game_view = ui_elements["game_view"]
    instructions_view = ui_elements["instructions_view"]
    game_over_view = ui_elements["game_over_view"]
    level_complete_view = ui_elements["level_complete_view"]

    # --- UI Manager ---
    ui_manager = UIManager()
    ui_manager.setup_ui(
        views=views,
        top_bar=top_bar_view,
        bottom_bar=bottom_bar_view,
        initial_view="game",
    )

    # --- Controller Setup via ControllerFactory ---
    controller_elements = ControllerFactory.create_and_register_controllers(
        game_state=game_state,
        level_manager=level_manager,
        balls=balls,
        paddle=paddle,
        block_manager=block_manager,
        input_manager=input_manager,
        layout=layout,
        renderer=renderer,
        audio_manager=audio_manager,
        event_sound_map=event_sound_map,
        ui_manager=ui_manager,
        quit_callback=lambda: nonlocal_vars.update({"running": False}),
        reset_game_callback=lambda: None,  # Placeholder for real callback
    )
    controller_manager = controller_elements["controller_manager"]
    game_controller = controller_elements["game_controller"]
    instructions_controller = controller_elements["instructions_controller"]
    level_complete_controller = controller_elements["level_complete_controller"]

    # Add an initial ball to start the game in the correct state
    balls.append(game_controller.create_new_ball())

    # --- AppCoordinator: sync UIManager and ControllerManager ---
    coordinator = AppCoordinator(ui_manager, controller_manager)

    # --- DI for GameOverController, GameOverView, InstructionsView, InstructionsController ---
    font = create_font(24)
    small_font = create_font(18)
    instructions_headline_font = create_font(26)
    instructions_text_font = create_font(21)
    xboing_module = XBoingModule(
        game_state=game_state,
        level_manager=level_manager,
        balls=balls,
        game_controller=game_controller,
        game_view=game_view,
        layout=layout,
        ui_manager=ui_manager,
        audio_manager=audio_manager,
        quit_callback=lambda: nonlocal_vars.update({"running": False}),
        get_score_callback=lambda: game_state.score,
        font=font,
        small_font=small_font,
        reset_game_callback=lambda: None,  # Placeholder callback for DI
        instructions_font=font,
        instructions_headline_font=instructions_headline_font,
        instructions_text_font=instructions_text_font,
        on_exit_callback=lambda: ui_manager.set_view("game"),
    )
    injector = Injector([xboing_module])
    game_over_controller = injector.get(GameOverController)
    game_over_view = injector.get(GameOverView)
    instructions_view = injector.get(InstructionsView)
    instructions_controller = injector.get(InstructionsController)

    # Now wire up the correct callbacks and event subscriptions
    level_complete_view.on_advance_callback = (
        level_complete_controller.advance_to_next_level
    )
    game_over_controller.reset_callback = game_over_controller.reset_game
    game_over_view.reset_game = game_over_controller.reset_game

    # --- Game loop ---
    last_time = time.time()
    nonlocal_vars = {"running": True}
    window_controller = WindowController(
        audio_manager=audio_manager,
        quit_callback=lambda: nonlocal_vars.update({"running": False}),
        ui_manager=ui_manager,
    )
    while nonlocal_vars["running"]:
        now = time.time()
        delta_time = now - last_time
        last_time = now

        events = pygame.event.get()
        input_manager.update(events)
        window_controller.handle_events(events)  # Handle global/system events
        controller_manager.active_controller.handle_events(events)
        audio_manager.handle_events(events)
        ui_manager.handle_events(events)
        controller_manager.active_controller.update(delta_time * 1000)

        # Clear/redraw the background and window hierarchy before drawing UI
        layout.draw(window.surface)
        ui_manager.draw_all(window.surface)
        window.update()

    pygame.quit()


if __name__ == "__main__":
    main()
