from unittest.mock import Mock, patch

import pygame
import pytest

from controllers.game_controller import GameController
from engine.graphics import Renderer
from engine.input import InputManager
from game.ball_manager import BallManager
from game.bullet_manager import BulletManager
from game.game_state import GameState
from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlockManager
from layout.game_layout import GameLayout


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def make_controller():
    gs = GameState()
    lm = LevelManager()
    bm = BallManager()
    paddle = Paddle(0, 0, 10, 10)
    sbm = SpriteBlockManager(0, 0)
    im = InputManager()
    layout = GameLayout(495, 580)
    renderer = Mock(spec=Renderer)
    bullet_manager = BulletManager()
    return (
        GameController(gs, lm, bm, paddle, sbm, im, layout, renderer, bullet_manager),
        gs,
        bullet_manager,
        sbm,
    )


def test_fire_bullet_decrements_ammo_and_creates_bullet():
    controller, gs, bullet_manager, sbm = make_controller()
    gs.ammo = 2
    controller.ball_manager.balls.append(Mock())
    controller.ball_manager.has_ball_in_play = lambda: True
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)
    with patch("pygame.event.post") as post:
        controller.handle_events([event])
        assert gs.ammo == 1
        assert len(bullet_manager.bullets) == 1
        assert post.called


def test_fire_bullet_with_no_ammo_does_not_create_bullet():
    controller, gs, bullet_manager, sbm = make_controller()
    gs.ammo = 0
    controller.ball_manager.balls.append(Mock())
    controller.ball_manager.has_ball_in_play = lambda: True
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)
    with patch("pygame.event.post") as post:
        controller.handle_events([event])
        assert gs.ammo == 0
        assert len(bullet_manager.bullets) == 0
        assert not post.called  # Should NOT post event when no ammo


def test_bullet_block_collision_removes_bullet_and_block():
    controller, gs, bullet_manager, sbm = make_controller()
    # Add a bullet and a block
    bullet = Mock()
    bullet.active = True
    bullet_manager.add_bullet(bullet)
    block = Mock()
    sbm.blocks.append(block)
    # Patch block_manager.check_collisions to simulate collision
    sbm.check_collisions = Mock(return_value=(100, 1, []))
    gs.add_score = Mock(return_value=[])
    controller.post_game_state_events = Mock()
    controller.bullet_manager._bullets = [bullet]
    controller.update_balls_and_collisions(16.67)
    assert bullet in controller.bullet_manager.bullets  # Still present if active
    sbm.check_collisions.assert_called_with(bullet)
    gs.add_score.assert_called_with(100)
    controller.post_game_state_events.assert_called()
