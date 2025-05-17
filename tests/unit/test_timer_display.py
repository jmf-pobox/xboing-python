import pygame
import pytest

from engine.events import TimerUpdatedEvent
from ui.timer_display import TimerDisplay


@pytest.fixture(autouse=True, scope="module")
def pygame_init_and_quit():
    pygame.init()
    yield
    pygame.quit()


class MockDigitRenderer:
    def __init__(self):
        self.last_time = None
        self.last_kwargs = None
        self.surface = pygame.Surface((80, 20))

    def render_time(self, seconds, spacing=2, scale=1.0, colon_width=8, color=None):
        self.last_time = seconds
        self.last_kwargs = dict(
            spacing=spacing, scale=scale, colon_width=colon_width, color=color
        )
        return self.surface


class DummyRenderer:
    def __init__(self):
        self.last_args = None

    def draw_text(self, text, font, color, x, y, centered=False):
        self.last_args = (text, font, color, x, y, centered)


class DummyLayout:
    class DummyTimeWindow:
        """Dummy time window for layout stub."""

        class DummyRect:
            """Dummy rect for layout stub."""

            rect = pygame.Rect(0, 0, 100, 30)

        rect = DummyRect()

    time_window = DummyTimeWindow()

    def get_timer_rect(self):
        return self.time_window.rect.rect


def test_timer_display_initial_state():
    layout = DummyLayout()  # type: ignore  # test stub, not a real GameLayout
    renderer = DummyRenderer()  # type: ignore  # test stub, not a real Renderer
    font = pygame.font.Font(None, 24)
    comp = TimerDisplay(layout, renderer, font)  # type: ignore
    assert comp.time_remaining == 0
    comp.draw(pygame.Surface((100, 30)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "00:00"


def test_timer_display_updates_on_event():
    layout = DummyLayout()  # type: ignore  # test stub, not a real GameLayout
    renderer = DummyRenderer()  # type: ignore  # test stub, not a real Renderer
    font = pygame.font.Font(None, 24)
    comp = TimerDisplay(layout, renderer, font)  # type: ignore
    # Create a pygame event with a TimerUpdatedEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": TimerUpdatedEvent(77)})
    comp.handle_events([event])
    assert comp.time_remaining == 77
    comp.draw(pygame.Surface((100, 30)))
    assert renderer.last_args is not None
    assert renderer.last_args[0] == "01:17"
