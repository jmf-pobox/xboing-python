import pytest
from unittest.mock import patch, call
import pygame

from engine.events import (
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
    with patch('pygame.event.post') as mock_post:
        state = GameState()
        yield state, mock_post


def test_score_event(game_state):
    state, mock_post = game_state
    state.set_score(42)
    # Check that pygame.event.post was called with a pygame.event.Event containing a ScoreChangedEvent
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, ScoreChangedEvent)
    assert pygame_event.event.score == 42

    # Reset the mock and test add_score
    mock_post.reset_mock()
    state.add_score(8)
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, ScoreChangedEvent)
    assert pygame_event.event.score == 50


def test_lives_event(game_state):
    state, mock_post = game_state
    state.set_lives(5)
    # Check that pygame.event.post was called with a pygame.event.Event containing a LivesChangedEvent
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, LivesChangedEvent)
    assert pygame_event.event.lives == 5

    # Reset the mock and test lose_life
    mock_post.reset_mock()
    state.lose_life()
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, LivesChangedEvent)
    assert pygame_event.event.lives == 4


def test_level_event(game_state):
    state, mock_post = game_state
    state.set_level(3)
    # Check that pygame.event.post was called with a pygame.event.Event containing a LevelChangedEvent
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, LevelChangedEvent)
    assert pygame_event.event.level == 3


def test_timer_event(game_state):
    state, mock_post = game_state
    state.set_timer(99)
    # Check that pygame.event.post was called with a pygame.event.Event containing a TimerUpdatedEvent
    mock_post.assert_called()
    args, _ = mock_post.call_args
    pygame_event = args[0]
    assert pygame_event.type == pygame.USEREVENT
    assert isinstance(pygame_event.event, TimerUpdatedEvent)
    assert pygame_event.event.time_remaining == 99


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
        mock_post.reset_mock()
        state.set_special(name, True)
        mock_post.assert_called()
        args, _ = mock_post.call_args
        pygame_event = args[0]
        assert pygame_event.type == pygame.USEREVENT
        assert isinstance(pygame_event.event, event_cls)
        assert pygame_event.event.active is True

        # Test setting special to False
        mock_post.reset_mock()
        state.set_special(name, False)
        mock_post.assert_called()
        args, _ = mock_post.call_args
        pygame_event = args[0]
        assert pygame_event.type == pygame.USEREVENT
        assert isinstance(pygame_event.event, event_cls)
        assert pygame_event.event.active is False
