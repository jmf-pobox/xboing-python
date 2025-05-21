from unittest.mock import Mock

import pygame
import pytest

from xboing.di_module import XBoingModule
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.renderers.bullet_renderer import BulletRenderer


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    pygame.display.set_mode((1, 1))  # Dummy video mode for image loading
    yield
    pygame.quit()


def make_module():
    gs = GameState()
    lm = LevelManager()
    bm = BallManager()
    paddle = Paddle(0, 0)
    sbm = BlockManager(0, 0)
    gc = Mock()
    gv = Mock()
    gv.renderer = Mock()
    layout = Mock()
    uim = Mock()
    am = Mock()
    im = Mock()
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
    return (
        module,
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
        im,
        bullet_manager,
        bullet_renderer,
    )


def test_providers_return_canonical_instances():
    (
        module,
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
        im,
        bullet_manager,
        bullet_renderer,
    ) = make_module()
    assert module.provide_game_state() is gs
    assert module.provide_level_manager() is lm
    assert module.provide_ball_manager() is bm
    assert module.provide_paddle() is paddle
    assert module.provide_block_manager() is sbm
    assert module.provide_game_view() is gv
    assert module.provide_ui_manager() is uim
    assert module.provide_audio_manager() is am
    assert module.provide_input_manager() is im
    assert module.provide_bullet_manager() is bullet_manager
    assert module.provide_bullet_renderer() is bullet_renderer


def test_ammo_and_bullet_providers():
    module, *_ = make_module()
    ammo_renderer = module.provide_ammo_renderer()
    assert ammo_renderer is not None
    bullet_renderer = module.provide_bullet_renderer()
    assert bullet_renderer is not None
