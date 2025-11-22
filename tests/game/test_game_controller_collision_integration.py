"""Integration tests for GameController and CollisionSystem."""

from typing import List

import pytest

from xboing.game.ball import Ball
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet import Bullet
from xboing.game.bullet_manager import BulletManager
from xboing.game.collision import CollisionSystem, CollisionType
from xboing.game.paddle import Paddle


class DummyGameController:
    """Minimal stub for GameController to test collision integration."""

    def __init__(self) -> None:
        self.collision_system = CollisionSystem()
        self.ball_manager = BallManager()
        self.bullet_manager = BulletManager()
        self.block_manager = BlockManager()
        self.paddle = Paddle(100, 400)
        self.events: List[str] = []

    def register_handlers(self) -> None:
        self.collision_system.register_collision_handler(
            CollisionType.BALL.value,
            CollisionType.BLOCK.value,
            lambda ball, block: self.events.append("ball-block"),
        )
        self.collision_system.register_collision_handler(
            CollisionType.BALL.value,
            CollisionType.PADDLE.value,
            lambda ball, paddle: self.events.append("ball-paddle"),
        )
        self.collision_system.register_collision_handler(
            CollisionType.BULLET.value,
            CollisionType.BLOCK.value,
            lambda bullet, block: self.events.append("bullet-block"),
        )
        self.collision_system.register_collision_handler(
            CollisionType.BULLET.value,
            CollisionType.BALL.value,
            lambda bullet, ball: self.events.append("bullet-ball"),
        )

    def setup_collidables(self) -> None:
        # Place all objects so they overlap
        ball = Ball(120, 120, 10, (255, 255, 255))
        bullet = Bullet(120, 120, vy=-5, radius=5)
        block = self.block_manager.create_block(110, 110, 30, 30, block_type="normal")
        self.ball_manager.add_ball(ball)
        self.bullet_manager.add_bullet(bullet)
        self.block_manager.blocks = [block]
        self.collision_system.add_collidable(ball)
        self.collision_system.add_collidable(bullet)
        self.collision_system.add_collidable(block)
        self.collision_system.add_collidable(self.paddle)


@pytest.fixture
def dummy_controller() -> DummyGameController:
    controller = DummyGameController()
    controller.register_handlers()
    controller.setup_collidables()
    return controller


def test_collision_handlers_are_called(dummy_controller: DummyGameController) -> None:
    """Test that collision handlers are called for overlapping objects."""
    dummy_controller.collision_system.check_collisions()
    # Should detect ball-block, bullet-block, bullet-ball, and ball-paddle (if overlapping)
    assert "ball-block" in dummy_controller.events
    assert "bullet-block" in dummy_controller.events
    assert "bullet-ball" in dummy_controller.events
    # Ball and paddle may not overlap in this setup, so don't require it
