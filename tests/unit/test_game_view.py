import pygame
import pytest

from game.ball_manager import BallManager
from game.bullet_manager import BulletManager
from renderers.bullet_renderer import BulletRenderer
from ui.game_view import GameView


class MockBlockManager:
    def __init__(self):
        self.drawn = False

    def draw(self, surface):
        self.drawn = True


class MockPaddle:
    def __init__(self):
        self.drawn = False

    def draw(self, surface):
        self.drawn = True


class MockBall:
    def __init__(self):
        self.drawn = False

    def draw(self, surface):
        self.drawn = True


class MockLayout:
    def get_play_rect(self):
        class R:
            x, y, width, height = 0, 0, 100, 100

        return R()


class MockRenderer:
    pass


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    pygame.display.set_mode((1, 1))  # Dummy video mode for image loading
    yield
    pygame.quit()


def test_game_view_draw():
    block_manager = MockBlockManager()  # type: ignore  # test mock
    paddle = MockPaddle()  # type: ignore  # test mock
    balls = [MockBall(), MockBall()]  # type: ignore  # test mock
    ball_manager = BallManager()
    for b in balls:
        ball_manager.add_ball(b)  # type: ignore  # test mock
    layout = MockLayout()  # type: ignore  # test mock
    renderer = MockRenderer()  # type: ignore  # test mock
    bullet_manager = BulletManager()
    bullet_renderer = BulletRenderer()
    surface = pygame.Surface((100, 100))
    view = GameView(layout, block_manager, paddle, ball_manager, renderer, bullet_manager, bullet_renderer)  # type: ignore  # test mock
    view.draw(surface)
    assert block_manager.drawn
    assert paddle.drawn
    assert all(getattr(ball, "drawn", False) for ball in ball_manager.balls)  # type: ignore  # test mock
