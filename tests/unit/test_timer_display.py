import pytest
import pygame
from pygame.font import Font
from ui.timer_display import TimerDisplay
from engine.events import TimerUpdatedEvent

@pytest.fixture(autouse=True, scope="module")
def pygame_init_and_quit():
    pygame.init()
    yield
    pygame.quit()

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
        self.last_time = None
        self.last_kwargs = None
        self.surface = pygame.Surface((80, 20))
    def render_time(self, seconds, spacing=2, scale=1.0, colon_width=8, color=None):
        self.last_time = seconds
        self.last_kwargs = dict(spacing=spacing, scale=scale, colon_width=colon_width, color=color)
        return self.surface

class DummyRenderer:
    def __init__(self):
        self.last_args = None
    def draw_text(self, text, font, color, x, y, centered=False):
        self.last_args = (text, font, color, x, y, centered)

class DummyLayout:
    class DummyTimeWindow:
        class DummyRect:
            rect = pygame.Rect(0, 0, 100, 30)
        rect = DummyRect()
    time_window = DummyTimeWindow()

def test_timer_display_initial_state():
    bus = DummyEventBus()
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = TimerDisplay(bus, layout, renderer, font)
    assert comp.time_remaining == 0
    comp.draw(pygame.Surface((100, 30)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "00:00"

def test_timer_display_updates_on_event():
    bus = DummyEventBus()
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = TimerDisplay(bus, layout, renderer, font)
    bus.fire(TimerUpdatedEvent(77))
    assert comp.time_remaining == 77
    comp.draw(pygame.Surface((100, 30)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "01:17" 