from unittest.mock import patch

import pygame
import pytest
from engine.events import (
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
    # Test set_score returns correct event
    changes = state.set_score(42)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, ScoreChangedEvent)
    assert event.score == 42

    # Test add_score returns correct event
    changes = state.add_score(8)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, ScoreChangedEvent)
    assert event.score == 50


def test_lives_event(game_state):
    state, mock_post = game_state
    # Test set_lives returns correct event
    changes = state.set_lives(5)
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, LivesChangedEvent)
    assert event.lives == 5

    # Test lose_life returns correct event (should decrement to 4)
    changes = state.lose_life()
    assert len(changes) == 1
    event = changes[0]
    assert isinstance(event, LivesChangedEvent)
    assert event.lives == 4


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
