import pytest
from game.game_state import GameState
from engine.events import (
    ScoreChangedEvent, LivesChangedEvent, LevelChangedEvent, TimerUpdatedEvent,
    SpecialReverseChangedEvent, SpecialStickyChangedEvent, SpecialSaveChangedEvent,
    SpecialFastGunChangedEvent, SpecialNoWallChangedEvent, SpecialKillerChangedEvent,
    SpecialX2ChangedEvent, SpecialX4ChangedEvent
)

class MockEventBus:
    def __init__(self):
        self.fired = []
    def fire(self, event):
        self.fired.append(event)

@pytest.fixture
def game_state():
    bus = MockEventBus()
    state = GameState(bus)
    return state, bus

def test_score_event(game_state):
    state, bus = game_state
    state.set_score(42)
    assert isinstance(bus.fired[-1], ScoreChangedEvent)
    assert bus.fired[-1].score == 42
    state.add_score(8)
    assert isinstance(bus.fired[-1], ScoreChangedEvent)
    assert bus.fired[-1].score == 50

def test_lives_event(game_state):
    state, bus = game_state
    state.set_lives(5)
    assert isinstance(bus.fired[-1], LivesChangedEvent)
    assert bus.fired[-1].lives == 5
    state.lose_life()
    assert isinstance(bus.fired[-1], LivesChangedEvent)
    assert bus.fired[-1].lives == 4

def test_level_event(game_state):
    state, bus = game_state
    state.set_level(3)
    assert isinstance(bus.fired[-1], LevelChangedEvent)
    assert bus.fired[-1].level == 3

def test_timer_event(game_state):
    state, bus = game_state
    state.set_timer(99)
    assert isinstance(bus.fired[-1], TimerUpdatedEvent)
    assert bus.fired[-1].time_remaining == 99

def test_special_events(game_state):
    state, bus = game_state
    specials = [
        ('reverse', SpecialReverseChangedEvent),
        ('sticky', SpecialStickyChangedEvent),
        ('save', SpecialSaveChangedEvent),
        ('fastgun', SpecialFastGunChangedEvent),
        ('nowall', SpecialNoWallChangedEvent),
        ('killer', SpecialKillerChangedEvent),
        ('x2', SpecialX2ChangedEvent),
        ('x4', SpecialX4ChangedEvent),
    ]
    for name, event_cls in specials:
        state.set_special(name, True)
        assert isinstance(bus.fired[-1], event_cls)
        assert bus.fired[-1].active is True
        state.set_special(name, False)
        assert isinstance(bus.fired[-1], event_cls)
        assert bus.fired[-1].active is False 