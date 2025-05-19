import pygame
import pytest

from xboing.game.ball import Ball


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


def test_ball_creation():
    b = Ball(10, 20, radius=5, color=(1, 2, 3))
    assert b.x == 10
    assert b.y == 20
    assert b.radius == 5
    assert b.color == (1, 2, 3)
    assert b.active is True
    assert b.stuck_to_paddle is False


def test_ball_update_moves_and_wall_collision():
    b = Ball(50, 50, radius=5)
    b.vx = 10
    b.vy = 0
    # Move right, should bounce off right wall
    b.update(16.67, 60, 60)
    assert b.x <= 60 - b.radius
    b.x = 5
    b.vx = -10
    b.update(16.67, 60, 60)
    assert b.x >= b.radius
    # Move up, should bounce off top
    b.y = 5
    b.vy = -10
    b.update(16.67, 60, 60)
    assert b.y >= b.radius
    # Move down, should deactivate if below bottom
    b.y = 70
    b.vy = 10
    b.update(16.67, 60, 60)
    assert not b.active


def test_ball_stuck_to_paddle_logic():
    class DummyPaddle:
        rect = pygame.Rect(30, 40, 20, 10)

        def is_sticky(self):
            return False

    b = Ball(35, 30, radius=5)
    b.stuck_to_paddle = True
    b.paddle_offset = 0
    b.update(16.67, 100, 100, paddle=DummyPaddle())
    assert b.x == DummyPaddle.rect.centerx
    assert b.y == DummyPaddle.rect.top - b.radius - 1


def test_ball_check_paddle_collision():
    class DummyPaddle:
        rect = pygame.Rect(30, 40, 20, 10)

        def is_sticky(self):
            return False

    b = Ball(40, 49, radius=5)
    b.vy = 10
    collided = b._check_paddle_collision(DummyPaddle())
    assert collided
    # Should bounce upward
    assert b.vy < 0


def test_ball_release_from_paddle():
    b = Ball(10, 10)
    b.stuck_to_paddle = True
    b.release_from_paddle()
    assert not b.stuck_to_paddle


def test_ball_set_position_and_velocity():
    b = Ball(0, 0)
    b.set_position(5, 6)
    assert b.x == 5
    assert b.y == 6
    b.set_velocity(3, 4)
    assert b.vx == 3
    assert b.vy == 4


def test_ball_is_active():
    b = Ball(0, 0)
    assert b.is_active() is True
    b.active = False
    assert b.is_active() is False


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
    b = Ball(10, 10)
    old_vx, old_vy = b.vx, b.vy
    b._add_random_factor()
    # Should change at least one component
    assert (b.vx != old_vx) or (b.vy != old_vy)


def test_ball_get_rect_and_position():
    b = Ball(15, 25, radius=4)
    rect = b.get_rect()
    assert rect.x == 11 and rect.y == 21 and rect.width == 8 and rect.height == 8
    pos = b.get_position()
    assert pos == (15, 25)


def test_ball_update_inactive():
    b = Ball(10, 10)
    b.active = False
    result = b.update(16.67, 100, 100)
    assert result == (False, False, False)
