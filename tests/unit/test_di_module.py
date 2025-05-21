from unittest.mock import Mock

import pygame

from xboing.controllers.game_controller import GameController
from xboing.di_module import XBoingModule
from xboing.engine.audio_manager import AudioManager
from xboing.engine.input import InputManager
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout
from xboing.renderers.ammo_renderer import AmmoRenderer
from xboing.renderers.bullet_renderer import BulletRenderer
from xboing.ui.ammo_display import AmmoDisplayComponent
from xboing.ui.game_view import GameView
from xboing.ui.ui_manager import UIManager


def test_di_provides_ammo_components():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    gs = GameState()
    lm = LevelManager()
    bm = BallManager()
    paddle = Paddle(0, 0)
    sbm = BlockManager(0, 0)
    gc = Mock(spec=GameController)
    gv = Mock(spec=GameView)
    gv.renderer = Mock()  # Add renderer attribute to fix DI module initialization
    layout = Mock(spec=GameLayout)
    uim = Mock(spec=UIManager)
    am = Mock(spec=AudioManager)
    im = Mock(spec=InputManager)
    font = Mock()
    small_font = Mock()
    bullet_manager = BulletManager()
    bullet_renderer = BulletRenderer()
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
        bullet_manager,
        bullet_renderer,
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
