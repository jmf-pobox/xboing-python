import pygame

from xboing.engine.events import LivesChangedEvent
from xboing.ui.lives_display import LivesDisplayComponent


class MockLivesRendererUtil:
    def __init__(self):
        self.last_lives = None
        self.last_kwargs = None
        self.surface = pygame.Surface((60, 20))

    def render(self, lives, spacing=10, scale=1.0, max_lives=3):
        self.last_lives = lives
        self.last_kwargs = dict(spacing=spacing, scale=scale, max_lives=max_lives)
        return self.surface


class MockAmmoRenderer:
    def __init__(self):
        self.last_ammo = None
        self.last_kwargs = None
        self.surface = pygame.Surface((60, 20))

    def render(self, ammo, spacing=1, max_ammo=20):
        self.last_ammo = ammo
        self.last_kwargs = dict(spacing=spacing, max_ammo=max_ammo)
        return self.surface


class DummyLayout:
    def get_score_rect(self):
        return pygame.Rect(0, 0, 200, 40)


def test_lives_display_initial_state():
    layout = DummyLayout()  # type: ignore
    util = MockLivesRendererUtil()  # type: ignore
    comp = LivesDisplayComponent(layout, util, x=10, max_lives=3)  # type: ignore
    assert comp.lives == 3
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 3
    assert util.last_kwargs is not None
    assert util.last_kwargs["max_lives"] == 3


def test_lives_display_loss():
    layout = DummyLayout()  # type: ignore
    util = MockLivesRendererUtil()  # type: ignore
    comp = LivesDisplayComponent(layout, util, x=10, max_lives=3)  # type: ignore

    # Create a pygame event with a LivesChangedEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": LivesChangedEvent(2)})
    comp.handle_events([event])

    assert comp.lives == 2
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 2
    assert util.last_kwargs is not None
    assert util.last_kwargs["max_lives"] == 3


def test_lives_display_gain():
    layout = DummyLayout()  # type: ignore
    util = MockLivesRendererUtil()  # type: ignore
    comp = LivesDisplayComponent(layout, util, x=10, max_lives=3)  # type: ignore

    # Create a pygame event with a LivesChangedEvent for loss
    event_loss = pygame.event.Event(pygame.USEREVENT, {"event": LivesChangedEvent(2)})
    comp.handle_events([event_loss])
    assert comp.lives == 2

    # Create a pygame event with a LivesChangedEvent for gain
    event_gain = pygame.event.Event(pygame.USEREVENT, {"event": LivesChangedEvent(3)})
    comp.handle_events([event_gain])
    assert comp.lives == 3

    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 3
    assert util.last_kwargs is not None
    assert util.last_kwargs["max_lives"] == 3
