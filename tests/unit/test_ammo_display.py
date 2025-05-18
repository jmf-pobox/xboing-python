# tests/unit/test_ammo_display.py
import pygame

from engine.events import AmmoFiredEvent
from ui.ammo_display import AmmoDisplayComponent


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


def test_ammo_display_initial_state():
    layout = DummyLayout()  # type: ignore
    util = MockAmmoRenderer()  # type: ignore

    class DummyGameState:
        def get_ammo(self):
            return 4

    comp = AmmoDisplayComponent(layout, util, DummyGameState(), max_ammo=20)  # type: ignore
    assert comp.ammo == 4
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_ammo == 4
    assert util.last_kwargs is not None
    if util.last_kwargs is not None:
        assert util.last_kwargs["max_ammo"] == 20


def test_ammo_display_update_on_event():
    layout = DummyLayout()  # type: ignore
    util = MockAmmoRenderer()  # type: ignore

    class DummyGameState:
        def __init__(self):
            self._ammo = 4

        def get_ammo(self):
            return self._ammo

    gs = DummyGameState()
    comp = AmmoDisplayComponent(layout, util, gs, max_ammo=20)  # type: ignore
    gs._ammo = 3
    event = pygame.event.Event(pygame.USEREVENT, {"event": AmmoFiredEvent(3)})
    comp.handle_events([event])
    assert comp.ammo == 3
    comp.draw(pygame.Surface((200, 40)))
    assert util.last_ammo == 3
    assert util.last_kwargs is not None
    if util.last_kwargs is not None:
        assert util.last_kwargs["max_ammo"] == 20
