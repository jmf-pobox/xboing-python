import pygame
import pytest
from engine.events import MessageChangedEvent
from ui.message_display import MessageDisplay


@pytest.fixture(autouse=True, scope="module")
def pygame_init_and_quit():
    pygame.init()
    yield
    pygame.quit()


class DummyRenderer:
    def __init__(self):
        self.last_args = None

    def draw_text(self, text, font, color, x, y, centered=False):
        self.last_args = (text, font, color, x, y, centered)


class DummyLayout:
    def get_message_rect(self):
        return pygame.Rect(0, 0, 200, 40)


def test_message_display_initial_state():
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = MessageDisplay(layout, renderer, font)
    assert comp.message == ""
    assert comp.alignment == "left"
    comp.draw(pygame.Surface((200, 40)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == ""
    assert renderer.last_args[2] == (0, 255, 0)


def test_message_display_updates_on_event():
    layout = DummyLayout()
    renderer = DummyRenderer()
    font = pygame.font.Font(None, 24)
    comp = MessageDisplay(layout, renderer, font)

    # Create a pygame event with a MessageChangedEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": MessageChangedEvent("Hello World", alignment="center")})
    comp.handle_events([event])

    assert comp.message == "Hello World"
    assert comp.alignment == "center"
    comp.draw(pygame.Surface((200, 40)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "Hello World"
    assert renderer.last_args[2] == (0, 255, 0)
