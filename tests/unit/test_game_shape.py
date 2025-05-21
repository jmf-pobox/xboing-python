import pygame

from xboing.game.game_shape import GameShape


class DummyShape(GameShape):
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__(x, y, width, height)
        self.draw_called = False

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_called = True
        # Draw a simple rect for test purposes
        pygame.draw.rect(surface, (255, 0, 0), self.rect)


def test_gameshape_init_and_rect():
    shape = DummyShape(10, 20, 30, 40)
    assert shape.x == 10
    assert shape.y == 20
    assert shape.rect.x == 10
    assert shape.rect.y == 20
    assert shape.rect.width == 30
    assert shape.rect.height == 40


def test_gameshape_update_rect():
    shape = DummyShape(5, 6, 7, 8)
    shape.x = 100
    shape.y = 200
    shape.update_rect()
    assert shape.rect.x == 100
    assert shape.rect.y == 200


def test_gameshape_get_rect_and_position():
    shape = DummyShape(1, 2, 3, 4)
    rect = shape.get_rect()
    pos = shape.get_position()
    assert rect.x == 1 and rect.y == 2 and rect.width == 3 and rect.height == 4
    assert pos == (1, 2)


def test_gameshape_draw_called():
    pygame.init()
    surface = pygame.Surface((50, 50))
    shape = DummyShape(0, 0, 10, 10)
    assert not shape.draw_called
    shape.draw(surface)
    assert shape.draw_called
    pygame.quit()
