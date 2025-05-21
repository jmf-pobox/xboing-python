import pygame

from xboing.game.circular_game_shape import CircularGameShape


class DummyCircularShape(CircularGameShape):
    def __init__(self, x: float, y: float, radius: int):
        super().__init__(x, y, radius)
        self.draw_called = False

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_called = True
        # Draw a simple circle for test purposes
        pygame.draw.circle(
            surface, (0, 255, 0), (int(self.x), int(self.y)), self.radius
        )


def test_circular_gameshape_init_and_rect():
    shape = DummyCircularShape(10, 20, 15)
    assert shape.x == 10
    assert shape.y == 20
    assert shape.radius == 15
    assert shape.rect.x == (10 - 15)
    assert shape.rect.y == (20 - 15)
    assert shape.rect.width == 30
    assert shape.rect.height == 30


def test_circular_gameshape_update_rect():
    shape = DummyCircularShape(5, 6, 7)
    shape.x = 100
    shape.y = 200
    shape.radius = 10
    shape.update_rect()
    assert shape.rect.x == 90
    assert shape.rect.y == 190
    assert shape.rect.width == 20
    assert shape.rect.height == 20


def test_circular_gameshape_get_position():
    shape = DummyCircularShape(1, 2, 3)
    pos = shape.get_position()
    assert pos == (1, 2)


def test_circular_gameshape_draw_called():
    pygame.init()
    surface = pygame.Surface((50, 50))
    shape = DummyCircularShape(0, 0, 10)
    assert not shape.draw_called
    shape.draw(surface)
    assert shape.draw_called
    pygame.quit()
