import pygame
import pytest
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

def test_game_view_draw():
    pygame.init()
    block_manager = MockBlockManager()
    paddle = MockPaddle()
    balls = [MockBall(), MockBall()]
    layout = MockLayout()
    renderer = MockRenderer()
    surface = pygame.Surface((100, 100))
    view = GameView(layout, block_manager, paddle, balls, renderer)
    view.draw(surface)
    assert block_manager.drawn
    assert paddle.drawn
    assert all(ball.drawn for ball in balls)
    pygame.quit() 