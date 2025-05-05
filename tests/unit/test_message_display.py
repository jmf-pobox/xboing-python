import pygame
import pytest
from engine.events import MessageChangedEvent
from ui.message_display import MessageDisplay


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

class DummyRenderer:
    def __init__(self):
        self.last_args = None
    def draw_text(self, text, font, color, x, y, centered=False):
        self.last_args = (text, font, color, x, y, centered)

class DummyLayout:
    def get_message_rect(self):
        return pygame.Rect(0, 0, 200, 40)

def test_message_display_initial_state():
    bus = DummyEventBus()
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = MessageDisplay(bus, layout, renderer, font)
    assert comp.message == ""
    assert comp.alignment == 'left'
    comp.draw(pygame.Surface((200, 40)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == ""
    assert renderer.last_args[2] == (0, 255, 0)

def test_message_display_updates_on_event():
    bus = DummyEventBus()
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = MessageDisplay(bus, layout, renderer, font)
    bus.fire(MessageChangedEvent("Hello World", alignment='center'))
    assert comp.message == "Hello World"
    assert comp.alignment == 'center'
    comp.draw(pygame.Surface((200, 40)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "Hello World"
    assert renderer.last_args[2] == (0, 255, 0) 