from unittest.mock import Mock

import pygame

from controllers.game_controller import GameController
from di_module import XBoingModule
from engine.audio_manager import AudioManager
from engine.input import InputManager
from game.ball_manager import BallManager
from game.game_state import GameState
from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlockManager
from layout.game_layout import GameLayout
from renderers.ammo_renderer import AmmoRenderer
from ui.ammo_display import AmmoDisplayComponent
from ui.game_view import GameView
from ui.ui_manager import UIManager


def test_di_provides_ammo_components():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    gs = GameState()
    lm = LevelManager()
    bm = BallManager()
    paddle = Paddle(0, 0, 10, 10)
    sbm = SpriteBlockManager(0, 0)
    gc = Mock(spec=GameController)
    gv = Mock(spec=GameView)
    layout = Mock(spec=GameLayout)
    uim = Mock(spec=UIManager)
    am = Mock(spec=AudioManager)
    im = Mock(spec=InputManager)
    font = Mock()
    small_font = Mock()
    module = XBoingModule(
        gs,
        lm,
        bm,
        paddle,
        sbm,
        gc,
        gv,
        layout,
        uim,
        am,
        lambda: None,
        lambda: 0,
        font,
        small_font,
        None,
        font,
        font,
        font,
        None,
        im,
    )
    ammo_renderer = module.provide_ammo_renderer()
    assert isinstance(ammo_renderer, AmmoRenderer)
    # Provide lives_display_component for dependency
    lives_renderer = module.provide_lives_renderer()
    lives_display_component = module.provide_lives_display_component(lives_renderer)
    ammo_display_component = module.provide_ammo_display_component(
        ammo_renderer, lives_display_component, gs
    )
    assert isinstance(ammo_display_component, AmmoDisplayComponent)
