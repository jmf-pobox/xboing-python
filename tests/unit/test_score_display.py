import pygame
from engine.events import ScoreChangedEvent
from ui.score_display import ScoreDisplay


class DummyEventBus:
    def __init__(self):
        self.subscriptions = {}
    def subscribe(self, event_type, handler):
        self.subscriptions[event_type] = handler
    def fire(self, event):
        handler = self.subscriptions.get(type(event))
        if handler:
            handler(event)

class MockDigitDisplay:
    def __init__(self):
        self.last_number = None
        self.last_kwargs = None
        self.surface = pygame.Surface((120, 30))
    def render_number(self, number, spacing=2, scale=1.0, width=None, right_justified=False):
        self.last_number = number
        self.last_kwargs = dict(spacing=spacing, scale=scale, width=width, right_justified=right_justified)
        return self.surface

class DummyLayout:
    def get_score_rect(self):
        return pygame.Rect(0, 0, 200, 40)

def test_score_display_initial_state():
    bus = DummyEventBus()
    layout = DummyLayout()
    digit_display = MockDigitDisplay()
    score_display = ScoreDisplay(bus, layout, digit_display, x=10, width=6)
    assert score_display.score == 0
    # Should render with width=6, right_justified=True
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 0
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs['width'] == 6
    assert digit_display.last_kwargs['right_justified'] is True

def test_score_display_updates_on_event():
    bus = DummyEventBus()
    layout = DummyLayout()
    digit_display = MockDigitDisplay()
    score_display = ScoreDisplay(bus, layout, digit_display, x=10, width=6)
    # Fire a score change event
    bus.fire(ScoreChangedEvent(12345))
    assert score_display.score == 12345
    # Draw should use the updated score
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 12345
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs['width'] == 6
    assert digit_display.last_kwargs['right_justified'] is True

def test_score_display_right_justification():
    bus = DummyEventBus()
    layout = DummyLayout()
    digit_display = MockDigitDisplay()
    score_display = ScoreDisplay(bus, layout, digit_display, x=10, width=6)
    # Fire a score change event with a small number
    bus.fire(ScoreChangedEvent(7))
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 7
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs['width'] == 6
    assert digit_display.last_kwargs['right_justified'] is True
    # Fire a score change event with a large number
    bus.fire(ScoreChangedEvent(999999))
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 999999
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs['width'] == 6
    assert digit_display.last_kwargs['right_justified'] is True 