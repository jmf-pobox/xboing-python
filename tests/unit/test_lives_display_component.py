import pygame
from engine.events import LivesChangedEvent
from ui.lives_display import LivesDisplayComponent


class DummyEventBus:
    def __init__(self):
        self.subscriptions = {}
    def subscribe(self, event_type, handler):
        self.subscriptions[event_type] = handler
    def fire(self, event):
        handler = self.subscriptions.get(type(event))
        if handler:
            handler(event)

class MockLivesDisplayUtil:
    def __init__(self):
        self.last_lives = None
        self.last_kwargs = None
        self.surface = pygame.Surface((60, 20))
    def render(self, lives, spacing=10, scale=1.0, max_lives=3):
        self.last_lives = lives
        self.last_kwargs = dict(spacing=spacing, scale=scale, max_lives=max_lives)
        return self.surface

class DummyLayout:
    def get_score_rect(self):
        return pygame.Rect(0, 0, 200, 40)

def test_lives_display_initial_state():
    bus = DummyEventBus()
    layout = DummyLayout()
    util = MockLivesDisplayUtil()
    comp = LivesDisplayComponent(bus, layout, util, x=10, max_lives=3)
    assert comp.lives == 3
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 3
    assert util.last_kwargs is not None
    assert util.last_kwargs['max_lives'] == 3

def test_lives_display_loss():
    bus = DummyEventBus()
    layout = DummyLayout()
    util = MockLivesDisplayUtil()
    comp = LivesDisplayComponent(bus, layout, util, x=10, max_lives=3)
    bus.fire(LivesChangedEvent(2))
    assert comp.lives == 2
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 2
    assert util.last_kwargs is not None
    assert util.last_kwargs['max_lives'] == 3

def test_lives_display_gain():
    bus = DummyEventBus()
    layout = DummyLayout()
    util = MockLivesDisplayUtil()
    comp = LivesDisplayComponent(bus, layout, util, x=10, max_lives=3)
    bus.fire(LivesChangedEvent(2))
    assert comp.lives == 2
    bus.fire(LivesChangedEvent(3))
    assert comp.lives == 3
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_lives == 3
    assert util.last_kwargs is not None
    assert util.last_kwargs['max_lives'] == 3 