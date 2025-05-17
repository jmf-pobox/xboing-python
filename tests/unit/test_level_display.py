import pygame

from engine.events import LevelChangedEvent
from ui.level_display import LevelDisplay


class MockDigitRenderer:
    def __init__(self):
        self.last_number = None
        self.last_kwargs = None
        self.surface = pygame.Surface((40, 20))

    def render_number(self, number, spacing=2, scale=1.0):
        self.last_number = number
        self.last_kwargs = dict(spacing=spacing, scale=scale)
        return self.surface


class DummyLayout:
    def get_score_rect(self):
        return pygame.Rect(0, 0, 200, 40)


def test_level_display_initial_state():
    layout = DummyLayout()
    digit_display = MockDigitRenderer()
    comp = LevelDisplay(layout, digit_display, x=10)
    assert comp.level == 1
    comp.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 1


def test_level_display_updates_on_event():
    layout = DummyLayout()
    digit_display = MockDigitRenderer()
    comp = LevelDisplay(layout, digit_display, x=10)

    # Create a pygame event with a LevelChangedEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": LevelChangedEvent(5)})
    comp.handle_events([event])

    assert comp.level == 5
    comp.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 5
