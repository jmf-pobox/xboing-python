from unittest.mock import patch

import pygame
import pytest

from engine.events import (
    AmmoFiredEvent,
    GameOverEvent,
    LevelChangedEvent,
    LivesChangedEvent,
    ScoreChangedEvent,
    SpecialFastGunChangedEvent,
    SpecialKillerChangedEvent,
    SpecialNoWallChangedEvent,
    SpecialReverseChangedEvent,
    SpecialSaveChangedEvent,
    SpecialStickyChangedEvent,
    SpecialX2ChangedEvent,
    SpecialX4ChangedEvent,
    TimerUpdatedEvent,
)
from game.game_state import GameState


@pytest.fixture
def game_state():
    pygame.init()  # Initialize pygame for events
    with patch("pygame.event.post") as mock_post:
        state = GameState()
        yield state, mock_post


def test_score_event(game_state):
    state, mock_post = game_state
    # Test _set_score returns correct event (private method, used for resets)
    changes = state._set_score(42)
    assert len(changes) == 1
    assert isinstance(changes[0], ScoreChangedEvent)
    assert changes[0].score == 42


def test_lives_event(game_state):
    state, mock_post = game_state
    # Test _set_lives returns correct event (private method, used for resets)
    changes = state._set_lives(5)
    assert len(changes) == 1
    assert isinstance(changes[0], LivesChangedEvent)
    assert changes[0].lives == 5


def test_level_event(game_state):
    state, mock_post = game_state
    # Test set_level returns correct event
    changes = state.set_level(3)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, LevelChangedEvent)
    assert event.level == 3


def test_timer_event(game_state):
    state, mock_post = game_state
    # Test set_timer returns correct event
    changes = state.set_timer(99)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, TimerUpdatedEvent)
    assert event.time_remaining == 99


def test_special_events(game_state):
    state, mock_post = game_state
    specials = [
        ("reverse", SpecialReverseChangedEvent),
        ("sticky", SpecialStickyChangedEvent),
        ("save", SpecialSaveChangedEvent),
        ("fastgun", SpecialFastGunChangedEvent),
        ("nowall", SpecialNoWallChangedEvent),
        ("killer", SpecialKillerChangedEvent),
        ("x2", SpecialX2ChangedEvent),
        ("x4", SpecialX4ChangedEvent),
    ]
    for name, event_cls in specials:
        # Test setting special to True
        changes = state.set_special(name, True)
        assert len(changes) == 1
        event = changes[0]
        assert isinstance(event, event_cls)
        assert event.active is True

        # Test setting special to False
        changes = state.set_special(name, False)
        assert len(changes) == 1
        event = changes[0]
        assert isinstance(event, event_cls)
        assert event.active is False


def test_game_over_event(game_state):
    state, mock_post = game_state
    # Should return GameOverEvent when setting to True
    changes = state.set_game_over(True)
    if not changes:
        # If already True, set to False and try again
        state.set_game_over(False)
        changes = state.set_game_over(True)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, GameOverEvent)
    # Should return empty list if setting to False or no change
    changes = state.set_game_over(False)
    assert changes == []


def test_ammo_initial_and_fire(game_state):
    state, _ = game_state
    # Initial ammo should be 4
    assert state.ammo == 4
    # Firing ammo decrements and emits event
    changes = state.fire_ammo()
    assert state.ammo == 3
    assert len(changes) == 1
    assert isinstance(changes[0], AmmoFiredEvent)
    assert changes[0].ammo == 3
    # Firing until empty
    state.ammo = 1
    changes = state.fire_ammo()
    assert state.ammo == 0
    assert len(changes) == 1
    changes = state.fire_ammo()
    assert state.ammo == 0
    assert changes == []


class DummyLevelManager:
    def load_level(self, level): pass
    def get_time_remaining(self): return 60
    def get_level_info(self): return {"title": "Test Level"}


def test_ammo_reset_on_restart(game_state):
    state, _ = game_state
    state.ammo = 0
    dummy_level_manager = DummyLevelManager()
    state.full_restart(dummy_level_manager)
    assert state.ammo == 4


def test_ammo_reset_on_full_restart(game_state):
    state, _ = game_state
    state.ammo = 0

    class DummyLevelManager:
        def get_time_remaining(self):
            return 0

        def get_level_info(self):
            return {"title": "foo"}

        def load_level(self, lvl):
            pass

    state.full_restart(DummyLevelManager())
    assert state.ammo == 4
