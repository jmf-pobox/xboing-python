import pygame
import pytest

from xboing.game.bullet import Bullet


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def test_bullet_creation():
    b = Bullet(10, 20, vx=2, vy=-5, radius=4, color=(1, 2, 3))
    assert b.x == 10
    assert b.y == 20
    assert b.vx == 2
    assert b.vy == -5
    assert b.radius == 4
    assert b.color == (1, 2, 3)
    assert b.active is True


def test_bullet_update_moves_and_deactivates():
    b = Bullet(10, 10, vy=-10)
    b.update(16.67)  # 1 frame at 60fps
    assert b.y < 10
    # Set the position in the physics component
    b.physics.set_position((b.x, -10))
    b.update(16.67)
    assert not b.active


def test_bullet_get_rect():
    b = Bullet(50, 60, radius=5)
    rect = b.get_rect()
    assert rect.x == 45
    assert rect.y == 55
    assert rect.width == 10
    assert rect.height == 10


def test_bullet_is_active_in_bounds():
    b = Bullet(100, 100)
    assert b.is_active() is True


def test_bullet_is_active_out_of_bounds():
    b = Bullet(-10, 100)
    assert not b.is_active()
    b = Bullet(100, 650)
    assert not b.is_active()


def test_bullet_draw_smoke():
    b = Bullet(10, 10)
    surface = pygame.Surface((20, 20))
    b.draw(surface)  # Should not raise
