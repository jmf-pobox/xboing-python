import pygame
import pytest

from xboing.engine.events import BallLostEvent, PaddleHitEvent, WallHitEvent
from xboing.game.ball import Ball
from xboing.game.circular_game_shape import CircularGameShape
from xboing.game.protocols import (
    Activatable,
    Collidable,
    Drawable,
    GameObject,
    Positionable,
    Updateable,
)


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_ball_inheritance_and_protocols():
    """Test that Ball inherits from CircularGameShape and implements all required protocols."""
    b = Ball(10, 20)
    # Test inheritance
    assert isinstance(b, CircularGameShape)
    # Test protocol implementation
    assert isinstance(b, Updateable)
    assert isinstance(b, Drawable)
    assert isinstance(b, Collidable)
    assert isinstance(b, Positionable)
    assert isinstance(b, Activatable)
    assert isinstance(b, GameObject)


def test_ball_creation():
    """Test that Ball initializes correctly."""
    b = Ball(10, 20, radius=5, color=(1, 2, 3))
    assert b.x == 10
    assert b.y == 20
    assert b.radius == 5
    assert b.color == (1, 2, 3)
    assert b.active is True
    assert b.stuck_to_paddle is False
    # Test physics component initialization
    assert hasattr(b, "physics")
    assert b.physics.get_position() == (10, 20)


def test_ball_update_moves_and_wall_collision():
    """Test that Ball moves and collides with walls correctly, generating appropriate events."""
    # Position the ball very close to the right wall
    b = Ball(58, 50, radius=5)
    b.set_velocity(100, 0)  # Use a high velocity to ensure wall collision

    # Move right, should bounce off right wall and generate WallHitEvent
    events = b.update(16.67, 60, 60)
    assert b.x <= 60 - b.radius
    assert any(isinstance(e, WallHitEvent) for e in events)

    # Reset position and move left, should bounce off left wall and generate WallHitEvent
    b.set_position(4, 30)
    b.set_velocity(-10, 0)
    events = b.update(16.67, 60, 60)
    assert b.x >= b.radius
    assert any(isinstance(e, WallHitEvent) for e in events)

    # Reset position and move up, should bounce off top wall and generate WallHitEvent
    b.set_position(30, 4)
    b.set_velocity(0, -10)
    events = b.update(16.67, 60, 60)
    assert b.y >= b.radius
    assert any(isinstance(e, WallHitEvent) for e in events)

    # Reset position and move down, should deactivate if below bottom and generate BallLostEvent
    b.set_position(30, 70)
    b.set_velocity(0, 10)
    events = b.update(16.67, 60, 60)
    assert not b.active
    assert any(isinstance(e, BallLostEvent) for e in events)


def test_ball_stuck_to_paddle_logic():
    """Test that Ball sticks to paddle correctly."""

    class DummyPaddle:
        rect = pygame.Rect(30, 40, 20, 10)

        def is_sticky(self):
            return False

    b = Ball(35, 30, radius=5)
    b.stuck_to_paddle = True
    b.paddle_offset = 0
    events = b.update(16.67, 100, 100, paddle=DummyPaddle())
    assert b.x == DummyPaddle.rect.centerx
    assert b.y == DummyPaddle.rect.top - b.radius - 1
    # Should not generate any events while stuck to paddle
    assert len(events) == 0
    # Physics component position should be updated
    assert b.physics.get_position() == (b.x, b.y)


def test_ball_check_paddle_collision():
    """Test that Ball collides with paddle correctly and generates PaddleHitEvent."""

    class DummyPaddle:
        rect = pygame.Rect(30, 40, 20, 10)

        def is_sticky(self):
            return False

    b = Ball(40, 49, radius=5)
    b.physics.set_velocity((0, 10))  # Moving downward
    collided = b._check_paddle_collision(DummyPaddle())
    assert collided
    # Should bounce upward
    _vx, vy = b.physics.get_velocity()
    assert vy < 0

    # Test that update generates PaddleHitEvent
    b = Ball(40, 39, radius=5)
    b.physics.set_velocity((0, 10))  # Moving downward
    events = b.update(16.67, 100, 100, paddle=DummyPaddle())
    assert any(isinstance(e, PaddleHitEvent) for e in events)


