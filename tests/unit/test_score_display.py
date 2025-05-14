import pygame
from engine.events import ScoreChangedEvent
from ui.score_display import ScoreDisplay


class MockDigitRenderer:
    def __init__(self):
        self.last_number = None
        self.last_kwargs = None
        self.surface = pygame.Surface((120, 30))

    def render_number(
        self, number, spacing=2, scale=1.0, width=None, right_justified=False
    ):
        self.last_number = number
        self.last_kwargs = dict(
            spacing=spacing, scale=scale, width=width, right_justified=right_justified
        )
        return self.surface


class DummyLayout:
    def get_score_rect(self):
        return pygame.Rect(0, 0, 200, 40)


def test_score_display_initial_state():
    layout = DummyLayout()
    digit_display = MockDigitRenderer()
    score_display = ScoreDisplay(layout, digit_display, x=10, width=6)
    assert score_display.score == 0
    # Should render with width=6, right_justified=True
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 0
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs["width"] == 6
    assert digit_display.last_kwargs["right_justified"] is True


def test_score_display_updates_on_event():
    layout = DummyLayout()
    digit_display = MockDigitRenderer()
    score_display = ScoreDisplay(layout, digit_display, x=10, width=6)

    # Create a pygame event with a ScoreChangedEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(12345)})
    score_display.handle_events([event])

    assert score_display.score == 12345
    # Draw should use the updated score
    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 12345
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs["width"] == 6
    assert digit_display.last_kwargs["right_justified"] is True


def test_score_display_right_justification():
    layout = DummyLayout()
    digit_display = MockDigitRenderer()
    score_display = ScoreDisplay(layout, digit_display, x=10, width=6)

    # Create a pygame event with a ScoreChangedEvent for a small number
    event_small = pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(7)})
    score_display.handle_events([event_small])

    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 7
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs["width"] == 6
    assert digit_display.last_kwargs["right_justified"] is True

    # Create a pygame event with a ScoreChangedEvent for a large number
    event_large = pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(999999)})
    score_display.handle_events([event_large])

    score_display.draw(pygame.Surface((200, 40)))
    assert digit_display.last_number == 999999
    assert digit_display.last_kwargs is not None
    assert digit_display.last_kwargs["width"] == 6
    assert digit_display.last_kwargs["right_justified"] is True