def test_ball_release_from_paddle():
    """Test that Ball releases from paddle correctly."""
    b = Ball(10, 10)
    b.stuck_to_paddle = True
    b.release_from_paddle()
    assert not b.stuck_to_paddle
    # Velocity should be set based on guide position
    vx, vy = b.physics.get_velocity()
    assert vx != 0 or vy != 0


def test_ball_set_position_and_velocity():
    """Test that Ball position and velocity can be set correctly."""
    b = Ball(0, 0)
    b.set_position(5, 6)
    assert b.x == 5
    assert b.y == 6
    assert b.physics.get_position() == (5, 6)

    b.set_velocity(3, 4)
    vx, vy = b.physics.get_velocity()
    assert vx == 3
    assert vy == 4


def test_ball_is_active_and_set_active():
    """Test that Ball active state can be checked and set correctly."""
    b = Ball(0, 0)
    assert b.is_active() is True

    # Test set_active method
    b.set_active(False)
    assert b.is_active() is False
    assert b.active is False

    b.set_active(True)
    assert b.is_active() is True
    assert b.active is True


def test_ball_draw_fallback(monkeypatch):
    b = Ball(10, 10)
    # Force sprites to None to test fallback
    monkeypatch.setattr(type(b), "sprites", None)
    surface = pygame.Surface((20, 20))
    b.draw(surface)  # Should not raise


def test_ball_draw_with_sprite(monkeypatch):
    b = Ball(10, 10)
    # Patch sprites to a list with a dummy surface
    dummy_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    monkeypatch.setattr(type(b), "sprites", [dummy_surface])
    b.sprite_index = 0
    surface = pygame.Surface((20, 20))
    b.draw(surface)  # Should not raise


def test_ball_draw_with_birth_animation(monkeypatch):
    b = Ball(10, 10)
    b.birth_animation = True
    b.animation_frame = 0
    dummy_anim1 = pygame.Surface((10, 10), pygame.SRCALPHA)
    dummy_anim2 = pygame.Surface((10, 10), pygame.SRCALPHA)
    monkeypatch.setattr(type(b), "animation_frames", [dummy_anim1, dummy_anim2])
    surface = pygame.Surface((20, 20))
    # Call draw 5 times to advance the animation frame
    for _ in range(5):
        b.draw(surface)
    assert b.animation_frame >= 1


def test_ball_add_random_factor_changes_velocity():
    """Test that _add_random_factor changes the velocity."""
    b = Ball(10, 10)
    old_vx, old_vy = b.physics.get_velocity()
    b._add_random_factor()
    # Should change at least one component
    new_vx, new_vy = b.physics.get_velocity()
    assert (new_vx != old_vx) or (new_vy != old_vy)


def test_ball_get_rect_and_position():
    b = Ball(15, 25, radius=4)
    rect = b.get_rect()
    assert rect.x == 11 and rect.y == 21 and rect.width == 8 and rect.height == 8
    pos = b.get_position()
    assert pos == (15, 25)


def test_ball_update_inactive():
    """Test that update returns empty events list when ball is inactive."""
    b = Ball(10, 10)
    b.set_active(False)
    events = b.update(16.67, 100, 100)
    assert events == []  # Should return empty list when inactive


def test_ball_collides_with():
    """Test that collides_with method works correctly."""
    b = Ball(10, 10, radius=5)

    # Create a collidable object that collides with the ball
    class MockCollidable:
        def get_rect(self):
            return pygame.Rect(8, 8, 5, 5)

    # Create a collidable object that doesn't collide with the ball
    class MockNonCollidable:
        def get_rect(self):
            return pygame.Rect(20, 20, 5, 5)

    # Test collision
    assert b.collides_with(MockCollidable())

    # Test no collision
    assert not b.collides_with(MockNonCollidable())
